# Wavefront solver methods

Two independently generated data artifacts target the frozen Quiet Echoes LABS512 contract. These are assistant-generated local candidate attempts, not independent scientific review, platform verification, independent replication, or novelty claims. The known reference energy 17,996 is used only to contextualize the final score, never as a seed.

## Seeded random multistart tabu search

`src/search.cpp random` uses an explicitly implemented SplitMix64 generator with seed 2026090401. Every restart samples all 512 signs independently from generator bits. The search evaluates every one-bit flip using the exact change in the full aperiodic energy. It selects the lowest-energy admissible neighbor, breaking ties through the seeded generator. Tabu tenure is 34–85 steps; a move beating the global best is permitted by aspiration. Positive-energy moves are allowed to leave local minima. The final run planned 512 restarts of 3,200 moves each and was stopped at its 540-second wall-time cap. Its best-so-far energy was 26,964, found at zero-based restart 45, step 2,895 after 75,210,240 neighbor evaluations. No later improvement was recorded. The exact total number of evaluations before the cap is unknown. A separate 46 × 3,200 winning-prefix replay reproduces the selected artifact byte for byte. A shorter 64 × 1,600 calibration run was performed first.

The implementation updates every correlation after each accepted flip, checks against direct recomputation every 128 steps, and independently recomputes every new global best. At startup it checks all 512 one-flip deltas on a deterministic vector and checks 100 subsequent correlation updates. Search arithmetic is integer-only. The wall-time cap limits how much of the planned search is completed. Each fixed-length prefix remains deterministic; energy itself depends only on artifact bytes.

## Structured quadratic-residue construction

`src/search.cpp structured` enumerates every rotation for every prime from 449 through 1,021, with both sign choices at residue zero. Nonzero quadratic residues map to +1 and nonresidues to −1. Repeating or truncating this periodic sign sequence gives exactly 512 signs. Every candidate is evaluated using the full *aperiodic* objective; this does not substitute a periodic correlation score.

The run evaluates 125,812 construction candidates and selects prime 491, rotation 360, and zero sign +1, with E = 20,604. The whole search was repeated and reproduced the identical file. `src/reproduce_structured.py` reconstructs that selected member directly, using only Python's standard library.

Legendre-sequence construction is established background, also discussed in Section 4.1 of [Pšeničnik et al.](https://arxiv.org/html/2409.07222v1). This implementation does not copy the authors' solver or use their published sequence. It claims no new construction theorem or record. The entire finite family enumerated here is much smaller than the unrestricted 2^512 search space.

## Artifact and verification boundaries

Each artifact directory contains only `sequence.txt`: exactly 512 ASCII `+` (U+002B) or `-` (U+002D) characters followed by LF. Search code, methods and provenance remain outside those directories. The official challenge checker and final pinned local container independently evaluate the final files. All receipts here are explicitly local and unsigned.

A candidate can be valid yet fail to improve the reference. In particular, the structured candidate has a smaller peak sidelobe than the literature reference while having worse total energy. That is a diagnostic tradeoff, not a win on this challenge's objective.
