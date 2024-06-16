import cadquery as cq

perimeter_w = 100
perimeter_h = 65
holes_w = 94
holes_h = 59

corner_fillet = 3
edge_chamfer = 1.5

# Hole size: direct threading of M2 machine screw
hole_diameter = 1.8
boss_diameter = 6

thickness = 3
standoff = 3

# Cutout for flash module
cutout_offset_from_left = 36
cutout_w = 28
cutout_l = 43
cutout_fillet = 2
cutout_inset = 15

s = cq.Workplane("XY")

result = (
    s
    .rect(perimeter_w, perimeter_h)
    .extrude(thickness)
    .edges("|Z").fillet(corner_fillet)
    .faces(">Z").workplane().tag("topface")
    .rect(holes_w, holes_h, forConstruction=True).vertices()
    .circle(boss_diameter / 2)
    .extrude(standoff)
    .workplaneFromTagged("topface").workplane(offset = -(thickness - edge_chamfer))
    .rect(holes_w, holes_h, forConstruction=True).vertices()
    .circle(hole_diameter / 2)
    .cutBlind(standoff + thickness - edge_chamfer)
    .workplaneFromTagged("topface")
    .center(-perimeter_w / 2, -perimeter_h / 2)
    .center(cutout_offset_from_left, cutout_inset)
    .rect(cutout_w, cutout_l - cutout_inset, centered=False)
    .cutThruAll(10)
    .edges("|Z").fillet(cutout_fillet)
    .faces("<Z").chamfer(edge_chamfer)
    .faces("<Z").workplane(centerOption="CenterOfBoundBox")
    .transformed(offset=(0,25,0),rotate=(0,0,180)).text("AMMO BOARD", 7.5, -0.2)
)

show_object(result)
cq.exporters.export(result, f"pcb_sled_W{perimeter_w}_H{perimeter_h}.stl")