import cadquery as cq

# Measurements (all in mm)

boox_width                    = 135.5
boox_edge_thickness           = 6.5
boox_button_centre_inset      = 22
boox_button_cutout_width      = 20
boox_button_cutout_depth_frac = 0.8
boox_button_height            = 2
# Parameters

brim = 4

col_width = 20
col_depth = 20
col_height = 60
col_fillet = 5

col_pushback = 0

base_width = boox_width + 1 * col_width 
base_depth = 18
base_height = 100 + brim

base_bottom_chamfer = 3
base_fillet = 5

base_cutout_count = 4
base_cutout_pitch = (base_width + 2 * col_width) / (base_cutout_count + 1)
base_cutout_width = base_cutout_pitch * 0.6
base_cutout_height = base_height * 0.8

# To flatten the bottom:
bottom_slice_off = 1

foot_width = 40
foot_count = 2
foot_pitch = 2 * base_cutout_pitch
foot_depth = 150
foot_corner_radius = 15
foot_chamfer = 2
foot_thickness = 10

#

columns = (
	cq.Workplane("front")
	.workplane(offset=-bottom_slice_off)
	.center(0, col_pushback)
	.rarray(boox_width + col_width - brim, 1, 2, 1)
	.rect(col_width + brim, col_depth)
	.extrude(col_height + base_height)
	.faces().fillet(col_fillet)
)

base = (
	cq.Workplane("front")
	.workplane(offset=-bottom_slice_off)
	.rect(base_width, base_depth)
	.extrude(base_height + bottom_slice_off)
	.edges("|X")
	.fillet(base_fillet)
	.faces("<Y").workplane()
	.center(0, 0.5 * base_height)
	.text(" ".join("BOOX"), 4, -1)
)

boox_blank = (
	cq.Workplane("front")
	.workplane(offset=base_height - brim)
	.tag("wp")
	.rect(boox_width, boox_edge_thickness)
	.extrude(col_height + 2 * brim + bottom_slice_off)
	.edges("<Z and |Y")
	.fillet(1.5)
	.workplaneFromTagged("wp")
	.center(0.5 * boox_width - boox_button_centre_inset, 0)
	.rect(boox_button_cutout_width, boox_button_cutout_depth_frac * boox_edge_thickness)
	.extrude(-boox_button_height)
)

floor = (
	cq.Workplane("front")
	.rect(1000, 1000)
	.extrude(-2 * bottom_slice_off)
)

base_cutouts = (
	cq.Workplane("XZ")
	.workplane(offset=-base_depth)
	.center(0, base_height / 2)
	.rarray(base_cutout_pitch, 1, base_cutout_count, 1)
	.rect(base_cutout_width, base_cutout_height)
	.extrude(base_depth * 2)
	.edges("|Y")
	.chamfer(base_cutout_width * 0.499)
)

base = (base | columns) - base_cutouts
bracket = base - boox_blank - floor

foot = (
	cq.Workplane("front")
	.rarray(foot_pitch, 1, foot_count, 1)
	.rect(foot_width, foot_depth)
	.extrude(foot_thickness)
	.edges("|Z")
	.fillet(foot_corner_radius)
	.faces("|Z")
	.chamfer(foot_chamfer)
)
result = bracket | foot

show_object(result)

# show_object(columns, options={"color": "red"})
# show_object(boox_blank)
cq.exporters.export(result, "stand.stl")
