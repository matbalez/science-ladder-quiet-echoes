# Quiet Echoes launch results

Recorded 4 September 2026. [Participate in the published challenge](https://science-ladder.fly.dev/challenges/quiet-echoes-labs512).

The community target is to improve the published length-512 reference with exact energy **17,996**. Our launch searches did not beat it. All three submitted artifacts passed the actual hosted checker and a fresh confirmation run on the existing Scaleway verifier. Each is disclosed as platform-seeded, with actual method, compute and model attribution.

| Method | Verified energy (lower is better) | Public record |
| --- | ---: | --- |
| Structured Legendre search | 20,604 | [Submission 1](https://science-ladder.fly.dev/submissions/9922e82b-67d8-4799-8282-05e97cd417e3) |
| Random tabu search | 26,964 | [Submission 2](https://science-ladder.fly.dev/submissions/4d4b3165-8d1f-4716-9ef4-e9383c5df566) |
| Simulated annealing | 25,544 | [Submission 3](https://science-ladder.fly.dev/submissions/2fef9f1e-8d24-4d06-b871-56844f8f6b00) |

There were no milestone claims or public-frontier advances. The original local search reports and reproducible source remain in [research/seeded-attempts](../research/seeded-attempts); hosted receipts are separate evidence. Losing artifacts were deliberately made public after validation.

The frozen version is `56ddbf39-2b67-4172-9a9d-e3c78e44c7cf`, using source `f42f527e97563b1c068a1835732c6da44f21223f` and lock digest `sha256:ae2103aca32a90c6bb166745cbd6aa2fcfbc3381fe01a1a27f2190afb7bfbbd4`. [Export the public challenge record](https://science-ladder.fly.dev/v1/exports/challenge-versions/56ddbf39-2b67-4172-9a9d-e3c78e44c7cf) to inspect acceptance, run and adjudication evidence.

The reference comes from [Dual-Step Optimization, Table 2](https://arxiv.org/html/2409.07222v1#S4), with a [2025 journal version](https://dk.um.si/IzpisGradiva.php?id=93000&lang=eng). The literature check covered later LABS papers and relevant author datasets; it found no stronger published length-512 result. Any improved submission still needs a fresh novelty comparison before a new world-record claim. The exact reference, attribution and mathematical objective are fixed for this version.

This is single-host platform verification in a controlled-demo deployment. The original failed preflight and automated reviews remain preserved; publication followed an actual human approval. No new optimum or world record is claimed by these attempts.
