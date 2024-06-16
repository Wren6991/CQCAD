import cadquery as cq

# Measurements (all in mm)

boox_width                    = 135.8
boox_edge_thickness           = 6.5
boox_button_centre_inset      = 22
boox_button_cutout_width      = 20
boox_button_cutout_depth_frac = 0.8
boox_button_height            = 2
# Parameters

brim = 3

col_width = 25
col_depth = 40
col_height = 60
col_fillet = 10

base_width = boox_width + 1 * col_width 
base_depth = 20
base_height = 30 + brim

base_bottom_chamfer = 3
base_fillet = 8

# To flatten the bottom:
bottom_slice_off = 1

#

columns = (
	cq.Workplane("front")
	.workplane(offset=-bottom_slice_off)
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
	.text("  ".join("BOOX"), 0.2 * base_height, -1)
)

boox_blank = (
	cq.Workplane("front")
	.workplane(offset=base_height - brim)
	.tag("wp")
	.rect(boox_width, boox_edge_thickness)
	.extrude(col_height + 2 * brim + bottom_slice_off)
	.edges("<Z and |Y")
	.fillet(1)
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

result = (base | columns) - boox_blank - floor

show_object(result)
# show_object(columns, options={"color": "red"})
# show_object(boox_blank)
cq.exporters.export(result, "stand.stl")
