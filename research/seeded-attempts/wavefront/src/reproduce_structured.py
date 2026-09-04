#!/usr/bin/env python3
"""MIT. Reproduce the selected Legendre-family candidate without running a search."""
from pathlib import Path
import argparse


def construct(prime=491, rotation=360, zero_sign=1):
    if prime < 2 or any(prime % d == 0 for d in range(2, int(prime**0.5)+1)):
        raise ValueError("prime parameter must be prime")
    if zero_sign not in (-1,1):raise ValueError("zero sign must be -1 or1")
    residues={x*x%prime for x in range(1,prime)}
    signs=[zero_sign if (i+rotation)%prime==0 else 1 if (i+rotation)%prime in residues else -1 for i in range(512)]
    return (''.join('+' if x==1 else '-' for x in signs)+'\n').encode('ascii')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    with args.output.open('xb') as out:out.write(construct())
