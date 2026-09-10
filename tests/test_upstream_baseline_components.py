"""Bounded tests of pinned upstream components, never their hardware runners."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "gest": "4fbe3e4549740dcceaf8a968bd0156ce8cbe5643",
    "gest_saga": "2292814234735680ccab4f0cba567017e4ca425c",
}


@pytest.mark.parametrize("name", PINS)
def test_pinned_component_contract(name):
    source = ROOT / "third_party" / name
    revision = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    assert revision == PINS[name]
    code = """
import sys
sys.path.insert(0, sys.argv[1])
from Individual import Individual
from Instruction import Instruction
from Population import Population
from Fitness.DefaultFitness import DefaultFitness

extra = {'numOfInstructions': 1} if sys.argv[2] == 'gest_saga' else {}
instruction = Instruction('add', 'alu', 0, operands=[], format='add x1,x2,x3', **extra)
left = Individual(sequence=[instruction], generation=0)
right = left.copy()
right.sequence[0].name = 'changed'
assert left.sequence[0].name == 'add'
left.setMeasurementsVector([0.25])
assert DefaultFitness().getFitness(left) == [0.25, 0.25]
left.setFitness(-0.25)
right.setFitness(-0.75)
population = Population(individuals=[right, left])
assert population.getFittest() is left
population.sortByFitessToWeakest()
assert population.getIndividual(0) is left
assert str(instruction) == 'add x1,x2,x3'
print('copy, rendering, measurement passthrough, maximize ordering: PASS')
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", code, str(source / "src"), name],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS" in result.stdout


def test_saga_features_cannot_distinguish_order():
    code = """
import sys
sys.path.insert(0, sys.argv[1])
from Individual import Individual
from Instruction import Instruction
from Population import Population
from featureExtraction import instructionTypesAsFeatures

alu = Instruction('add', 'alu', 0, 1, operands=[], format='add x1,x2,x3')
mul = Instruction('mul', 'multiply', 0, 1, operands=[], format='mul x1,x2,x3')
a = Individual(sequence=[alu.copy(), mul.copy()], generation=0)
b = Individual(sequence=[mul.copy(), alu.copy()], generation=0)
a.setFitness(1.0)
b.setFitness(1.0)
rows, names = instructionTypesAsFeatures(Population(individuals=[a,b]), 2)
assert rows[0] == rows[1] == [1.0, 1, 1]
assert names == ['alu', 'multiply']
print('reordered sequences have identical upstream features: PASS')
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", code,
         str(ROOT / "third_party/gest_saga/src")],
        text=True, capture_output=True, check=True,
    )
    assert "PASS" in result.stdout
