import cadquery as cq
import math

# Dimensions in mm
fit_tolerance = 0.3
casing_width = 165 + fit_tolerance
casing_height = 100 + fit_tolerance
casing_thickness = 3.7 + fit_tolerance

ribbon_width = 35
ribbon_clearance = 1.5

recline_from_vertical = 30

base_thickness = 10
base_column_width = 10
base_column_height = 30
base_length = 65
base_cutout_depth = base_length * 2 / 3
base_chamfer = 3
lip = 2

result = (
	cq.Workplane("front")
	.rect(casing_width + 2 * base_column_width, base_length)
	.extrude(base_thickness)
	.rarray(casing_width + base_column_width - lip, 1, 2, 1)
	.rect(base_column_width + lip, base_length)
	.extrude(base_thickness + base_column_height)
	.center(0, base_length / 2)
	.rect(casing_width - 2 * base_column_width, 2 * base_cutout_depth)
	.cutThruAll()
	.faces().chamfer(base_chamfer)
)

casing = (
	cq.Workplane("front")
	.transformed(offset=(0, 0, (casing_height / 2) * math.cos(recline_from_vertical * math.pi / 180) + base_thickness))
	.transformed(rotate=(90 - recline_from_vertical, 0, 0))
	.rect(casing_width, casing_height)
	.extrude(casing_thickness)
	.rarray(1, casing_height, 1, 2)
	.rect(ribbon_width, ribbon_clearance)
	.extrude(casing_thickness)
)

result = result - casing

show_object(result)
show_object(casing, options={"color": "red"})
cq.exporters.export(result, "stand.stl")
