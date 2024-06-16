import cadquery as cq

depth = 18
width = 295
length = width / 2

wall_thickness = 3
corner_radius = 30
bottom_chamfer = 5

n_bottom_grooves = 15
bottom_groove_depth = 0.5
bottom_groove_pitch = (width - 2 * max(bottom_chamfer, corner_radius)) / n_bottom_grooves

result = (
    cq.Workplane("front")
    .rect(width, length)
    .extrude(depth)
    .edges("|Z")
    .fillet(corner_radius)
    .faces("-Z")
    .chamfer(bottom_chamfer)
    .faces("<Z")
    .tag("bottom")
    .workplane(offset=-depth)
    .center(0, -length / 2 + 2)
    .circle(10)
    .extrude(8, taper=45)
    .faces("+Z")
    .shell(-wall_thickness)
    .workplaneFromTagged("bottom")
    .rarray(bottom_groove_pitch, 1, n_bottom_grooves, 1)
    .slot2D(length, bottom_groove_pitch * 0.5, 90)
    .cutBlind(bottom_groove_depth)
)

show_object(result)
cq.exporters.export(result, "scrap_tray.stl")
