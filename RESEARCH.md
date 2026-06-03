# Research grounding

This document lists the academic literature that grounds Code Crew's design and empirical claims. All arXiv links here were verified by direct lookup. The full literature synthesis that informed individual design decisions (with additional citations not all independently verified) lives at [`experiments/2026-06-01-dissent-ablation/RESEARCH_PERSONA_PROMPTING.md`](experiments/2026-06-01-dissent-ablation/RESEARCH_PERSONA_PROMPTING.md).

## Persona prompting (the central evidence base)

### Is "you are an X" prompting actually a free lift?

- **Zheng, M., Pei, J., Logeswaran, L., Lee, M., Jurgens, D.** (2023). *When "A Helpful Assistant" Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models.* [arXiv:2311.10054](https://arxiv.org/abs/2311.10054). EMNLP 2024.
  - Systematic test of 162 personas × 4 model families × 2,410 QA items. Adding a persona did **not** improve accuracy on average and usually slightly hurt it. Oracle best-persona-per-item did help, but automated selection performed no better than random — so even if the right named expert helps for a given input, you can't reliably pick it ex ante.

- **Hu, Z., Rostami, M., Thomason, J.** (2026). *Expert Personas Improve LLM Alignment but Damage Accuracy: Bootstrapping Intent-Based Persona Routing with PRISM.* [arXiv:2603.18507](https://arxiv.org/abs/2603.18507).
  - Shows the dose-response: MMLU accuracy drops as personas lengthen (71.6% → 68.0% → 66.3%). Expert personas improve alignment-style judgments but degrade closed-form reasoning tasks. **Code review is closed-form on bug-finding and open-form on taste; PRISM's curve predicts the accuracy tax we measured.**

- **Luz de Araujo, P. H., Röttger, P., Hovy, D., Roth, B.** (2025). *Principled Personas: Defining and Measuring the Intended Effects of Persona Prompting on Task Performance.* [arXiv:2508.19764](https://arxiv.org/abs/2508.19764). EMNLP 2025.
  - Defines three desiderata for persona prompting: Expertise Advantage, Robustness, Fidelity. Across 9 LLMs × 27 tasks: expert personas produce only small, non-significant positive changes — and **irrelevant biographical attributes (like swapping a first name) can drop performance by up to ~30 percentage points.** This is the load-bearing citation behind Code Crew's "do not name the person directly in the lead" decision (see [`runs/framing/SUMMARY.md`](experiments/2026-06-01-dissent-ablation/runs/framing/SUMMARY.md)).

### Where role-play prompting *does* help

- **Kong, A., Zhao, S., Chen, H., et al.** (2023). *Better Zero-Shot Reasoning with Role-Play Prompting.* [arXiv:2308.07702](https://arxiv.org/abs/2308.07702). NAACL 2024.
  - Two-stage role-setting + role-feedback approach. Large gains on 12 reasoning benchmarks — but used **generic functional roles** ("an excellent math teacher," "a recorder"), not named historical figures. The role-as-method framing carried the lift, not the name.

- **Salewski, L., Alaniz, S., Rio-Torto, I., Schulz, E., Akata, Z.** (2023). *In-Context Impersonation Reveals Large Language Models' Strengths and Biases.* [arXiv:2305.14930](https://arxiv.org/abs/2305.14930). NeurIPS 2023.
  - Domain-expert impersonation outperforms non-domain-expert impersonation on MMLU and fine-grained vision-language tasks. Confirms domain *match* in the role matters; doesn't isolate name vs. role.

- **Xu, B., Yang, A., Lin, J., et al.** (2023). *ExpertPrompting: Instructing Large Language Models to be Distinguished Experts.* [arXiv:2305.14688](https://arxiv.org/abs/2305.14688).
  - Auto-generates a detailed expert identity description per instruction. Higher quality (GPT-4 judged), and the gain comes from **long, task-tailored expert descriptions** — not from sticking a fixed celebrity name in.

### Persona prompting can hurt — and how to mitigate it

- **Kim, J., Yang, N., Jung, K.** (2024). *Persona is a Double-edged Sword: Mitigating the Negative Impact of Role-playing Prompts in Zero-shot Reasoning Tasks.* [arXiv:2408.08631](https://arxiv.org/abs/2408.08631).
  - Role-playing prompts **degrade reasoning on 7/12 datasets for Llama-3** and 4/12 for GPT-4. Proposes "Jekyll-&-Hyde": run both persona and neutral prompts, then have an LLM evaluator pick. LLM-generated personas were more stable than handcrafted ones.

- **Deshpande, A., Murahari, V., Rajpurohit, T., Kalyan, A., Narasimhan, K.** (2023). *Toxicity in ChatGPT: Analyzing Persona-assigned Language Models.* [arXiv:2304.05335](https://arxiv.org/abs/2304.05335). EMNLP 2023.
  - Assigning ChatGPT a persona increases toxic-generation rates by up to 6×, with bias targeted at specific entities/groups. Persona richness is correlated with off-profile fabrication, which is the mechanism behind the fabrication delta we measured in the framing A/B.

## Multi-agent / multi-persona ensembles

- **Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., Mordatch, I.** (2023). *Improving Factuality and Reasoning in Language Models through Multiagent Debate.* [arXiv:2305.14325](https://arxiv.org/abs/2305.14325).
  - Canonical Multi-Agent Debate paper. Multiple LLM instances debate over multiple rounds; lifts on factuality and reasoning. Key finding: the lift comes from independent agent starting points, not from labelling them as "experts."

- **Liang, T., He, Z., Jiao, W., et al.** (2023). *Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate.* [arXiv:2305.19118](https://arxiv.org/abs/2305.19118). EMNLP 2024.
  - Names the dominant single-agent failure mode: **Degeneration-of-Thought (DoT)** — once an LLM has committed, self-reflection won't generate novel paths; external pressure from a differently-positioned agent is what breaks it. Directly motivates Code Crew's "independent blind passes" hard gate.

- **Wang, X., Wei, J., Schuurmans, D., et al.** (2022). *Self-Consistency Improves Chain of Thought Reasoning in Language Models.* [arXiv:2203.11171](https://arxiv.org/abs/2203.11171). ICLR 2023.
  - The cheap baseline every multi-agent design has to beat. +17.9pp on GSM8K, +12.2pp on AQuA — using no personas. Sampling N CoT traces and majority-voting often outperforms more elaborate multi-agent setups without tuning.

## Our experimental results (cite these papers when explaining the empirical claims)

| Code Crew finding | Grounded by |
|---|---|
| K+H+T (a 3-persona crew with multi-pass) beats naive single Claude on PR review recall | Du et al. (multi-agent debate), Liang et al. (DoT), Wang et al. (must beat self-consistency baseline) |
| Adding personas to K+H+T degrades synthesis (sextet does worse than the triple) | Smit et al. on MAD overhead (in synthesis doc), Liang et al. on coordination cost when agents are not heterogeneous |
| Named archetypes don't improve recall over generic numbered reviewers (Δ ≈ 0) | Zheng et al. (personas don't help on average), Kong et al. (role/method carries the lift, not the name) |
| Direct-naming briefs ("X — author of TAOCP...") underperformed archetype-inspired briefs | Luz de Araujo et al. (irrelevant attributes destabilize), Hu et al. (PRISM dose-response on accuracy), Deshpande et al. (richer profiles → more fabrication) |
| Verifier between blind passes and synthesis (mandatory) | Standard self-consistency + Jekyll-&-Hyde pattern (Kim et al.); the rubric is novel to this project |

## How to read the experiments through this lens

- The **persona ablation** (n=50, K+H+T vs the sextet vs solo personas vs generic-6) replicates Zheng et al.'s "personas don't help on average" finding for the named-vs-generic comparison: Δ recall = 0.000, p = 0.50. See [`experiments/2026-06-01-dissent-ablation/runs/personas/SUMMARY.md`](experiments/2026-06-01-dissent-ablation/runs/personas/SUMMARY.md).

- The **framing A/B** (n=50, direct-named vs archetype-inspired) replicates the Luz de Araujo / PRISM / Deshpande triad: direct-named recall −3.9pp (p=0.039 one-sided A>B; p=0.078 two-sided), precision −3.5pp (p=0.013 one-sided A>B; p=0.027 two-sided), fabrication +9.9pp (not significant). See [`experiments/2026-06-01-dissent-ablation/runs/framing/SUMMARY.md`](experiments/2026-06-01-dissent-ablation/runs/framing/SUMMARY.md).

- The **triple search** (10 of C(6,3) triples on n≈41 each) supports Liang et al.'s heterogeneity claim: triples without a pragmatic-axis member (Torvalds) or with two overlapping architectural lenses (Liskov + Pike) cluster near the bottom. See [`experiments/2026-06-01-dissent-ablation/runs/triples/SUMMARY.md`](experiments/2026-06-01-dissent-ablation/runs/triples/SUMMARY.md).

## Gaps and honest uncertainty

1. **No paper runs the clean "You are Knuth" vs "You are a rigorous algorithm analyst" controlled ablation.** Code Crew's framing A/B is the closest in-domain replication we have.
2. **PersonaEval-style work caps LLM-as-judge reliability on persona fidelity at ~69%.** We use external diff-level outcomes (judged recall against human reviewer comments), which dodges the persona-fidelity-as-metric problem entirely.
3. **The Code Crew judge is Claude.** Anonymized + skeptic-framed, but Claude judging Claude has a residual self-preference vector that we have not eliminated. The relative comparisons across arms hold (same judge across arms), but absolute fabrication rates may be inflated or deflated.

## Other references cited in the project's literature syntheses

The fuller workflow-generated literature synthesis ([`experiments/2026-06-01-dissent-ablation/RESEARCH_PERSONA_PROMPTING.md`](experiments/2026-06-01-dissent-ablation/RESEARCH_PERSONA_PROMPTING.md)) cites additional papers including Hu & Collier ("Quantifying the Persona Effect", ACL 2024, arXiv:2402.10811), Tseng et al. ("Two Tales of Persona in LLMs", EMNLP Findings 2024, arXiv:2406.01171), Smit et al. ("Should we be going MAD?", ICML 2024), Chan et al. ("ChatEval", arXiv:2308.07201, ICLR 2024), and a handful of more recent papers on persona-induced fabrication. Those arXiv IDs and venues were generated by an LLM literature-survey workflow and have not all been independently verified by the maintainers of this repository. The papers cited in *this* document have all been verified by direct arXiv lookup; treat them as the canonical reference set.
