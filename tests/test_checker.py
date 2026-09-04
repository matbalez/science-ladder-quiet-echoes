"""Adversarial and independent mathematical checks. These are local tests."""
from __future__ import annotations
from contextlib import contextmanager
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from checker import ArtifactError, LENGTH, MAX_ENERGY, correlations, energy, evaluate, parse_sequence, read_artifact
from tools.reproduce import data, decode_hex, rudin_shapiro


def independent_correlations(sequence):
    # A Hamming-distance/XOR/popcount implementation, separate from the checker's
    # explicit products and sums. It is used as a mathematical cross-check only.
    number = int(''.join('1' if x == 1 else '0' for x in sequence),2)
    n = len(sequence)
    return tuple((n-k)-2*((number^(number>>k))&((1<<(n-k))-1)).bit_count() for k in range(1,n))


@contextmanager
def artifact(payload=b'+'*512+b'\n'):
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder)
        (root/'sequence.txt').write_bytes(payload)
        yield root


class MathematicsTests(unittest.TestCase):
    def test_reference_reproduces_exact_published_value(self):
        ref=json.loads((ROOT/'literature/reference.json').read_text())
        s=decode_hex(ref['hex'])
        self.assertEqual((ROOT/'fixtures/baseline/sequence.txt').read_bytes(),data(s))
        self.assertEqual(energy(s),17996)
        self.assertEqual(max(map(abs,correlations(s))),32)
        self.assertEqual(512**2/(2*energy(s)),7.283396310291176)
        self.assertEqual(correlations(s),independent_correlations(s))

    def test_independent_implementations_exhaustive_small_instances(self):
        for n in range(1,9):
            for s in itertools.product((-1,1),repeat=n):
                self.assertEqual(correlations(s),independent_correlations(s))

    def test_full_size_deterministic_vectors(self):
        generator=random.Random(20260904)
        for _ in range(25):
            s=tuple(generator.choice((-1,1)) for _ in range(LENGTH))
            self.assertEqual(correlations(s),independent_correlations(s))
            self.assertGreaterEqual(energy(s),256)
            self.assertEqual(energy(s)%4,0)

    def test_extremal_boundary_and_construction(self):
        self.assertEqual(energy((1,)*512),MAX_ENERGY)
        self.assertEqual(MAX_ENERGY,44608256)
        self.assertEqual(energy(rudin_shapiro()),43776)

    def test_equivalent_symmetries_do_not_create_improvements(self):
        s=decode_hex(json.loads((ROOT/'literature/reference.json').read_text())['hex'])
        for rev in (s,s[::-1]):
            for sign in (-1,1):
                for alternate in (False,True):
                    transformed=tuple(x*sign*(-1 if alternate and i%2 else 1) for i,x in enumerate(rev))
                    self.assertEqual(energy(transformed),17996)
        self.assertNotEqual(energy(s[1:]+s[:1]),17996) # cyclic shifts are not generally aperiodic symmetries


