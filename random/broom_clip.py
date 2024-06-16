import cadquery as cq

# Measurements
handle_diameter = 21.6
screw_thread_diameter = 3.5
screw_head_diameter = 6.6

# Clearances
handle_clearance = 0.5
screw_clearance = 0.2

# Parameters
plate_width = 45
plate_height = 25
plate_thickness = 3
plate_corner_fillet = 5

hole_spacing = plate_width - 10

bracket_height = 20
bracket_thickness = 3
bracket_extra_grip_depth = 5


plate = (
    cq.Workplane("front")
    .rect(plate_width, plate_height)
    .extrude(plate_thickness)
    .edges("|Z").fillet(plate_corner_fillet)
    .faces(">Z").chamfer(plate_corner_fillet / 4)
    .faces(">Z").workplane()
    .rarray(hole_spacing, 1, 2, 1)
    .cskHole(screw_thread_diameter + screw_clearance, screw_head_diameter + screw_clearance, cskAngle=82)
)

bracket = (
    cq.Workplane("top")
    .workplane(offset=-bracket_height / 2)
    .center(0, -(handle_diameter / 2 + handle_clearance / 2 + plate_thickness))
    .circle((handle_diameter + handle_clearance) / 2 + bracket_thickness)
    .extrude(bracket_height)
    .circle((handle_diameter + handle_clearance) / 2)
    .cutThruAll()
    .center(0, -(bracket_extra_grip_depth + 100))
    .rect(plate_width,  2 * 100)
    .cutThruAll()
)

result = plate | bracket
show_object(result)

cq.exporters.export(result, "broom_clip.stl")
