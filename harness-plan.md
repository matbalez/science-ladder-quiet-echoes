# Verification plan

The checker consumes `/sl/submission/sequence.txt` and the frozen public `/sl/suite/contract.json`. Source lives at `/sl/challenge`; temporary storage, if needed by the runner, is `/sl/work`. It writes exactly one `/sl/output/result.json` with the protocol's four fields: apiVersion, kind, decimal-string score and the complete gate map. It never executes submitted code or returns submitted text as diagnostics.

The entrypoint is direct Python argv. The dependency lock declares no third-party packages. Scientific scoring uses integer arithmetic exclusively; canonical ASCII serialization eliminates number parsing, duplicate keys, exponent notation, NaN, infinities and Unicode ambiguity. The result contains no duration or environment-derived score.

## Public fixtures

| Fixture | Expected local outcome | Score when valid |
| --- | --- | ---: |
| baseline | valid | 17,996 |
| valid | valid, Rudin–Shapiro comparison | 43,776 |
| invalid | hard_gate_failed, nonbinary sign | — |
| malformed | invalid_output, forbidden artifact filename | — |
| empty | hard_gate_failed | — |
| oversized | invalid_output before execution | — |
| maximum | valid, all equal signs | 44,608,256 |

Unit tests also cover wrong lengths, CRLF, missing final LF, extra entries, nested paths, symlinks, hardlinks, FIFO files, sparse oversized files, executable-looking text, duplicate-key JSON, very large numeric strings, modified public suite contracts and refusing to overwrite old output. The platform rejects malformed artifact structure before execution. Invalid contents at the canonical path, including empty or non-ASCII data, produce failed hard gates. Genuine checker errors remain challenge faults. An initial conformance run caught this distinction; its failed report is retained.

An independent XOR/Hamming-distance implementation cross-checks all binary strings through length eight and 25 deterministic full-size vectors. The test suite checks all eight standard sign/reversal/alternation symmetries and verifies that a cyclic shift is not silently treated as an aperiodic symmetry. Four fresh checker processes must produce identical result bytes for the reference.

The scorer has a fixed workload of 130,816 sign products. No valid 513-byte artifact intentionally stalls it. Timeout behavior is therefore exercised separately using a deliberately stalled trusted local test process killed by the test harness. That is a local cleanup test, not an adversarial input accepted by the checker and not proof of Firecracker's resource isolation. Hosted preflight must exercise the real runner's timeout and memory enforcement.

## Sandbox and resource contract

The draft requests one CPU, 128 MiB, a five-second execution timeout and at most 4,096 output bytes. Official execution belongs in the platform's isolated verification plane. A local Docker run uses no network, a read-only root and input mounts, dropped capabilities, no new privileges, a non-root UID, bounded process/file resources and scratch mounts. The manifest pins the published patched runtime `sha256:a8136bf6f5082a72776f2565f279a6c336b462da483aa54cfa81586ad20705fa`. Actual hosted vulnerability-policy evaluation and preflight remain required: local execution is opt-in and cannot approve the runtime. The verification policy is explicitly platform, requiring fresh isolated repeats on one enrolled host; independent physical-host replication is a separate state.

The suite is fully public. There are no hidden cases, secrets, model judges or datasets to leak. Hard-coding a known sequence only reproduces its true energy. Hard-coding a claimed score is ineffective because the checker ignores all purported result data. Symmetry-equivalent sequences have equal E and cannot earn a strict improvement. Extra metadata belongs in external submission notes, never in the artifact.

## Commands and recorded evidence

```sh
python3 tools/reproduce.py --check
python3 -m unittest discover -s tests -v
sl candidate lint science-ladder-candidate.yaml
sl challenge lint science-ladder.yaml
sl challenge test --manifest science-ladder.yaml --unsafe-local
```

`reports/` records what actually ran and its environment. Host and clean Linux-container tests are local evidence. A passing schema or local fixture report is not a creator adoption, reproducible hosted build, platform verification receipt or independent replication result.

The creator adoption and rights statement is recorded in `docs/creator-adoption.md` under MatBalez’s explicit authorization. Real preflight must still bind the final committed source, independently resolve its scientific evidence, evaluate the pinned runtime policy, and execute all fixtures. Changes to the checker, score, suite, baseline or thresholds after lock require the platform's versioning process.
