"""Split quantisation error into the part along each vector and the part sideways to it,
then see which part changes the top-10 inner-product ranking more.
Synthetic data, fixed seed. An illustration of the paper's observation, not ScaNN."""
import numpy as np

rng = np.random.default_rng(0)
N, D, K, Q, TOP = 20_000, 64, 256, 200, 10

# Synthetic database: 50 loose clusters in 64 dimensions.
centers = rng.normal(size=(50, D)) * 2.0
X = centers[rng.integers(0, 50, N)] + rng.normal(size=(N, D))
queries = rng.normal(size=(Q, D))

# Ordinary k-means quantisation: each vector is replaced by its nearest centroid.
C = X[rng.choice(N, K, replace=False)].copy()
for _ in range(15):
    d = (X**2).sum(1)[:, None] - 2 * X @ C.T + (C**2).sum(1)[None]
    a = d.argmin(1)
    for k in range(K):
        m = a == k
        if m.any():
            C[k] = X[m].mean(0)
d = (X**2).sum(1)[:, None] - 2 * X @ C.T + (C**2).sum(1)[None]
Xq = C[d.argmin(1)]

# Error = original minus quantised. Parallel part lies along the original vector.
R = X - Xq
r_par = ((R * X).sum(1) / (X * X).sum(1))[:, None] * X
r_perp = R - r_par

print(f"vectors={N} dim={D} centroids={K} queries={Q} seed=0 (synthetic data)")
print(f"average length of original vector:   {np.linalg.norm(X, axis=1).mean():.3f}")
print(f"average length of parallel error:    {np.linalg.norm(r_par, axis=1).mean():.3f}")
print(f"average length of perpendicular error: {np.linalg.norm(r_perp, axis=1).mean():.3f}")


def top_ids(db):
    s = queries @ db.T
    return np.argsort(-s, axis=1)[:, :TOP]


def changed(db):
    base = top_ids(X)
    new = top_ids(db)
    kept = [len(set(b) & set(n)) for b, n in zip(base, new)]
    return 100 * (1 - np.mean(kept) / TOP)


print(f"\nshare of the true top-{TOP} that drops out of the top-{TOP} (mean over {Q} queries):")
print(f"  full quantisation error applied: {changed(X - R):5.1f}%")
print(f"  only parallel error applied:     {changed(X - r_par):5.1f}%")
print(f"  only perpendicular error applied:{changed(X - r_perp):5.1f}%")

# Test closer to the paper's claim: how much does a unit-length error in each direction
# move the query-vector score <q, x>, for high-scoring pairs vs. pairs picked at random?
ok = np.linalg.norm(r_perp, axis=1) > 1e-9          # skip vectors that sit exactly on a centroid
u_par = X / np.linalg.norm(X, axis=1, keepdims=True)
u_perp = np.zeros_like(X)
u_perp[ok] = r_perp[ok] / np.linalg.norm(r_perp[ok], axis=1, keepdims=True)
top = top_ids(X)
qi_top, xi_top = np.repeat(np.arange(Q), TOP), top.ravel()
pick = np.random.default_rng(1)
qi_rnd, xi_rnd = pick.integers(0, Q, 200_000), pick.integers(0, N, 200_000)


def sens(qi, xi):
    keep = ok[xi]
    qi, xi = qi[keep], xi[keep]
    return ((queries[qi] * u_par[xi]).sum(1) ** 2).mean(), ((queries[qi] * u_perp[xi]).sum(1) ** 2).mean()


print("\nmean squared change in the score <q, x> caused by an error of length 1:")
for name, (qi, xi) in [("true top-10 pairs", (qi_top, xi_top)), ("random pairs", (qi_rnd, xi_rnd))]:
    p, o = sens(qi, xi)
    print(f"  {name:<18} along the vector: {p:6.2f}   sideways: {o:5.2f}   ratio: {p / o:5.1f}")
