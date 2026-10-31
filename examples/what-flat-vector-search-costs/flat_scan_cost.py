"""Time a flat (full-scan) vector search on synthetic data. numpy only.

Synthetic data, fixed seed: random unit vectors, dimension 384, float32.
Per query: dot product of the query with every vector, then the top 10.
Time per size = median of 20 timed runs after one warm-up run.
"""
import time
import numpy as np

DIM, K, RUNS = 384, 10, 20
SIZES = [10_000, 50_000, 100_000, 250_000, 500_000]

rng = np.random.default_rng(0)


def unit(a):
    return (a / np.linalg.norm(a, axis=1, keepdims=True)).astype(np.float32)


def scan(vectors, query):
    scores = vectors @ query                      # compare with every vector
    top = np.argpartition(scores, -K)[-K:]        # pick the 10 best
    return top[np.argsort(scores[top])[::-1]]


query = unit(rng.standard_normal((1, DIM)))[0]
print(f"synthetic random unit vectors, dim={DIM}, float32, seed=0, top {K}")
print(f"{'vectors':>9} {'ms/query':>9} {'ms/1,000 vectors':>17} {'memory (MB)':>12}")
for n in SIZES:
    vectors = unit(rng.standard_normal((n, DIM)))
    scan(vectors, query)                          # warm-up
    times = []
    for _ in range(RUNS):
        t = time.perf_counter()
        scan(vectors, query)
        times.append(time.perf_counter() - t)
    ms = float(np.median(times)) * 1000
    print(f"{n:>9,} {ms:>9.2f} {ms / (n / 1000):>17.4f} {vectors.nbytes / 1e6:>12.1f}")
    del vectors
