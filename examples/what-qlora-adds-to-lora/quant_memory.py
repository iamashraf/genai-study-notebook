"""Memory arithmetic and block-wise absmax uniform quantization on SYNTHETIC weights.
This is plain uniform quantization, not NF4."""
import numpy as np

# Part 1: memory for a 7B-parameter model (bytes = params x bits / 8)
params = 7_000_000_000
print("Part 1: memory to store 7B weights")
for bits in (16, 8, 4):
    print(f"  {bits:>2}-bit: {params * bits / 8 / 1e9:.1f} GB")

# Part 2: quantize a synthetic Gaussian matrix, block-wise, absmax scaling
rng = np.random.default_rng(0)
W = rng.standard_normal((4096, 4096)).astype(np.float32)  # synthetic, not real model weights
BLOCK = 64

def quantize(W, bits):
    blocks = W.reshape(-1, BLOCK)
    scale = np.abs(blocks).max(axis=1, keepdims=True)   # one absmax constant per block
    levels = 2 ** (bits - 1) - 1                         # 127 for 8-bit, 7 for 4-bit
    q = np.round(blocks / scale * levels)                # integers in [-levels, levels]
    return (q / levels * scale).reshape(W.shape)         # unpack back to floats

print("\nPart 2: synthetic 4096x4096 Gaussian matrix, block size 64, fixed seed 0")
base_gb = W.size * 16 / 8 / 1e9
print(f"  16-bit storage: {base_gb * 1000:.1f} MB")
for bits in (8, 4):
    err = np.abs(W - quantize(W, bits)).mean()
    # bits per weight plus one 32-bit scale per 64-weight block
    stored_bits = bits + 32 / BLOCK
    stored_mb = W.size * stored_bits / 8 / 1e6
    saved = 100 * (1 - stored_mb / (base_gb * 1000))
    print(f"  {bits}-bit: mean abs error {err:.5f}, stored {stored_mb:.1f} MB "
          f"(incl. scales), saved {saved:.1f}% vs 16-bit")
print(f"  (mean absolute value of the weights themselves: {np.abs(W).mean():.5f})")
