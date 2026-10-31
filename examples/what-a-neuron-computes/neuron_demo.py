"""Backs the claims in posts/what-a-neuron-computes.md.
Run with: uv run examples/what-a-neuron-computes/neuron_demo.py"""

import math

inputs = [2.0, -1.0]
weights = [0.5, 1.5]
bias = 0.2

z = sum(w * x for w, x in zip(weights, inputs)) + bias
output = 1 / (1 + math.exp(-z))  # sigmoid activation

print(f"weighted sum (z) = {z}")
print(f"activation output = {output:.4f}")
