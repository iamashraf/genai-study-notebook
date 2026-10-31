"""IVF from scratch: recall vs. clusters searched. Synthetic data, fixed seed, numpy only."""
import time
import numpy as np

rng = np.random.default_rng(0)
N, D, BLOBS, NLIST, NQ, K = 100_000, 64, 200, 256, 200, 10

# Synthetic data: 100,000 vectors drawn from 200 Gaussian blobs.
centers = rng.normal(0, 1, (BLOBS, D)).astype(np.float32)
db = centers[rng.integers(0, BLOBS, N)] + rng.normal(0, 0.5, (N, D)).astype(np.float32)
queries = centers[rng.integers(0, BLOBS, NQ)] + rng.normal(0, 0.5, (NQ, D)).astype(np.float32)


def sqdist(a, b):
    """Squared Euclidean distance between every row of a and every row of b."""
    return (a**2).sum(1)[:, None] - 2 * a @ b.T + (b**2).sum(1)[None, :]


def assign(x, cents, chunk=10_000):
    return np.concatenate([sqdist(x[i:i + chunk], cents).argmin(1) for i in range(0, len(x), chunk)])


# k-means, 10 iterations, 256 clusters, started from random database vectors.
cents = db[rng.choice(N, NLIST, replace=False)].copy()
for _ in range(10):
    labels = assign(db, cents)
    for c in range(NLIST):
        members = db[labels == c]
        if len(members):
            cents[c] = members.mean(0)
labels = assign(db, cents)
lists = [np.where(labels == c)[0] for c in range(NLIST)]  # the "inverted file": cluster -> vector ids

# Ground truth: exact top-10 by a full scan of all 100,000 vectors.
exact = np.argsort(sqdist(queries, db), axis=1)[:, :K]

print(f"synthetic data: {N} vectors, dim {D}, {BLOBS} blobs, {NLIST} k-means clusters, {NQ} queries")
print(f"cluster sizes: min {min(map(len, lists))}, median {int(np.median(list(map(len, lists))))}, max {max(map(len, lists))}")
print(f"{'searched':>8} {'recall@10':>10} {'compared':>9} {'ms/query':>9}")

for nprobe in [1, 2, 4, 8, 16, 32]:
    hits, compared, times = 0, 0, []
    for q, truth in zip(queries, exact):
        t0 = time.perf_counter()
        near = sqdist(q[None], cents)[0].argsort()[:nprobe]       # pick the nearest clusters
        ids = np.concatenate([lists[c] for c in near])            # only these vectors get compared
        top = ids[sqdist(q[None], db[ids])[0].argsort()[:K]]
        times.append(time.perf_counter() - t0)
        hits += len(set(top) & set(truth))
        compared += len(ids)
    print(f"{nprobe:>8} {hits / (NQ * K):>10.3f} {compared / (NQ * N):>9.2%} {np.median(times) * 1000:>9.2f}")

# Baseline: the exact full scan, timed the same way.
times = []
for q in queries:
    t0 = time.perf_counter()
    db_top = sqdist(q[None], db)[0].argsort()[:K]
    times.append(time.perf_counter() - t0)
print(f"{'full scan':>8} {1.0:>10.3f} {1:>9.2%} {np.median(times) * 1000:>9.2f}   (exact answer, 100% recall by definition)")
