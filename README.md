# Quiet Echoes

**A 512-bit search for cleaner signals.** Submit one small text file. The checker measures the exact total energy of its aperiodic autocorrelation sidelobes.

This is an adopted Science Ladder challenge candidate awaiting hosted review and conformance. Its baseline is a real, attributed published sequence, reproduced locally at **E = 17,996**, with merit factor **7.2833963103** and peak sidelobe **32**. Every milestone requires a lower energy. MatBalez authorized creator adoption through Codex, recorded in [the adoption statement](docs/creator-adoption.md). No new record, passing hosted acceptance or independent replication is claimed by this repository.

Open [visualize.html](visualize.html) to explore the reference pulse, sidelobes and spectrum, or load a candidate file. All displayed measurements are calculated from the selected data. The visual explorer is an educational local preview; only the platform checker can issue a platform verification receipt.

Read [the scientific brief](challenge-brief.md), [the Scout comparison](docs/scout-verdict.md), and [the verification plan](harness-plan.md).

## Artifact

One file named `sequence.txt`, containing exactly 512 ASCII `+` or `-` characters followed by one LF. No spaces, other files, archives or executable code. `+` means +1; `-` means −1.

The reference is in `fixtures/baseline/sequence.txt`. `fixtures/valid/sequence.txt` is an independently generated Rudin–Shapiro comparison, with E = 43,776; it is valid but does not beat the baseline.

## Reproduce locally

Python 3.13 or newer, standard library only:

```sh
python3 tools/reproduce.py --check
python3 -m unittest discover -s tests -v
mkdir -p .local
python3 checker.py --submission fixtures/baseline --suite suite --output .local/result.json
```

The checker refuses to overwrite an existing result; remove your previous local output or choose a fresh path when repeating that last command.

With the Science Ladder CLI:

```sh
sl candidate lint science-ladder-candidate.yaml
sl challenge lint science-ladder.yaml
sl challenge test --manifest science-ladder.yaml --unsafe-local
```

The local container path uses the exact runtime digest in the manifest. It now pins the published patched runtime `sha256:a8136bf6f5082a72776f2565f279a6c336b462da483aa54cfa81586ad20705fa`. Local checks against that image are recorded separately from the historical reports. Actual hosted vulnerability-policy checks, scientific review and machine preflight must still pass before publication.

## Research and contributions

The frozen mathematical task is unrestricted LABS at length 512: no enforced balance, skew-symmetry, periodic wraparound or peak-sidelobe objective. Search can use any lawful method and compute; the submitted artifact remains data only.

A sequence may pass validation without improving the baseline. Reproductions and symmetry-equivalent sequences are welcome as accurately labeled checks, but cannot earn improvement milestones. Report methods, compute and provenance in accompanying public notes; do not add those notes to the one-file artifact.

[MIT](LICENSE) covers first-party software and documentation. The published baseline retains [CC BY 4.0 attribution](THIRD_PARTY_NOTICES.md). Submitted sequence data use CC BY 4.0. No payments or rewards are part of this draft.
