import cadquery as cq

card_clearance = 0.5
card_wh = 46 + 2 * card_clearance
card_thickness = 3
card_spacing = 10
n_cards = 10

card_angle = 60

card_edge_inset = 5
base_width = card_wh + 2 * card_edge_inset
base_length = 0.4 * card_wh + card_spacing * (n_cards - 1) + 10
base_height = card_wh * 0.5

base = (
    cq.Workplane("front")
    .rect(base_width, base_length)
    .extrude(base_height)
    .edges("|Z")
    .fillet(6)
    .faces("<Z")
    .chamfer(3)
    .faces("<Y")
    .workplane().center(0, base_height)
    .circle(card_wh / 4)
    .cutThruAll()
    .faces(">Z")
    .fillet(3)
    .faces("<X").workplane(offset=-card_edge_inset, centerOption="CenterOfBoundBox")
    .center(0, 0.25 * card_wh)
    .rarray(card_spacing, 1, n_cards, 1)
    .slot2D(card_wh, card_thickness, card_angle)
    .cutBlind(-card_wh)
    .faces(">Z")
    .chamfer(1)
    .faces(">Y").workplane(centerOption="CenterOfBoundBox")
    .center(0, -4)
	.text("AMTEST", 7, -0.5, font="noto sans mono", kind="bold")
)

show_object(base)
cq.exporters.export(base, "amy_card_boxy.stl")
