#!/usr/bin/env python3
"""Reproduce the attributed literature baseline; never searches for new solves."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from checker import correlations, energy
ROOT=Path(__file__).resolve().parents[1]


def decode_hex(value: str, length: int = 512) -> tuple[int, ...]:
    bits=bin(int(value,16))[2:].zfill(length)
    if len(bits)!=length: raise ValueError("reference length mismatch")
    return tuple(1 if b=="1" else -1 for b in bits)


def rudin_shapiro(length: int = 512) -> tuple[int, ...]:
    # a_n=(-1)^(number of overlapping 11 pairs in the binary expansion of n).
    return tuple(-1 if (n & (n>>1)).bit_count()%2 else 1 for n in range(length))


def data(sequence: tuple[int, ...]) -> bytes:
    return ("".join("+" if v==1 else "-" for v in sequence)+"\n").encode("ascii")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    reference=json.loads((ROOT/'literature/reference.json').read_text())
    sequence=decode_hex(reference['hex'])
    encoded=data(sequence)
    assert energy(sequence)==17996
    assert max(map(abs,correlations(sequence)))==32
    assert (ROOT/'fixtures/baseline/sequence.txt').read_bytes()==encoded
    if args.check:
        print("baseline bytes, exact energy17996 and peak sidelobe32 verified")
        return
    report={'kind':'LocalReferenceReproduction','official':False,'reference':reference['source'],'length':len(sequence),'scoreTicks':str(energy(sequence)),'meritFactorNumerator':str(len(sequence)**2),'meritFactorDenominator':str(2*energy(sequence)),'peakSidelobe':max(map(abs,correlations(sequence))),'sequenceSha256':hashlib.sha256(encoded).hexdigest(),'comparison':{'name':'Rudin–Shapiro construction','energy':energy(rudin_shapiro())},'claim':'Reproduction of published data. No new sequence, official receipt or optimality proof.'}
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
