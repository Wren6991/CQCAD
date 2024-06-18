import cadquery as cq

# Scrap tray to slide under K1 Max, for your skirts, supports, purge lines etc.
# Printable on K1 Max. Note the max depth for the stock feet is around 18 mm. I
# printed the squashball feet from here:
#
#   https://www.printables.com/model/734250-creality-k1k1-max-squashball-foot
#
# Which provide sufficient depth for this tray size. I recommend increasing your
# line width in your slicer to around 1.25x your nozzle diameter to reduce print
# time with all the flat surfaces.

depth = 35
width = 295
length = width * 0.8

wall_thickness = 3
corner_radius = 30
bottom_chamfer = 10
handle_radius = 15

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
    .center(0, -length / 2 + wall_thickness)
    .circle(handle_radius)
    .extrude(handle_radius - wall_thickness, taper=45)
    .faces("+Z")
    .shell(-wall_thickness)
    .workplaneFromTagged("bottom")
    .rarray(bottom_groove_pitch, 1, n_bottom_grooves, 1)
    .slot2D(length, bottom_groove_pitch * 0.5, 90)
    .cutBlind(bottom_groove_depth)
)

show_object(result)
cq.exporters.export(result, "scrap_tray.stl")
