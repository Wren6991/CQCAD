import cadquery as cq

# Main knobs
package_size = 10
package_thickness = 0.8
cols = 4
rows = 4
lid_text = "" + ("QFN80" if package_size == 10 else "QFN60")
text_size = 12

package_clearance = 0.3
package_spacing = 4
package_lip_height = 1
package_lip_chamfer = 1.2
package_wall_cutout_fraction = 0.5

package_pitch = package_size + package_spacing
package_wall_height = package_thickness + package_lip_height

box_margin = 10
box_fillet = 5
box_bottom_chamfer = 1.5
box_top_chamfer = 0.6
box_finger_cutout_inset_fraction = 0.6
box_finger_cutout_widening_fraction = 1
box_finger_cutout_depth_fraction = 0.5

box_width = cols * package_pitch + 2 * box_margin
box_height = rows * package_pitch + 2 * box_margin
box_depth = 7.5
lid_clearance = 0.2

magnet_diameter = 6 + 0.35
magnet_thickness = 3 + 0.2
magnet_edge_inset = 1.5
magnet_bury_depth = 0.4

base = (
    # Basic block for base
    cq.Workplane("front")
    .rect(box_width, box_height)
    .extrude(box_depth)
    .edges("|Z").fillet(box_fillet)
    .faces("<Z").chamfer(box_bottom_chamfer)
    # Box edge cutouts to make it easier to pull apart
    .faces(">Z").workplane().tag("base_face")
    .rarray(box_width + 2 * box_margin * box_finger_cutout_widening_fraction, box_height + 2 * box_margin * box_finger_cutout_widening_fraction, 2, 1)
    .circle(box_margin * (box_finger_cutout_widening_fraction + box_finger_cutout_inset_fraction))
    .rarray(box_width + 2 * box_margin * box_finger_cutout_widening_fraction, box_height + 2 * box_margin * box_finger_cutout_widening_fraction, 1, 2)
    .circle(box_margin * (box_finger_cutout_widening_fraction + box_finger_cutout_inset_fraction))
    .cutBlind(-box_depth * box_finger_cutout_depth_fraction)
    .faces(">Z").chamfer(box_top_chamfer)
    # Blind holes for magnets
    .faces(">Z").workplane().tag("base_top")
    .workplane(offset=-magnet_bury_depth)
    .rarray(box_width - magnet_diameter - 2 * magnet_edge_inset, box_height - magnet_diameter - 2 * magnet_edge_inset, 2, 2)
    .circle(magnet_diameter / 2)
    .cutBlind(-magnet_thickness)
    # Pockets for each package
    .workplaneFromTagged("base_face")
    .rect(cols * package_pitch + package_spacing, rows * package_pitch + package_spacing)
    .extrude(package_wall_height)
    .faces(">Z").workplane()
    .rarray(package_pitch, package_pitch, cols, rows)
    .rect(package_size + 2 * package_clearance, package_size + 2 * package_clearance)
    .cutBlind(-package_wall_height)
    .faces(">Z").chamfer(package_lip_chamfer)
    # Blow out the middle of each package wall to allow packages to be jimmied out
    .workplaneFromTagged("base_top")
    .rarray(package_pitch, package_pitch, cols, 1)
    .rect(package_size * package_wall_cutout_fraction, package_pitch * rows + package_spacing)
    .cutBlind(package_wall_height)
    .rarray(package_pitch, package_pitch, 1, rows)
    .rect(package_pitch * cols + package_spacing, package_size * package_wall_cutout_fraction)
    .cutBlind(package_wall_height)
)

lid = (
    cq.Workplane("front").workplane(offset = 30)
    .rect(box_width, box_height)
    .extrude(box_depth)
    .edges("|Z").fillet(box_fillet)
    .faces(">Z").tag("lid_top")
    .chamfer(box_bottom_chamfer)
    .faces(">Z").workplane()
    .text(lid_text, text_size, -0.2, halign="center", valign="center", font="noto sans mono")
    .faces("<Z").tag("lid_bottom").workplane()
    # Finger cutouts matching the base
    .rarray(box_width + 2 * box_margin * box_finger_cutout_widening_fraction, box_height + 2 * box_margin * box_finger_cutout_widening_fraction, 2, 1)
    .circle(box_margin * (box_finger_cutout_widening_fraction + box_finger_cutout_inset_fraction))
    .rarray(box_width + 2 * box_margin * box_finger_cutout_widening_fraction, box_height + 2 * box_margin * box_finger_cutout_widening_fraction, 1, 2)
    .circle(box_margin * (box_finger_cutout_widening_fraction + box_finger_cutout_inset_fraction))
    .cutBlind(-box_depth * box_finger_cutout_depth_fraction)
    .faces("<Z").chamfer(box_top_chamfer)
    # Blind holes for magnets
    .faces("<Z").workplane(offset=-magnet_bury_depth)
    .rarray(box_width - magnet_diameter - 2 * magnet_edge_inset, box_height - magnet_diameter - 2 * magnet_edge_inset, 2, 2)
    .circle(magnet_diameter / 2)
    .cutBlind(-magnet_thickness)
    # Cutout for package walls on base
    .faces("<Z").workplane(offset=-package_wall_height)
    .rect(cols * package_pitch + package_spacing + 2 * lid_clearance, rows * package_pitch + package_spacing + 2 * lid_clearance)
    .cutBlind(package_wall_height)
    .rarray(package_pitch, package_pitch, cols, rows)
    .circle(package_size * 0.8 / 2)
    .extrude(package_lip_height)
)

show_object(base)
show_object(lid)
cq.exporters.export(base, f"{package_size}mm_{cols}x{rows}_base.stl")
cq.exporters.export(lid, f"{package_size}mm_{cols}x{rows}_lid.stl")
