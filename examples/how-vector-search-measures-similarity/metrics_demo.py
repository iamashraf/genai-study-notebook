"""Rank 40 sentences by cosine, dot product and negative Euclidean distance,
on raw nomic-embed-text vectors and on the same vectors scaled to length 1."""
import json
import urllib.request
import numpy as np

TOPICS = {
    "cooking": [
        "Simmer the tomato sauce for twenty minutes before adding basil.",
        "Knead the bread dough until it springs back when pressed.",
        "Season the steak with salt and sear it in a hot pan.",
        "Whisk the eggs and sugar until the mixture turns pale.",
        "Roast the vegetables with olive oil at high heat.",
        "Let the pie cool before slicing so the filling sets.",
        "Chop the onions finely and fry them until golden.",
        "Marinate the chicken overnight in yogurt and spices.",
    ],
    "travel": [
        "Our flight to Lisbon leaves at dawn from terminal two.",
        "Book the hostel early because the beach town fills up in summer.",
        "The train from Tokyo to Kyoto takes about two hours.",
        "Pack a passport, a charger and a light jacket for the trip.",
        "We rented a car and drove along the coast for three days.",
        "The museum pass saves money if you visit several sites.",
        "Customs lines were short when we landed in Toronto.",
        "A backpacking trip through the Andes needs sturdy boots.",
    ],
    "finance": [
        "The central bank raised interest rates by a quarter point.",
        "Diversifying a portfolio spreads risk across several assets.",
        "Quarterly earnings beat expectations and the stock jumped.",
        "A mortgage payment depends on the loan size and the rate.",
        "Inflation reduced the purchasing power of savings accounts.",
        "The company issued new bonds to refinance its debt.",
        "Index funds charge lower fees than actively managed funds.",
        "Tax returns are due by April for most salaried workers.",
    ],
    "sports": [
        "The striker scored twice in the second half to win the match.",
        "She ran the marathon in under three hours.",
        "The goalkeeper saved a penalty in the final minute.",
        "Our basketball team practices free throws every morning.",
        "The tennis final went to a fifth set tiebreak.",
        "He trained for months before the swimming championship.",
        "The coach changed the lineup at halftime.",
        "Cyclists climbed the mountain stage in heavy rain.",
    ],
    "weather": [
        "A cold front will bring heavy rain and strong wind tonight.",
        "Temperatures dropped below freezing and frost covered the fields.",
        "The forecast shows clear skies and light breezes all weekend.",
        "Thunderstorms rolled across the valley in the afternoon.",
        "Fog hid the bridge until the sun burned it off.",
        "A heat wave pushed the thermometer past forty degrees.",
        "Snow fell steadily and buried the road overnight.",
        "Humidity made the evening feel sticky and still.",
    ],
}
QUERIES = {
    "cooking": "How long should I bake the cake?",
    "travel": "What should I bring on a trip abroad?",
    "finance": "Should I put my money in stocks or bonds?",
    "sports": "Who won the game last night?",
    "weather": "Is it going to storm tomorrow?",
}

def embed(texts):
    req = urllib.request.Request(
        "http://localhost:11434/api/embed",
        data=json.dumps({"model": "nomic-embed-text", "input": texts}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return np.array(json.load(r)["embeddings"], dtype=np.float64)

sentences = [s for t in TOPICS for s in TOPICS[t]]
labels = [t for t in TOPICS for _ in TOPICS[t]]
vecs = embed(sentences + list(QUERIES.values()))
docs, qs = vecs[:40], vecs[40:]

lengths = np.linalg.norm(docs, axis=1)
print(f"sentences: {len(docs)}, dimensions: {docs.shape[1]}")
print(f"raw sentence vector length: min {lengths.min():.6f}, mean {lengths.mean():.6f}, max {lengths.max():.6f}")
print(f"raw query vector length:    min {np.linalg.norm(qs, axis=1).min():.6f}, max {np.linalg.norm(qs, axis=1).max():.6f}")

def unit(m):
    return m / np.linalg.norm(m, axis=1, keepdims=True)

def top5(q, d):
    cos = (d @ q) / (np.linalg.norm(d, axis=1) * np.linalg.norm(q))
    dot = d @ q
    neg = -np.linalg.norm(d - q, axis=1)
    return {n: list(np.argsort(-s, kind="stable")[:5]) for n, s in
            (("cosine", cos), ("dot", dot), ("neg_euclid", neg))}

def diff(a, b):
    return 5 - len(set(a) & set(b))

print("\nTop-5 results that differ from cosine's top 5 (0 = same five sentences):")
print(f"{'query':<9} {'vectors':<7} {'dot':>4} {'euclid':>7}  {'dot vs euclid':>13}")
for (topic, _), q in zip(QUERIES.items(), qs):
    for name, d, qq in (("raw", docs, q), ("scaled", unit(docs), q / np.linalg.norm(q))):
        t = top5(qq, d)
        print(f"{topic:<9} {name:<7} {diff(t['cosine'], t['dot']):>4} "
              f"{diff(t['cosine'], t['neg_euclid']):>7}  {diff(t['dot'], t['neg_euclid']):>13}")

print("\nOn-topic hits in cosine top 5 (raw):")
for (topic, _), q in zip(QUERIES.items(), qs):
    t = top5(q, docs)["cosine"]
    print(f"{topic:<9} {sum(labels[i] == topic for i in t)}/5")

# --- synthetic section: unequal vector lengths, fixed seed, no model involved ---
print("\nSynthetic check (numpy seed 0, 4 dimensions, 8 candidates with unequal lengths):")
rng = np.random.default_rng(0)
q = np.array([1.0, 0.0, 0.0, 0.0])
dirs = rng.normal(size=(8, 4)) + 2 * q
dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
lens = rng.uniform(0.3, 5.0, size=8)
C = dirs * lens[:, None]
scores = {
    "cosine": (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q)),
    "dot": C @ q,
    "neg_euclid": -np.linalg.norm(C - q, axis=1),
}
print(f"{'id':>2} {'length':>7} {'cosine':>7} {'dot':>7} {'distance':>9}")
for i in range(8):
    print(f"{i:>2} {lens[i]:>7.2f} {scores['cosine'][i]:>7.3f} {scores['dot'][i]:>7.3f} {-scores['neg_euclid'][i]:>9.3f}")
for name, s in scores.items():
    print(f"top 3 by {name:<10}: {[int(i) for i in np.argsort(-s, kind='stable')[:3]]}")
