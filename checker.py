#!/usr/bin/env python3
"""Quiet Echoes: exact data-only LABS512 checker. First-party code: MIT."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys

LENGTH = 512
MAX_BYTES = LENGTH + 1
MAX_ENERGY = (LENGTH - 1) * LENGTH * (2 * LENGTH - 1) // 6
GATES = ("one_canonical_sequence", "binary_length_512")


class ArtifactError(ValueError):
    """Malformed transport or filesystem; never emit a score."""


def correlations(sequence: tuple[int, ...]) -> tuple[int, ...]:
    """Aperiodic C_k for k=1..N-1; Python integer arithmetic only."""
    return tuple(
        sum(sequence[i] * sequence[i + lag] for i in range(len(sequence) - lag))
        for lag in range(1, len(sequence))
    )


def energy(sequence: tuple[int, ...]) -> int:
    return sum(value * value for value in correlations(sequence))


def read_artifact(root: Path) -> bytes:
    # Open the immutable mount itself without following a final symlink, then all
    # payloads relative to that descriptor. Never open arbitrary submitted paths.
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory = os.open(root, flags)
    try:
        if sorted(os.listdir(directory)) != ["sequence.txt"]:
            raise ArtifactError("artifact must contain only sequence.txt")
        fd = os.open("sequence.txt", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ArtifactError("payload must be one regular file, without links")
            if not 0 <= info.st_size <= MAX_BYTES:
                raise ArtifactError("payload must contain at most513 bytes")
            data = os.read(fd, MAX_BYTES + 1)
            if len(data) != info.st_size or len(data) > MAX_BYTES:
                raise ArtifactError("payload changed or exceeds byte limit")
            return data
        finally:
            os.close(fd)
    except OSError as error:
        raise ArtifactError("unreadable or non-regular artifact") from error
    finally:
        os.close(directory)


def parse_sequence(data: bytes) -> tuple[tuple[int, ...] | None, dict[str, bool]]:
    # A single ASCII encoding avoids JSON numbers, exponents, NaN, duplicate keys,
    # Unicode confusables, and multiple equivalent whitespace representations.
    canonical = len(data) == MAX_BYTES and data[-1:] == b"\n" and b"\n" not in data[:-1]
    binary = canonical and all(byte in (43, 45) for byte in data[:-1])
    gates = {GATES[0]: canonical, GATES[1]: binary}
    if not binary:
        return None, gates
    return tuple(1 if byte == 43 else -1 for byte in data[:-1]), gates


def verify_suite(root: Path) -> None:
    # The public suite locks the scientific contract, not precomputed answers.
    path = root / "contract.json"
    data = path.read_bytes()
    if len(data) > 1024:
        raise ArtifactError("invalid suite contract")
    expected = b'{"contract":"quiet-echoes-labs512-v1","length":512,"correlation":"aperiodic","objective":"sum-squared-nonzero-lags"}\n'
    if data != expected:
        raise ArtifactError("suite contract does not match checker")


def evaluate(root: Path, suite: Path) -> dict:
    verify_suite(suite)
    sequence, gates = parse_sequence(read_artifact(root))
    score = energy(sequence) if sequence is not None else MAX_ENERGY
    return {"apiVersion": "science-ladder/v1", "kind": "ValidatorResult", "score": str(score), "gates": gates}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission", type=Path, default=Path("/sl/submission"))
    parser.add_argument("--suite", type=Path, default=Path("/sl/suite"))
    parser.add_argument("--output", type=Path, default=Path("/sl/output/result.json"))
    args = parser.parse_args()
    try:
        result = evaluate(args.submission, args.suite)
    except (ArtifactError, OSError):
        # No attacker data or traceback is echoed. The runner marks invalid_output.
        print("artifact or public suite failed structural validation", file=sys.stderr)
        return 2
    output = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"
    # The runner provides an empty writable output directory. Exactly one regular
    # result is produced; no pictures, extra files, external accesses or solver code.
    with args.output.open("xb") as handle:
        handle.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
