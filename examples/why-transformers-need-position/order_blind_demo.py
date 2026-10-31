"""Backs the claims in posts/why-transformers-need-position.md.
Run with: uv run examples/why-transformers-need-position/order_blind_demo.py

Shows that self-attention alone doesn't know sequence order: the same
token gets the same output whether it's first or second, as long as the
*set* of tokens around it is the same. Positional encoding is what fixes
this (not demonstrated here -- this script only shows the problem it solves).
"""

import math


def self_attention(vectors):
    """Real attention: dot-product score -> softmax -> weighted blend,
    run once per vector in the sequence, each acting as the query."""
    outputs = []
    for query in vectors:
        scores = [sum(q * k for q, k in zip(query, key)) for key in vectors]
        exp_scores = [math.exp(s) for s in scores]
        total = sum(exp_scores)
        weights = [e / total for e in exp_scores]
        blended = [sum(w * v[d] for w, v in zip(weights, vectors)) for d in range(len(query))]
        outputs.append(blended)
    return outputs


vec_A, vec_B, vec_C = [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]

order1 = [vec_A, vec_B, vec_C]          # A, B, C
order2 = [vec_C, vec_A, vec_B]          # same tokens, different order

out1 = self_attention(order1)
out2 = self_attention(order2)

print("order1 output for A (position 0):", [round(x, 4) for x in out1[0]])
print("order2 output for A (position 1):", [round(x, 4) for x in out2[1]])
print("same values -> attention alone never noticed A moved")
