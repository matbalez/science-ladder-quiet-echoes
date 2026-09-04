# SPDX-License-Identifier: MIT
"""Reproduce the recorded independent stochastic search; requires C++17 clang++."""
import argparse
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--work', type=Path, required=True)
parser.add_argument('--seed', type=int, required=True)
parser.add_argument('--iterations', type=int, required=True)
args = parser.parse_args()
args.work.mkdir(parents=True, exist_ok=True)
binary = args.work.resolve() / 'search'
subprocess.run(['clang++', '-O3', '-std=c++17', '-DNDEBUG', str(root/'search.cpp'), '-o', str(binary)], check=True)
subprocess.run([str(binary), str(args.seed), str(args.iterations), str(args.work.resolve()/'candidate')], check=True)
