"""Compress embeddings of this repo's own paragraphs and measure recall@10 against float32."""
import json, re, urllib.request
import numpy as np

rng = np.random.default_rng(0)

# --- corpus: paragraphs (>= 20 words) from a fixed list of 27 posts, no code blocks, no ## Sources ---
# The list is pinned so the numbers do not change when other posts are edited.
POSTS = [
    "ai-agents-vs-agentic-ai.md",
    "how-a-program-learns.md",
    "how-attention-weighs-words.md",
    "how-do-you-know-if-a-rag-answer-is-any-good.md",
    "what-a-context-window-actually-limits.md",
    "what-a-neuron-computes.md",
    "what-context-engineering-is.md",
    "what-different-vector-index-strategies-trade-off.md",
    "what-different-ways-to-chunk-a-document-exist.md",
    "what-fine-tuning-changes.md",
    "what-graphrag-adds-that-plain-rag-cant-see.md",
    "what-is-a-token.md",
    "what-is-an-embedding.md",
    "what-is-an-llm.md",
    "what-is-context-poisoning.md",
    "what-problem-does-rag-actually-solve.md",
    "what-rlhf-adds.md",
    "what-thinking-step-by-step-actually-changes.md",
    "why-a-few-examples-teach-what-instructions-cant.md",
    "why-ai-doesnt-have-to-think-like-a-human.md",
    "why-chunking-strategy-matters-more-than-your-database.md",
    "why-llms-state-fake-facts-with-total-confidence.md",
    "why-more-context-can-make-an-llm-worse.md",
    "why-rag-systems-combine-keyword-and-vector-search.md",
    "why-the-same-prompt-gives-different-answers.md",
    "why-transformers-need-position.md",
    "why-you-cant-just-grep-your-way-to-semantic-search.md",
]
paras = []
for f in sorted(POSTS):
    text = re.sub(r"```.*?```", "", open("posts/" + f).read(), flags=re.S)
    text = text.split("## Sources")[0]
    for p in re.split(r"\n\s*\n", text):
        p = p.strip()
        if len(p.split()) >= 20 and not p.startswith(("#", "!", "|")):
            paras.append(p)
paras = [paras[i] for i in sorted(rng.choice(len(paras), min(400, len(paras)), replace=False))]
print(f"paragraphs: {len(paras)}")

def embed(batch):
    req = urllib.request.Request("http://localhost:11434/api/embed",
        data=json.dumps({"model": "nomic-embed-text", "input": batch}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=600))["embeddings"]

vecs = []
for i in range(0, len(paras), 50):
    vecs += embed(paras[i:i + 50])
X = np.array(vecs, dtype=np.float32)
n, d = X.shape
print(f"embedding dimensions: {d}")
queries = sorted(rng.choice(n, 40, replace=False))

def unit(A):
    return A / np.linalg.norm(A, axis=1, keepdims=True)

def top10(scores):
    out = []
    for q in queries:
        s = scores(q).copy()
        s[q] = -np.inf  # exclude the query itself
        out.append(set(np.argsort(-s)[:10]))
    return out

def cos_scores(V):
    V = unit(V.astype(np.float32))
    return lambda q: V @ V[q]

truth = top10(cos_scores(X))

def recall(res):
    return np.mean([len(a & b) / 10 for a, b in zip(truth, res)])

rows = []
rows.append(("float32", 4 * d, truth))

# float16
H = X.astype(np.float16)
rows.append(("float16", 2 * d, top10(cos_scores(H.astype(np.float32)))))

# int8 scalar quantisation: per-dimension min/max mapped to 0..255
lo, hi = X.min(0), X.max(0)
Q = np.round((X - lo) / (hi - lo) * 255).astype(np.uint8)
rows.append(("int8 scalar", d, top10(cos_scores(Q.astype(np.float32) / 255 * (hi - lo) + lo))))

# 1-bit binary: sign of each number, ranked by Hamming agreement
B = X > 0
rows.append(("1-bit binary", d // 8, top10(lambda q: -(B != B[q]).sum(1).astype(np.float32))))

# product quantisation: M subvectors, K centroids each, a few k-means iterations
M, K = 96, 16
print(f"PQ: {M} subvectors x {K} centroids ({len(paras)} vectors are too few to train 256 centroids)")
sub = d // M
codes = np.zeros((n, M), dtype=np.uint8)
recon = np.zeros_like(X)
for m in range(M):
    part = X[:, m * sub:(m + 1) * sub]
    cent = part[rng.choice(n, K, replace=False)].copy()
    for _ in range(10):
        a = ((part[:, None, :] - cent[None]) ** 2).sum(2).argmin(1)
        for k in range(K):
            if (a == k).any():
                cent[k] = part[a == k].mean(0)
    a = ((part[:, None, :] - cent[None]) ** 2).sum(2).argmin(1)
    codes[:, m] = a
    recon[:, m * sub:(m + 1) * sub] = cent[a]
pq_bytes = int(np.ceil(M * np.log2(K) / 8))  # 4 bits per code when K=16
rows.append((f"PQ {M}x{K}", pq_bytes, top10(cos_scores(recon))))

print(f"\n{'method':<14}{'bytes/vector':>14}{'saved vs float32':>18}{'recall@10':>11}")
for name, b, res in rows:
    print(f"{name:<14}{b:>14}{1 - b / (4 * d):>18.1%}{recall(res):>11.3f}")
