# type: ignore

from compas.geometry import Point, Polygon, Translation
from compas.utilities import linspace, pairwise
from compas.datastructures import Mesh
from compas.colors import Color, ColorMap
from compas_view2.app import App

n = 1000
t = 0.3

up = []
down = []
for i in linspace(0, 10, n):
    point = Point(i, 0, 0)
    up.append(point + [0, t, 0])
    down.append(point - [0, t, 0])

polygons = []
for (d, c), (a, b) in zip(pairwise(up), pairwise(down)):
    polygons.append(Polygon([a, b, c, d]))

mesh = Mesh.from_polygons(polygons)

viewer = App()
viewer.view.show_grid = False

cmap = ColorMap.from_color(Color.red())
facecolors = {i: cmap(i, minval=0, maxval=n - 1) for i in range(n)}

viewer.add(mesh, facecolor=facecolors, show_lines=False)

cmap = ColorMap.from_color(Color.red(), rangetype="light")
facecolors = {i: cmap(i, minval=0, maxval=n - 1) for i in range(n)}

translation = Translation.from_vector([0, -3 * t, 0])
viewer.add(mesh.transformed(translation), facecolor=facecolors, show_lines=False)

cmap = ColorMap.from_color(Color.red(), rangetype="dark")
facecolors = {i: cmap(i, minval=0, maxval=n - 1) for i in range(n)}

translation = Translation.from_vector([0, -6 * t, 0])
viewer.add(mesh.transformed(translation), facecolor=facecolors, show_lines=False)

viewer.show()
