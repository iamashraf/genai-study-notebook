"""LoRA toy demo. Synthetic data, fixed seed, numpy only. This is a toy, not an LLM."""
import numpy as np

# Part 1: trainable-parameter arithmetic for one 4096 x 4096 weight matrix.
d = 4096
full = d * d
print(f"Part 1: one {d}x{d} weight matrix")
print(f"full fine-tune trainable: {full:,}")
for r in (1, 4, 8, 16, 64):
    lora = d * r + r * d  # thin matrix B (d x r) plus thin matrix A (r x d)
    print(f"LoRA rank {r:>2}: {lora:>9,} trainable = {100 * lora / full:.3f}% of full")

# Part 2: tiny training run. W is frozen. Target = W + a true rank-4 change.
n, true_rank = 64, 4
rng = np.random.default_rng(0)
W = rng.normal(size=(n, n))
delta = rng.normal(size=(n, true_rank)) @ rng.normal(size=(true_rank, n))
delta /= np.linalg.norm(delta)  # change has Frobenius norm 1
target = W + delta
print(f"\nPart 2: frozen {n}x{n} W, true change has rank {true_rank}")
print(f"error before training (change not yet learned): {np.linalg.norm(target - W):.6f}")

for r in (1, 2, 4, 8):
    B = np.zeros((n, r))                    # starts at zero, so W + B@A starts equal to W
    A = rng.normal(size=(r, n)) * 0.1
    lr = 0.2
    for _ in range(20000):
        E = (W + B @ A) - target            # gradient of 0.5*||E||^2
        gB, gA = E @ A.T, B.T @ E
        B -= lr * gB
        A -= lr * gA
    err = np.linalg.norm(W + B @ A - target)
    print(f"rank {r}: final error {err:.6f}  (trainable {2 * n * r:,} vs full {n * n:,})")
