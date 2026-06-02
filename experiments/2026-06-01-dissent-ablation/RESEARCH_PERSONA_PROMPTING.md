# Persona Prompting Research Scan

Conducted 2026-06-02 as part of the framing ablation. Four parallel literature surveys synthesized by a fifth agent.

## TL;DR Recommendation

**Keep the "reasoning archetype inspired by X" framing. Do not switch to "Named person — accomplishments".**

Three converging evidence strands:

- **Principled Personas (Luz de Araujo et al., EMNLP 2025)**: irrelevant surface attributes including names can swing performance by ~30pp.
- **PRISM (arXiv:2603.18507)**: accomplishment lists add tokens without lifting accuracy and degrade closed-form work (MMLU 71.6 → 68.0 → 66.3 as personas lengthen).
- **Fabrication research (Deshpande et al. EMNLP 2023; Sadeq et al.; TimeChara ACL 2024; IMPersona)**: richer real-person profiles *increase* confident off-profile fabrication and can multiply toxicity up to 6×.

## Full Synthesis

## 1. What the empirical research says about persona prompting effects on task quality

The evidence base is now large enough to give a clear verdict: **persona prompting is not a free accuracy lift, and is often a small net loss on closed-form/factual work.** Zheng et al.'s 162-persona, 4-model, 2,410-item sweep ("When 'A Helpful Assistant' Is Not Really Helpful," EMNLP 2024) found no average gain from adding a persona, and crucially showed that *oracle* best-per-question selection does help — but *automated* persona selection performs no better than random. Luz de Araujo et al.'s "Principled Personas" (EMNLP 2025) is the strongest direct evidence on framing: across 9 SOTA models and 27 tasks, expert personas produce only small/non-significant positive changes, while **irrelevant attributes — including a swapped first name — can drop performance by up to ~30 percentage points.** The PRISM paper (arXiv:2603.18507) shows the dose-response: MMLU dropped from 71.6% → 68.0% with a minimal persona and → 66.3% with a long one.

Where persona prompting *does* lift quality is narrower than folklore suggests: subjective/alignment-style writing, structurally distinct multi-agent debate (Du et al., ICML 2024), and **long, auto-tailored expert descriptions** matched to the task (ExpertPrompting, Xu et al. 2023). Salewski et al. (NeurIPS 2023) confirm domain *match* in the role matters; Kong et al.'s "Better Zero-Shot Reasoning with Role-Play Prompting" (NAACL 2024) got large GSM-family gains — but with **generic functional roles ("an excellent math teacher"), not named historical figures.** Hu & Collier (ACL 2024) bound the effect: persona variables explain <10% of variance in simulation tasks. Net: the *role description* carries the lift; the *name* mostly carries variance.

## 2. What the research says about multi-persona / multi-agent setups

For a 3-persona crew the relevant findings are sharper. Liang et al.'s MAD (EMNLP 2024) names the dominant failure mode — **Degeneration-of-Thought**: once a single LLM commits, self-reflection won't generate novel paths; external pressure from a *differently-positioned* agent is what breaks it. Dynamic role assignment outperforms uniform assignment by **up to 74.8%** in MAD ablations, and ChatEval (Chan et al., ICLR 2024) shows functionally-distinct named personas materially raise correlation with human judgment vs same-role debate.

Two skeptical results discipline the design: Smit et al.'s "Should we be going MAD?" (ICML 2024) found **debate does not reliably beat self-consistency or simple ensembling without tuning** (agreement-modulation in particular), and Wang et al.'s self-consistency (ICLR 2023) remains a cheap, hard baseline (+17.9 GSM8K, +12.2 AQuA) using no personas at all. Recent 2026 scaling work suggests **2-3 diverse agents ≈ 16 homogeneous ones**, with coordination overhead overtaking benefit once base accuracy passes ~45%. Three is at or near the sweet spot — *if the three are genuinely heterogeneous*. Naik et al.'s "Diversity of Thought" gives the one published green light for historical-figure personas — but uses them explicitly as a *diversity-injection lever*, not as authority.

## 3. Best practices for a 3-persona code-review crew

