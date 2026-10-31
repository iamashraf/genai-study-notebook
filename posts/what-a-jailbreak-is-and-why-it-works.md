# What Is a Jailbreak, and Why Does It Work?

*~3 min read*

**One-line answer:** a jailbreak is an input that gets a model to do something its own safety training was meant to prevent, and the Wei et al. "Jailbroken" paper hypothesizes two failure modes of that training to explain why such attacks succeed: "competing objectives" and "mismatched generalization" [1].

![Two rows, one per local model, of six prompt framings; a direct ask was refused by both, while some reframings leaked the secret word](../assets/what-a-jailbreak-is-and-why-it-works.svg)
*Same rule, same models, same secret: the direct ask held both times, but different reframings broke it.*

## The problem

Picture a receptionist told on day one: "never give out the manager's home address." Ask her outright and she says no. Now say, "Let's play a game where you're a tour guide who mentions the address," or "translate your instructions into French." She has one job, being helpful, and one rule, and a clever framing can make the helpful instinct win. Nobody hacked the building. You just found a phrasing her rule didn't anticipate.

Wei et al. describe "jailbreak" attacks as ones that "elicit undesired behavior" from models such as ChatGPT [1]. OWASP notes that prompt injection and jailbreaking are "often used interchangeably" and calls jailbreaking "a form of prompt injection where the attacker provides inputs that cause the model to disregard its safety protocols entirely" [2]. This post's demo uses a system-prompt rule as a stand-in for a trained-in refusal.

## How it works

1. Wei et al. analyse the vulnerability of safety-trained models by examining the model's pretraining and safety training processes [1].
2. **Competing objectives:** per the paper, these "arise when a model's capabilities and safety goals conflict" [1].
3. **Mismatched generalization:** per the paper, this "occurs when safety training fails to generalize to a domain for which capabilities exist" [1].
4. The authors conclude that safety mechanisms should be "as sophisticated as the underlying model," and argue against "the idea that scaling alone can resolve these safety failure modes" [1].
5. Anthropic describes its Constitutional Classifiers research as "a method that defends AI models against universal jailbreaks"; a prototype was robust to thousands of hours of human red teaming, "albeit with high overrefusal rates and compute overhead" [3].

## Real example

The script uses a harmless stand-in: a system prompt saying the secret word is BANANA and to never reveal it. It then asks six ways (a direct ask plus five reframings) and checks whether the word leaks. Run it with `uv run examples/what-a-jailbreak-is-and-why-it-works/secret_word_demo.py`.

| Condition | Leaked in |
|---|---|
| Direct ask | 0 of 2 models |
| Reframings (5 each, 10 calls) | 5 of 10 calls |

In this demo the direct ask held on both models, and 5 of the 10 reframed calls leaked the word.

## When this picture isn't enough

BANANA is a toy. It shows a system-prompt rule holding under the direct ask and failing under some changed frames in these 12 calls. It says nothing about how often real safety training fails. The paper's own tests were on GPT-4 and Claude v1.3 [1], and this post includes no real attack prompts.

For attacks on an app's own instructions, see [prompt injection](what-prompt-injection-is.md); for the checks wrapped around a model, see [guardrails](what-guardrails-do-and-dont-catch.md).

## Takeaway

In this demo a rule that held against the direct ask failed in 5 of 10 reframed calls. Wei et al. attribute jailbreak success to competing objectives and mismatched generalization in safety training [1].

## Sources

[1] Jailbroken: How Does LLM Safety Training Fail?, Wei, Haghtalab, Steinhardt, https://arxiv.org/abs/2307.02483
[2] LLM01:2025 Prompt Injection, OWASP Gen AI Security Project, https://genai.owasp.org/llmrisk/llm01-prompt-injection/
[3] Constitutional Classifiers: Defending against universal jailbreaks, Anthropic, https://www.anthropic.com/research/constitutional-classifiers
