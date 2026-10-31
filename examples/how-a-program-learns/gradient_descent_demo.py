"""Backs the claims in posts/how-a-program-learns.md.
Run with: uv run examples/how-a-program-learns/gradient_descent_demo.py"""

# Fixed data: the true relationship is y = 2x + 1.
xs = [1.0, 2.0, 3.0, 4.0, 5.0]
ys = [3.0, 5.0, 7.0, 9.0, 11.0]

w, b = 0.0, 0.0  # no rule programmed in -- both start at zero
lr = 0.05

for step in range(1, 6):
    preds = [w * x + b for x in xs]
    errors = [p - y for p, y in zip(preds, ys)]
    loss = sum(e**2 for e in errors) / len(errors)

    print(f"step {step}: w={w:.3f} b={b:.3f} loss={loss:.3f}")

    grad_w = 2 * sum(e * x for e, x in zip(errors, xs)) / len(xs)
    grad_b = 2 * sum(errors) / len(xs)
    w -= lr * grad_w
    b -= lr * grad_b
