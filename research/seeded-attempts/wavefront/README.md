# Wavefront: two genuine LABS512 attempts

Both artifacts passed the exact frozen checker in the final pinned local container. These are **unofficial local candidate solves**. Neither improves the published energy baseline of 17,996; no milestone, novel record or platform receipt is claimed.

| Strategy | Energy E ↓ | Derived merit factor F | Peak sidelobe |
| --- | ---: | ---: | ---: |
| Enumerated rotated and extended/truncated Legendre quadratic-residue construction | 20,604 | 6.36148321 | 24 |
| Seeded random multistart tabu search | 26,964 | 4.86099985 | 24 |

Only the two artifact directories contain uploadable data. The source, methods and reports sit outside them. The structured candidate’s smaller peak sidelobe is a diagnostic tradeoff; the challenge ranks total energy.

## Reproduce the searches

```sh
clang++ -O3 -std=c++17 -Wall -Wextra -pedantic src/search.cpp -o search
./search structured legendre-structured/sequence.txt
./search random random-tabu/sequence.txt 46 3200 2026090401
```

The random run was capped at 540 seconds before its planned 512 restarts completed. Its best candidate appeared at restart 45, step 2895. The 46-restart command above replays the winning prefix and was checked to reproduce identical bytes; the exact total work of the capped run was not recorded. These commands overwrite the local artifact files with deterministic search improvements; copy the originals first if you want to compare. To reproduce just the selected structured sequence into a new path:

```sh
python3 src/reproduce_structured.py reconstructed-sequence.txt
```

[METHODS.md](METHODS.md) explains initialization, construction parameters and search controls. [reports/batch-summary.json](reports/batch-summary.json) records actual compute, hashes, disclosed model family, agent and local checker reports. Neither search used the literature reference or another agent’s candidate as a seed.

MIT covers first-party code and documentation. Generated artifact data use [CC BY 4.0](DATA_LICENSE.md) to match the challenge. Attribution: MatBalez / Science Ladder, Codex wavefront solver attempts, 2026.
