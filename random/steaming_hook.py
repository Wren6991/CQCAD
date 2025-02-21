import cadquery as cq

# Screw to the top of a doorframe. Perfect place to hang a coathanger when
# steaming a shirt.

# Dimensions in mm
csk_diameter = 7.8
csk_height = 3.5
thread_diameter = 4.2 + 0.2

block_depth = 18
block_width = 40
block_height = 20

cone_depth = 15
cone_inset = 5

edge_fillet = min((block_depth, block_width, block_height)) * 0.2

cone = (
    cq.Workplane("top")
    .workplane(offset=block_height / 2 - cone_depth)
    .center(0, -cone_inset)
    .circle(block_height)
    .extrude(block_height)
    .faces("<Y")
    .chamfer(block_height * 0.999)
)


result = (
    cq.Workplane("front")
    .rect(block_width, block_height)
    .extrude(block_depth)
    .edges("|Z or >Z")
    .fillet(edge_fillet)
    .faces(">Z").workplane()
    .rarray(block_width - 1.5 * csk_diameter, 1, 2, 1)
    .cskHole(thread_diameter, csk_diameter, 90)
) - cone

show_object(result)

cq.exporters.export(result, "steaming_hook.stl")
