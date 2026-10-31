"""Backs the claims in posts/how-attention-weighs-words.md.
Run with: uv run examples/how-attention-weighs-words/attention_demo.py

This runs the real attention calculation (dot-product score -> softmax ->
weighted blend), the same three steps a transformer uses. The vectors
below are hand-picked for illustration, not weights from a real trained
model -- but the math applied to them is the real mechanism.

Sentence: "The trophy didn't fit in the suitcase because it was too big."
Toy 2D vectors stand in for each word's learned embedding.
"""

import math

tokens = {
    "The": [0.0, 0.0],
    "trophy": [1.0, 0.0],
    "suitcase": [0.2, 0.0],
    "it": [0.9, 0.0],  # the query: what should "it" pay attention to?
}

query = tokens["it"]
keys = tokens

scores = {word: sum(q * k for q, k in zip(query, vec)) for word, vec in keys.items()}

# softmax: turn raw scores into weights that sum to 1
exp_scores = {w: math.exp(s) for w, s in scores.items()}
total = sum(exp_scores.values())
weights = {w: e / total for w, e in exp_scores.items()}

for word in tokens:
    print(f"attention('it' -> '{word}') = {weights[word]:.3f}")
