"""Backs the claims in posts/01-what-is-a-token.md. Run with: uv run examples/01-what-is-a-token/tokenize_demo.py"""

import tiktoken

enc = tiktoken.get_encoding("o200k_base")  # tiktoken.encoding_for_model("gpt-4o")

for word in ["hello", "tokenization", "strawberry", "unbelievable"]:
    ids = enc.encode(word)
    print(word, "->", ids, "->", [enc.decode([i]) for i in ids])
