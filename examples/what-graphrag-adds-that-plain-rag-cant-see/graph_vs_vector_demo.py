"""Backs the claims in posts/what-graphrag-adds-that-plain-rag-cant-see.md.
Run with: uv run examples/what-graphrag-adds-that-plain-rag-cant-see/graph_vs_vector_demo.py

A real (tiny) knowledge graph, queried two ways: a single-hop lookup a plain
chunk-similarity search could also do, versus a multi-hop traversal a
similarity search over isolated text chunks has no way to perform, because
the connecting fact never appears in either chunk on its own.
"""

edges = [
    ("Wastewater Surveillance", "UTILIZES", "BioSense Sensor Network"),
    ("BioSense Sensor Network", "MANAGED_BY", "Jane Doe"),
    ("Jane Doe", "WORKS_IN", "Environmental Health Division"),
]

graph: dict[str, list[tuple[str, str]]] = {}
for src, rel, dst in edges:
    graph.setdefault(src, []).append((rel, dst))


def walk(node: str) -> list[str]:
    """Follow edges from `node` to the end of the chain, one hop at a time."""
    chain = [node]
    while graph.get(chain[-1]):
        _, dst = graph[chain[-1]][0]
        chain.append(dst)
    return chain


print("One-hop fact (a vector search over the right chunk could find this too):")
print("  Wastewater Surveillance --UTILIZES--> BioSense Sensor Network")
print()

print("Two-hop question: 'Who manages the sensor network the Wastewater")
print("Surveillance project utilizes?' -- no single chunk states this; it")
print("only exists by walking two edges across the graph:")
print("  " + " -> ".join(walk("Wastewater Surveillance")))
print(f"  answer: {walk('Wastewater Surveillance')[2]}")
