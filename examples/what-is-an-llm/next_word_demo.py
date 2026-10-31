"""Backs the claims in posts/what-is-an-llm.md.
Run with: uv run examples/what-is-an-llm/next_word_demo.py

A toy, non-neural stand-in for "predict the next token": count which word
follows "the cat" most often in a tiny corpus, and predict that one.
Real LLMs don't count word pairs like this -- they use a trained neural
network (a transformer) -- but the goal is the same: predict the next
token from patterns learned in training data.
"""

from collections import Counter

corpus = [
    "the cat sat on the mat",
    "the cat sat on the rug",
    "the cat ate the fish",
]

next_words = Counter()
for line in corpus:
    words = line.split()
    for i in range(len(words) - 2):
        if words[i] == "the" and words[i + 1] == "cat":
            next_words[words[i + 2]] += 1

total = sum(next_words.values())
for word, count in next_words.most_common():
    print(f"after 'the cat': '{word}' -> {count}/{total} = {count/total:.2f}")
