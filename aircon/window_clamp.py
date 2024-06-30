import cadquery as cq
import math
from util import safe_write_stl

l1                 = 25 # Back-side X
l2                 = 6  # Y
l3                 = 22 # approx 45 degrees
l4_options         = [17, 43] # Front-side X

l3_angle_hack      = 3

seal_step          = 3.5
seal_step_from_end = 9

thickness          = 2 # Set to 4x extrusion line width

height             = 30

screw_loose        = 3.7
screw_tight        = 3.1
screw_block_width  = screw_tight + 2.5
screw_block_height = 3.5
screw_block_fillet = thickness / 2
screw_count        = 2
screw_spacing      = height / 2
screw_cb_depth     = 3.1
screw_cb_diameter  = 5.5

def resolve_delta(l):
	accum = [0 for x in l[0]]
	points_out = [tuple(accum)]
	for delta in l:
		for i, x in enumerate(delta):
			accum[i] += x
		points_out.append(tuple(accum))
	return points_out

def c_clip(l4):
	delta_xy = [
		(l4 - thickness / 2, 0),
		(l3 / math.sqrt(2), l3 / math.sqrt(2) - l3_angle_hack),
		(0, l2 + thickness + l3_angle_hack),
		(-l1 + thickness / 2 + seal_step + seal_step_from_end, 0),
		(-seal_step, -seal_step),
		(-seal_step_from_end, 0)
	]

	return (
		cq.Workplane("XY")
		.polyline(resolve_delta(delta_xy))
		.offset2D(thickness / 2)
		.extrude(height)
	).translate((thickness / 2, 0, 0))

def screw_block():
	return (
		cq.Workplane("XY")
		.center(screw_block_width / 2, -screw_block_height / 2)
		.rect(screw_block_width, screw_block_height + thickness)
		.extrude(height)
		.edges("|Z").fillet(screw_block_fillet)
	)

def clip_screw_hole():
	return (
		cq.Workplane("XZ")
		.workplane(offset=-thickness / 2)
		.center(screw_block_width / 2, height / 2)
		.rarray(1, screw_spacing, 1, screw_count)
		.circle(screw_tight / 2)
		.extrude(screw_block_height + thickness)
	)

for i, l4 in enumerate(l4_options):
	result = c_clip(l4).union(screw_block()) - clip_screw_hole()
	if "show_object" in globals(): show_object(result.translate((0, 0, i * height * 1.5)))
	safe_write_stl(result, f"window_clamp_{l4}.stl")

def clamp_plate():
	return (
		cq.Workplane("XZ")
		.rect(min(l4_options), height, centered=False)
		.extrude(1.2 + screw_cb_depth)
		.edges("|Y").fillet(thickness / 2)
		.faces("<Y").fillet(thickness / 2)
		.center(screw_block_width / 2, height / 2)
		.rarray(1, screw_spacing, 1, screw_count)
		.circle(screw_loose / 2).cutThruAll()
		.faces("<Y").workplane()
		.rarray(1, screw_spacing, 1, screw_count)
		.circle(screw_cb_diameter / 2).cutBlind(-screw_cb_depth)
	)

plate = clamp_plate()
if "show_object" in globals(): show_object(plate.translate((0, -50, 0)))
safe_write_stl(plate.rotate((0, 0, 0), (1, 0, 0), -90), "window_clamp_plate.stl")
