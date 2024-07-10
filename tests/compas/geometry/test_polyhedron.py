import pytest
import json
import compas
from random import random
from compas.geometry import Point
from compas.geometry import Polyhedron
from compas.itertools import pairwise


def test_polyhedron():
    vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    faces = [[0, 1, 2, 3]]
    name = "Test Polyhedron"
    polyhedron = Polyhedron(vertices, faces, name)

    assert polyhedron.vertices == vertices
    assert polyhedron.faces == faces
    assert polyhedron.name == name
    assert polyhedron.points == vertices
    assert polyhedron.lines == [(a, b) for a, b in pairwise(vertices + vertices[:1])]
    assert polyhedron.points[0] == vertices[0]
    assert polyhedron.points[-1] != polyhedron.points[0]


def test_polyhedron_str():
    vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0]]
    faces = [[0, 1, 2]]
    polyhedron = Polyhedron(vertices, faces)

    assert str(polyhedron) == "Polyhedron(vertices=[['0.000', '0.000', '0.000'], ['1.000', '0.000', '0.000'], ['1.000', '1.000', '0.000']], faces=[[0, 1, 2]])"
