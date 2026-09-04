# SPDX-License-Identifier: MIT
"""Independent integer XOR/Hamming-distance verification of a LABS512 artifact."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('artifact', type=Path)
args = parser.parse_args()
data = (args.artifact / 'sequence.txt').read_bytes()
assert set(p.name for p in args.artifact.iterdir()) == {'sequence.txt'}
assert len(data) == 513 and data[-1:] == b'\n' and set(data[:-1]) <= {43, 45}
# A bit and its k-shift differ precisely when the corresponding signs differ.
bits = sum((symbol == 43) << i for i, symbol in enumerate(data[:-1]))
correlations = [512-k-2*((bits ^ (bits >> k)) & ((1 << (512-k))-1)).bit_count() for k in range(1,512)]
energy = sum(value*value for value in correlations)
print(json.dumps({'length': 512, 'energy': energy, 'meritFactor': 512*512/(2*energy),
                  'peakSidelobe': max(map(abs,correlations)), 'sha256': hashlib.sha256(data).hexdigest(),
                  'method': 'integer XOR/Hamming-distance aperiodic correlation'}, indent=2))
