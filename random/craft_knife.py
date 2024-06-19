import cadquery as cq

# Craft knife with 1992 Stanley blade embedded as a print-over element.
# (Single-use, but then so are the blades.)
#
# Print with at least three perimeters. Print with a layer height of 0.16 to get
# correct thickness for the blade cavity.

# All dimensions in mm.

handle_thickness      = 20
handle_depth          = 30
handle_length         = 95
handle_end_fillet     = 10
handle_chamfer        = 5

handle_groove_count   = 4
handle_groove_spacing = handle_length / handle_groove_count
handle_groove_radius  = handle_length / 8
handle_groove_depth   = 3

blade_to_bottom_edge  = 8
exposed_blade_length  = 6
blade_print_clearance = 0.65

def stanley_blade():
	thickness         = 0.6
	depth             = 19.0 + blade_print_clearance
	slot_separation   = 3 + blade_print_clearance
	slot_width        = 3.3 - blade_print_clearance
	slot_depth_rect   = 2.5
	slot_round_radius = slot_width / 2
	bottom_length     = 61.5 + blade_print_clearance
	top_length        = 2 * 11.5 + 2 * slot_width + slot_separation + blade_print_clearance
	return (
		cq.Workplane("XY")
		.workplane(offset=-thickness / 2)
		.polyline([
			(0, 0, 0),
		    ((bottom_length - top_length) / 2, depth, 0),
		    (bottom_length - (bottom_length - top_length) / 2, depth, 0),
		    (bottom_length, 0, 0)
		]).close()
		.extrude(thickness)
		.center(bottom_length / 2, depth - slot_depth_rect / 2)
		.rarray(slot_separation + slot_width, 1, 2, 1)
		.rect(slot_width, slot_depth_rect)
		.cutThruAll()
		.center(0, -slot_depth_rect / 2)
		.rarray(slot_separation + slot_width, 1, 2, 1)
		.circle(slot_width / 2)
		.cutThruAll()
	)

def handle():
	return (
		cq.Workplane("XY")
		.workplane(offset=-handle_thickness / 2)
		.rect(handle_length, handle_depth, centered=False)
		.extrude(handle_thickness)
		.faces(">X").edges("|Z").fillet(handle_end_fillet)
		.faces(">Y").edges("|Z").fillet(handle_end_fillet)
		.faces("<Y").edges("<X").chamfer(handle_chamfer)
		.faces(">Z or <Z").chamfer(handle_chamfer)
		.center(handle_length / 2, -(handle_groove_radius - handle_groove_depth))
		.rarray(handle_groove_spacing, 1, handle_groove_count, 1)
		.circle(handle_groove_radius)
		.cutThruAll()
		.faces("<Y")
		.fillet(handle_groove_depth)
		.faces(">Z").workplane(centerOption="CenterOfBoundBox")
		.text("DOWNLOAD-A-KNIFE", handle_length * 0.08, -1)
	)

blade_translated = stanley_blade().translate((-exposed_blade_length, blade_to_bottom_edge, 0))
result = handle() - blade_translated

if "show_object" in globals():
	show_object(blade_translated, options={"color": "gray"})
	show_object(result, options={"color": "red", "alpha": 0.5})

cq.exporters.export(result, "craft_knife.stl")
