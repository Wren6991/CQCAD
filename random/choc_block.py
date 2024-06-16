import cadquery as cq

cols = 5
rows = 4
colspace = 17.5
rowspace = 17.5
case_height = 8

margin = 4
socket_clearance = 0 
socket_width = 13.8 + socket_clearance
socket_height = 13.6 + socket_clearance
socket_depth = 1.2
socket_rib_thickness = 3

screw_boss_diameter = 6
screw_boss_height = 5
screw_hole_diameter = 2.8
screw_hole_depth = 4.5

base_thickness = 4.5
base_hole_diameter = 3.2
base_cbore_diameter = 5.2
base_cbore_depth = 3.2

pico_length = 51
pico_width = 21
pico_hole_diameter = 2.1
pico_hole_sep_l = 47
pico_hole_sep_w = 11.4
pico_hole_peg_height = 1.5

pico_header_digout_inset = 0.5
pico_header_digout_width = 4
pico_header_digout_depth = 1

# Bars running down edges of the base to help centre the case during assembly
alignment_bar_thickness = 1.5
alignment_bar_clearance = 0.2

case = (
    cq.Workplane("front")
    # Body
    .box(cols * colspace + 2 * margin, rows * rowspace + 2 * margin, case_height)
    .edges("|Z").fillet(margin)
    .faces(">Z").chamfer(margin * 0.5)
    .faces(">Z").workplane(offset=-socket_rib_thickness)
    .rect(cols * colspace, rows * rowspace).cutBlind(-case_height)
    # Switch sockets
    .faces(">Z").workplane()
    .rarray(colspace, rowspace, cols, rows)
    .rect(socket_width, socket_height).cutBlind(-socket_rib_thickness)
    .faces(">Z").workplane(offset=-socket_depth)
    .rarray(colspace, rowspace, cols, rows)
    .rect(colspace - 2, rowspace - 2).cutBlind(-socket_rib_thickness)
    # Bossed screw holes
    .faces(">Z").workplane(offset=-case_height)
    .rarray(cols * colspace, rows * rowspace, 2, 2)
    .circle(screw_boss_diameter / 2).extrude(screw_boss_height)
    .faces(">Z").workplane(offset=-case_height - (screw_boss_height - screw_hole_depth))
    .rarray(cols * colspace, rows * rowspace, 2, 2)
    .circle(screw_hole_diameter / 2).cutBlind(5)
    # Micro USB cutout
    .faces(">X").edges("<Z").workplane(centerOption="CenterOfMass").tag("usb_edge")
    .rect(8, 2 * 3.6).cutBlind(-(margin + 1))
    .workplaneFromTagged("usb_edge")
    .rect(12, 2 * 6).cutBlind(-(margin - 1))
)

base = (
    cq.Workplane("front").workplane(offset=-30)
    # Body
    .box(cols * colspace + 2 * margin, rows * rowspace + 2 * margin, base_thickness)
    .edges("|Z").fillet(margin)
    .faces("<Z").chamfer(0.2 * margin)
    # Locating pegs for Pico mounting holes
    .faces(">Z").workplane(centerOption="CenterOfBoundBox").tag("topsurface")
    .center((cols * colspace - pico_length) / 2, 0)
    .rarray(pico_hole_sep_l, pico_hole_sep_w, 2, 2)
    .circle(pico_hole_diameter / 2).extrude(pico_hole_peg_height)
    # Butt stop for Pico, to take USB insertion force
    .workplaneFromTagged("topsurface")
    .pushPoints([(cols * colspace / 2 - pico_length - alignment_bar_thickness / 2, 0)])
    .rect(alignment_bar_thickness, pico_hole_sep_w).extrude(alignment_bar_thickness)
    # Dig out space under Pico headers, to accommodate solder blobs
    .workplaneFromTagged("topsurface")
    .center((cols * colspace - pico_length) / 2, 0)
    .rarray(1, pico_width - 2 * pico_header_digout_inset, 1, 2)
    .rect(pico_length, pico_header_digout_width).cutBlind(-pico_header_digout_depth)
    # Locating features on edges for assembly
    .workplaneFromTagged("topsurface")
    .rarray(1, rows * rowspace - alignment_bar_thickness - 2 * alignment_bar_clearance, 1, 2)
    .rect(cols * colspace - screw_boss_diameter - 2 * alignment_bar_clearance, alignment_bar_thickness)
    .extrude(alignment_bar_thickness)
    # Close USB cutout
    .faces(">X").edges("|Y and >Z").workplane(centerOption="CenterOfMass").tag("usbplane")
    .rect(8, 2 * 1).extrude(-margin)
    .workplaneFromTagged("usbplane")
    .rect(12, 2 * 3).cutBlind(-(margin - 1))
    # Screw holes
    .faces("<Z").workplane(centerOption="CenterOfBoundBox")
    .rect(cols * colspace, rows * rowspace).vertices()
    .cboreHole(base_hole_diameter, base_cbore_diameter, base_cbore_depth)
)

show_object(case)
show_object(base)

cq.exporters.export(case, f"choc_block_case_{cols}x{rows}.stl")
cq.exporters.export(base, f"choc_block_base_{cols}x{rows}.stl")
