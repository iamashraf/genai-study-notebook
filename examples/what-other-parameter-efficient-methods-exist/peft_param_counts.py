"""Trainable-parameter arithmetic for three parameter-efficient methods.
One stated configuration. This is arithmetic from each paper's definition, not a training run."""

L = 12      # Transformer layers
d = 768     # hidden size
m = 64      # adapter bottleneck size
p_prefix = 20   # prefix length
p_prompt = 20   # prompt length

# Full model: the 12 Transformer blocks only (embeddings and output head left out,
# since this configuration states no vocabulary size).
attn = 4 * (d * d + d)                      # Q, K, V, output projections with biases
ffn = (d * 4 * d + 4 * d) + (4 * d * d + d)  # two feed-forward layers, hidden size 4*d
norms = 2 * (2 * d)                          # two layer norms (scale + shift)
per_block = attn + ffn + norms
full = L * per_block

# Adapters (Houlsby et al.): 2md + d + m per adapter, two adapters per layer.
adapter = L * 2 * (2 * m * d + d + m)

# Prefix tuning (Li and Liang): a |P| x dim(h) matrix, where dim(h) joins the
# key and value of every layer: 2 * L * d.
prefix = p_prefix * (2 * L * d)

# Prompt tuning (Lester et al.): a p x e matrix, e = embedding size (= d here).
prompt = p_prompt * d

rows = [("Full fine-tuning", full), ("Adapters", adapter),
        ("Prefix tuning", prefix), ("Prompt tuning", prompt)]
print(f"Configuration: {L} layers, hidden size {d}, adapter bottleneck {m}, "
      f"prefix length {p_prefix}, prompt length {p_prompt}")
print(f"Full model (blocks only): {full:,} parameters\n")
print(f"{'Method':<18}{'Trainable':>14}{'% of full':>12}")
for name, n in rows:
    print(f"{name:<18}{n:>14,}{100 * n / full:>11.3f}%")
print(f"\nFull / prompt tuning ratio: {full / prompt:,.0f}x")
