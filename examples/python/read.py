#!/usr/bin/python
# coding: utf8

import os
from os.path import dirname, abspath, join
import sys

root = dirname(dirname(dirname(abspath(__file__))))
sys.path.insert(0, join(root, 'wrappers/python'))

import speechtux

if __name__ == "__main__":
    speechtux.read("Ceci est un test de lecture avec les paramètres par défaut.")
    speechtux.read(
        "Ceci est un test de lecture accéléré.",
        speed=200
    )
    speechtux.read(
        "Ceci est un test de lecture ralenti",
        speed=50
    )
    speechtux.read(
        "Ceci est un test de lecture level",
        level=50
    )
    speechtux.read(
        "Changement de volume : quart du son",
        volume=25
    )
