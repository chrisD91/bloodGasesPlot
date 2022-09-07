# For relative imports to work in Python 3.6
import os
import sys

# see https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
from pathlib import Path


print("Running" if __name__ == "__main__" else "Importing", Path(__file__).resolve())
if os.path.dirname(os.path.realpath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))


usual = dict(
    o2=[80, 112],
    co2=[36, 46],
    ph=[3.34, 7.48],
    hco3=[22, 29],
    angap=[5, 16],
    na=[136, 142],
    cl=[98, 104],
    k=[2.2, 4],
)
