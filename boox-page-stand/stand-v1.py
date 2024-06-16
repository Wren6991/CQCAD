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

col_width = 20
col_depth = 30
col_height = 60

base_width = boox_width + 2 * col_width 
base_depth = col_depth
base_height = 25 + brim

base_bottom_chamfer = 3
base_fillet = 8

#

base = (
	cq.Workplane("front")
	.rect(base_width, base_depth)
	.extrude(base_height)
	.faces(">Z").workplane()
	.rarray(boox_width + col_width - brim, 1, 2, 1)
	.rect(col_width + brim, col_depth)
	.extrude(col_height)
	.faces("<Z")
	.chamfer(base_bottom_chamfer)
	.faces("<X or >X or <Y or >Y")
	.fillet(base_fillet)
	.faces("<Y").workplane()
	.center(0, -0.5 * base_height)
	.text("  ".join("BOOX"), 0.5 * base_height, -1)
)

boox_blank = (
	cq.Workplane("front")
	.workplane(offset=base_height - brim)
	.tag("wp")
	.rect(boox_width, boox_edge_thickness)
	.extrude(col_height + 2 * brim)
	.workplaneFromTagged("wp")
	.center(0.5 * boox_width - boox_button_centre_inset, 0)
	.rect(boox_button_cutout_width, boox_button_cutout_depth_frac * boox_edge_thickness)
	.extrude(-boox_button_height)
)

result = base - boox_blank

show_object(result)
# show_object(boox_blank)
cq.exporters.export(result, "stand.stl")
