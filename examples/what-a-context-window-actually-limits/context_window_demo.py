"""Backs the claims in posts/what-a-context-window-actually-limits.md.
Run with: uv run examples/what-a-context-window-actually-limits/context_window_demo.py

Counts the real token length of this project's own posts with the same
tokenizer used in posts/what-is-a-token.md, then shows what fraction of a
few real model context windows that would consume.
"""

import glob

import tiktoken

encoding = tiktoken.get_encoding("o200k_base")

posts_dir = "posts"
total_tokens = 0
for path in sorted(glob.glob(f"{posts_dir}/*.md")):
    with open(path) as f:
        total_tokens += len(encoding.encode(f.read()))

context_windows = {
    "GPT-2 (2019)": 1024,
    "GPT-3.5 (original)": 4096,
    "Claude Sonnet 4.5": 200_000,
    "Claude Sonnet 5 / 1M-token models": 1_000_000,
}

print(f"all current posts, tokenized: {total_tokens} tokens")
print()
for name, size in context_windows.items():
    pct = total_tokens / size * 100
    print(f"{name} ({size:,} tokens): this project's posts alone use {pct:.2f}% of it")