1. **Lead each persona with reasoning method, not credentials.** OpenAI's prompt guidance and Mollick converge here; PRISM and Principled Personas give the empirical backing. Knuth = "exact analysis, literate exposition, suspicious of unmeasured optimization"; Hickey = "decomplect; data > objects; simplicity as an objective property"; Torvalds = "pragmatic taste; brutal directness on architectural choices."
2. **Run independent blind passes before debate.** Matches MAD/Liang findings and avoids Degeneration-of-Thought. Already in the council protocol.
3. **Keep one persona-free neutral pass as a tiebreaker.** Kim/Lee et al.'s "Persona is a Double-edged Sword" (arXiv:2408.08631) shows role-play degrades reasoning on 7/12 datasets in Llama-3 and flips 13.78% of items; their Jekyll-&-Hyde ensemble fix is well-attested.
4. **Benchmark against self-consistency CoT on real review tasks.** If the crew doesn't beat majority-voted CoT, the personas are decoration (Smit et al., Wang et al.).
5. **Use agreement-modulation.** Instruct personas to disagree on round 1 and converge only on evidence; premature consensus is the modal failure.
6. **Add 2-4 behavioral anchors per persona** (how this archetype phrases a critique, refusal, trade-off). Persona-vector work suggests short anchors are surprisingly effective; Comet/Nautilus document drift mitigation.
7. **System-prompt the persona; user-prompt the diff.** Standard Anthropic/OpenAI/Willison guidance; keeps the persona auditable and stable.

## 4. Recommendation: archetype-inspired or directly named?

**Keep the "reasoning archetype inspired by X" framing. Do not switch to "Named person — accomplishment 1, accomplishment 2, …"**

Three converging strands of evidence support this:

- **Principled Personas (Luz de Araujo et al., EMNLP 2025)** is the closest controlled test: irrelevant surface attributes including names can swing performance by ~30pp. A direct "Donald Knuth — author of TAOCP, invented TeX, …" header front-loads exactly the high-variance surface attributes that destabilize the model.
- **PRISM (arXiv:2603.18507)** shows accomplishment lists *add tokens without lifting accuracy and degrade closed-form work* (71.6 → 68.0 → 66.3% on MMLU as personas lengthen). For code review — which is closed-form on bug-finding and open-form on taste — the accomplishment framing pays a measurable closed-form tax.
- **Fabrication evidence (Deshpande et al. EMNLP 2023; Sadeq et al. arXiv:2406.17260; TimeChara, ACL 2024; IMPersona arXiv:2504.04332)** shows richer real-person profiles *increase* confident off-profile fabrication (invented quotes, anecdotes, "Knuth would say…") and toxicity up to 6×. Kong/Lee's double-edged sword paper independently confirms the reasoning hit. Your existing CLAUDE.md non-impersonation rule is well-aligned; the directly-named framing erodes it.

What Kong et al.'s NAACL 2024 result and ExpertPrompting *do* support is the part the current briefs already do well: long, method-rich role descriptions outperform short labels. So the upgrade path is **deeper method/anchor content under the archetype frame**, not flipping to a name-and-laurels header.

## 5. Three pitfalls for the K+H+T design (with mitigations)

1. **Premature convergence / Degeneration-of-Thought.** Three personas with the same base model and overlapping training data will agree fast and look like consensus. *Mitigation:* mandate independent blind passes first (Du et al., Liang et al.), explicit round-1 disagreement instruction, and agreement-modulation tuning (Smit et al.).
2. **Confident quote/anecdote fabrication under the named-real-person surface.** Even with the archetype disclaimer, model priors will leak ("Knuth famously said…"). *Mitigation:* in-file rule — "never invent quotes, anecdotes, or first-person claims; speak in third person about the archetype's method"; add a behavioral anchor demonstrating the third-person move; keep accomplishment lists out of the brief (PRISM, Sadeq et al., TimeChara).
3. **No baseline — the crew can't prove it's earning its tokens.** Smit et al. and Wang et al. show MAD often loses to self-consistency CoT untuned. *Mitigation:* build a tiny eval harness (10-20 real diffs with known issues) and require the crew to beat (a) single-pass CoT and (b) self-consistency majority vote on bug-finding precision/recall before shipping any persona change.

**Honest gaps:** no paper runs a clean "You are Knuth" vs "You are a rigorous algorithm analyst" controlled ablation; the named-person → quote-fabrication dose-response is mechanistically supported (Deshpande, Sadeq, GDELT-style detail hallucination) but not directly benchmarked; PersonaEval (arXiv:2508.10014) caps LLM-judge reliability at ~69%, meaning self-evaluation of the crew's persona fidelity is itself unreliable — use external diff-level outcomes, not persona-fidelity scores, as the metric.