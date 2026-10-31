# GenAI Study Notebook

Short, plain-language explainers on AI, LLMs, and generative AI: concepts,
papers, and techniques, written while learning them. No formulas — a gist
anyone can follow, with links out to primary sources for the depth. Starts
as my own notes; the goal is to make this material easier for other
engineers to pick up too, and to connect to words they hear in meetings.

## How this works

There's no fixed reading order and no numbering. Each post links directly
to whatever other post or source it depends on, right where that term
comes up in the text — so you can start anywhere and follow links outward
or backward as needed. When a post needs a prior concept that doesn't
have its own post yet, that post gets written first, then linked in.

Every post states its own read time at the top (2-5 min, whatever the
topic needs). A post that verifies a claim by running code keeps that
code in a matching `examples/<slug>/` folder, runnable with
`uv run examples/<slug>/<script>.py`.

Most posts also carry a diagram as a real SVG file in `assets/<slug>.svg`,
embedded with a normal markdown image tag — not a Mermaid code block, so
it renders the same everywhere (GitHub, a local editor preview, a plain
file browser) instead of only where Mermaid is supported. Each one plots
the post's own real numbers (the measured scores, weights, or counts from
its example), not a generic illustration. A few posts also link to a
small interactive tool published as a Claude.ai Artifact; those links are
private by default — only shared if you open the page and share it.

## Posts

| Post | Status |
|------|--------|
| [Why Doesn't an AI Have to Think Like a Human?](posts/why-ai-doesnt-have-to-think-like-a-human.md) | Draft |
| [How Can a Program "Learn" a Rule Nobody Programmed?](posts/how-a-program-learns.md) | Draft |
| [What Does a Single Neuron In a Neural Network Actually Compute?](posts/what-a-neuron-computes.md) | Draft |
| [Why Does An LLM Split "Strawberry" Into Three Pieces?](posts/what-is-a-token.md) | Draft |
| [Why Is "Kitten" Closer to "Cat" Than "Car" Is?](posts/what-is-an-embedding.md) | Draft |
| [How Does a Transformer Decide Which Earlier Words Matter?](posts/how-attention-weighs-words.md) | Draft |
| [Why Does a Transformer Need to Be Told Word Order, When Attention Doesn't See It?](posts/why-transformers-need-position.md) | Draft |
| [What Is an LLM, Actually?](posts/what-is-an-llm.md) | Draft |
| [What Does "Fine-Tuning" Actually Change in an Already-Trained Model?](posts/what-fine-tuning-changes.md) | Draft |
| [What Does RLHF Add on Top of Fine-Tuning?](posts/what-rlhf-adds.md) | Draft |
| [Why Can a Few Examples Teach an LLM Something a Plain Instruction Can't?](posts/why-a-few-examples-teach-what-instructions-cant.md) | Draft |
| [What Does Telling an LLM to "Think Step by Step" Actually Change?](posts/what-thinking-step-by-step-actually-changes.md) | Draft |
| [Why Does the Same Prompt Give a Different Answer Each Time?](posts/why-the-same-prompt-gives-different-answers.md) | Draft |
| [Why Do LLMs State Fake Facts With Total Confidence?](posts/why-llms-state-fake-facts-with-total-confidence.md) | Draft |
| [What Is a "Context Window," and Why Does It Run Out?](posts/what-a-context-window-actually-limits.md) | Draft |
| [What Problem Does RAG Actually Solve?](posts/what-problem-does-rag-actually-solve.md) | Draft |
| [Why Can't You Just Grep Your Way to Semantic Search?](posts/why-you-cant-just-grep-your-way-to-semantic-search.md) | Draft |
| [What Does GraphRAG Add That Plain RAG Can't See?](posts/what-graphrag-adds-that-plain-rag-cant-see.md) | Draft |
| [What's Actually Different Between an "AI Agent" and "Agentic AI"?](posts/ai-agents-vs-agentic-ai.md) | Draft |
| [Why Does Chunking Strategy Matter More Than Which Database You Pick?](posts/why-chunking-strategy-matters-more-than-your-database.md) | Draft |
| [Why Do RAG Systems Combine Keyword Search With Vector Search?](posts/why-rag-systems-combine-keyword-and-vector-search.md) | Draft |
| [How Do You Know If a RAG Answer Is Actually Any Good?](posts/how-do-you-know-if-a-rag-answer-is-any-good.md) | Draft |
| [What Are the Different Ways a Vector Database Can Index Your Data?](posts/what-different-vector-index-strategies-trade-off.md) | Draft |
| [What Are the Different Ways to Chunk a Document?](posts/what-different-ways-to-chunk-a-document-exist.md) | Draft |
| [What Is Context Engineering, and How Is It Different from Prompt Engineering?](posts/what-context-engineering-is.md) | Draft |
| [Why Can Giving an LLM More Context Make It Worse, Not Better?](posts/why-more-context-can-make-an-llm-worse.md) | Draft |
| [What Is Context Poisoning?](posts/what-is-context-poisoning.md) | Draft |
| [What Is Context Compaction?](posts/what-context-compaction-is.md) | Draft |
| [Why Do Agents Need Memory Beyond the Context Window?](posts/why-agents-need-memory-beyond-the-context-window.md) | Draft |
| [Why Do Tool Results Quietly Fill Up an Agent's Context?](posts/why-tool-results-bloat-context.md) | Draft |
| [What Are Context Distraction, Confusion, and Clash?](posts/what-context-distraction-confusion-and-clash-are.md) | Draft |
| [How Does Prompt Caching Make Long Prompts Cheaper?](posts/how-prompt-caching-works.md) | Draft |
| [What Is "Just-in-Time" Context?](posts/what-just-in-time-context-is.md) | Draft |
| [What Is the Agent Loop?](posts/what-the-agent-loop-is.md) | Draft |
| [Why Do Agent Loops Need Stop Conditions?](posts/why-agent-loops-need-stop-conditions.md) | Draft |
| [How Does an Agent Recover From Its Own Mistakes?](posts/how-an-agent-recovers-from-its-own-mistakes.md) | Draft |
| [What Is Prompt Injection?](posts/what-prompt-injection-is.md) | Draft |
| [Why Is Indirect Prompt Injection Harder to Stop?](posts/why-indirect-prompt-injection-is-harder.md) | Draft |
| [What Is a Jailbreak, and Why Does It Work?](posts/what-a-jailbreak-is-and-why-it-works.md) | Draft |
| [What Do Guardrails Actually Catch, and What Slips Through?](posts/what-guardrails-do-and-dont-catch.md) | Draft |
| [Why Does Giving an LLM Tools Raise the Security Stakes?](posts/why-an-agent-with-tools-raises-the-stakes.md) | Draft |