class ArtifactTests(unittest.TestCase):
    def test_valid_complete_result(self):
        result=evaluate(ROOT/'fixtures/baseline',ROOT/'suite')
        self.assertEqual(result,{'apiVersion':'science-ladder/v1','kind':'ValidatorResult','score':'17996','gates':{'one_canonical_sequence':True,'binary_length_512':True}})

    def test_wrong_length_or_alphabet_never_scores_valid(self):
        for payload in (b'+'*511+b'\n', b'+'*511+b'0\n',b'+'*511+b'1\n',b'+'*511+b'x\n',b'+'*511+b'\r\n', b'', b'\xef\xbb\xbf'+b'+'*509+b'\n', b'\xff',b'+'*512,b'+'*256+b'\n'+b'-'*255+b'\n'):
            with artifact(payload) as root:
                result=evaluate(root,ROOT/'suite')
                self.assertFalse(all(result['gates'].values()))

    def test_json_parser_tricks_and_numeric_inputs_rejected(self):
        for payload in (b'{"x":1,"x":2}',b'1e309',b'NaN',b'Infinity',b'-0',b'999999999999999999999',b'[]',b'__import__("os").system("id")'):
            with artifact(payload) as root:
                self.assertFalse(all(evaluate(root,ROOT/'suite')['gates'].values()))

    def test_malformed_encoding_empty_and_overlarge(self):
        for payload in (b'+'*514,b'PK\x03\x04'+b'+'*510):
            with artifact(payload) as root:
                with self.assertRaises((ArtifactError,OSError)):
                    evaluate(root,ROOT/'suite')

    def test_byte_count_checked_before_read(self):
        with artifact() as root:
            with (root/'sequence.txt').open('wb') as f: f.truncate(1024*1024*1024)
            with self.assertRaises(ArtifactError):read_artifact(root)

    def test_extra_files_nested_paths_and_empty_directory(self):
        with artifact() as root:
            (root/'ignored.json').write_text('{}')
            with self.assertRaises(ArtifactError):read_artifact(root)
        with artifact() as root:
            (root/'data').mkdir()
            with self.assertRaises(ArtifactError):read_artifact(root)
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ArtifactError):read_artifact(Path(folder))

    def test_symlink_hardlink_and_fifo_rejected_without_hang(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'submission';root.mkdir()
            outside=Path(folder)/'outside.txt';outside.write_bytes(b'+'*512+b'\n')
            target=root/'sequence.txt';target.symlink_to(outside)
            with self.assertRaises((ArtifactError,OSError)):read_artifact(root)
            target.unlink();os.link(outside,target)
            with self.assertRaises(ArtifactError):read_artifact(root)
            target.unlink();os.mkfifo(target)
            with self.assertRaises(ArtifactError):read_artifact(root)
            target.unlink();(Path(folder)/'link').symlink_to(root,target_is_directory=True)
            with self.assertRaises((ArtifactError,OSError)):read_artifact(Path(folder)/'link')

    def test_suite_cannot_override_length_or_supply_scores(self):
        with tempfile.TemporaryDirectory() as folder:
            suite=Path(folder)
            for payload in (b'{"length":1}', b'{"length":512,"length":1}', b'{"score":"0"}',(ROOT/'suite/contract.json').read_bytes()+b' '):
                (suite/'contract.json').write_bytes(payload)
                with self.assertRaises(ArtifactError):evaluate(ROOT/'fixtures/baseline',suite)


class ProcessTests(unittest.TestCase):
    def run_checker(self,fixture,output):
        return subprocess.run([sys.executable,str(ROOT/'checker.py'),'--submission',str(ROOT/'fixtures'/fixture),'--suite',str(ROOT/'suite'),'--output',str(output)],capture_output=True,timeout=5)

    def test_exact_output_repeatability_and_failure_has_no_score(self):
        with tempfile.TemporaryDirectory() as folder:
            paths=[Path(folder)/f'result-{i}.json' for i in range(4)]
            for path in paths:self.assertEqual(self.run_checker('baseline',path).returncode,0)
            self.assertEqual(len({hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),1)
            bad=Path(folder)/'bad.json';result=self.run_checker('malformed',bad)
            self.assertEqual(result.returncode,2);self.assertFalse(bad.exists())
            self.assertNotIn(b'Traceback',result.stderr)

    def test_output_cannot_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'result.json';path.write_bytes(b'previous')
            self.assertNotEqual(self.run_checker('baseline',path).returncode,0)
            self.assertEqual(path.read_bytes(),b'previous')

    def test_local_harness_enforces_timeout_for_stalled_process(self):
        # Deliberately stalled trusted test process, not a submission or checker
        # feature. This only checks local deadline cleanup, not Firecracker.
        start=time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            subprocess.run([sys.executable,'-c','import time; time.sleep(60)'],timeout=0.1,capture_output=True)
        self.assertLess(time.monotonic()-start,3)

if __name__=='__main__':unittest.main(verbosity=2)
