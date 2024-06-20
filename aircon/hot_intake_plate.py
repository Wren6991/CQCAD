import cadquery as cq
import math
from util import *

# All dimensions in mm
plate_width            = 255
plate_height           = 249
plate_corner_radius    = 6
plate_edge_chamfer     = 2
plate_wall_thickness   = 4
plate_wall_height      = 8
plate_bottom_thickness = 5

# Locking tabs on bottom edge of plate
tab_width              = 10
tab_length             = 4
tab_thickness          = 2.1
tab_pitch              = 98
tab_count              = 3

# Snap-fits on top edge of plate
top_snap_width         = 10
top_snap_side_relief   = 2.1
top_snap_thickness     = 1.5
top_snap_inset         = 1.0
top_snap_freeboard     = 2.4
top_snap_lip_step      = 1.6 # Measured at 1.0
top_snap_lip_height    = 3.5 # Measured at 3.5
top_snap_pitch         = 160
top_snap_count         = 2

side_snap_width        = 6.8

hose_hole_diameter     = 150
hose_groove_diameter   = hose_hole_diameter + 10
hose_groove_depth      = 2
hose_screw_ring        = hose_hole_diameter + 20
hose_screw_count       = 6
hose_screw_loose       = 3.7
hose_screw_tight       = 3.1
hose_screw_cb_depth    = 3.1
hose_screw_cb_diameter = 5.5

# Magnets for attaching a filter mesh plate inside this backplate:
magnet_hole_diameter   = 6.5
magnet_hole_depth      = 3.2
magnet_hole_edge_inset = 10

fitting_diameter       = hose_screw_ring + 10
fitting_thread_pitch   = 8
fitting_thread_crest   = 5
fitting_length         = fitting_thread_pitch * 3.5
fitting_lefthanded     = False

filter_clearance      = 1
filter_width          = plate_width - 2 * (filter_clearance + plate_wall_thickness)
filter_height         = plate_height - 2 * (filter_clearance + plate_wall_thickness)
filter_edge_thickness = plate_wall_height - 1
filter_edge_width     = magnet_hole_diameter * 1.5
filter_rib_thickness  = filter_edge_thickness / 2
filter_rib_width      = filter_rib_thickness
filter_thickness      = 0.8
filter_line_width     = 0.5 # Set to extruder line width
filter_line_thickness = 0.2 # Set to layer height
filter_line_pitch     = 2 * filter_line_width
filter_zones          = 3
filter_corner_radius  = max(2, plate_corner_radius - plate_wall_thickness)
filter_bottom_chamfer = max(1, plate_edge_chamfer - plate_wall_thickness)
filter_top_chamfer    = 1

def plate_base():
    positive = (
        cq.Workplane("XY")
        .rect(plate_width, plate_height)
        .extrude(plate_bottom_thickness + plate_wall_height)
        .edges("|Z")
        .fillet(plate_corner_radius)
        .faces(">Z")
        .chamfer(plate_edge_chamfer)
    )
    negative = (
        cq.Workplane("XY")
        .rect(plate_width - 2 * plate_wall_thickness, plate_height - 2 * plate_wall_thickness)
        .extrude(plate_wall_height)
        .edges("|Z")
        .fillet(plate_corner_radius - plate_wall_thickness)
        .faces(">Z")
        .chamfer(plate_edge_chamfer)
    )
    return Feature(positive, negative)

def tabs():
    return Feature(
        cq.Workplane("XY")
        .center(0, -plate_height / 2 - tab_length / 2)
        .rarray(tab_pitch, 1, tab_count, 1)
        .rect(tab_width, tab_length)
        .extrude(tab_thickness)
        .edges("<Y and |Z")
        .fillet(tab_length / 4)
    )

def snap_fits(width, pitch, count, centre_to_wall, angle):

    def base_plane():
        return (
            cq.Workplane("XY")
            .workplane(offset=plate_wall_height)
            .center(0, centre_to_wall - top_snap_thickness / 2 - top_snap_inset)
        )

    positive = (
        base_plane()
        .rarray(pitch, 1, count, 1)
        .rect(width, top_snap_thickness)
        .extrude(-plate_wall_height - top_snap_freeboard)
        .faces(">Z")
        .workplane(offset=-plate_wall_height - top_snap_freeboard)
        .center(0, top_snap_lip_step / 2)
        .rarray(pitch, 1, count, 1)
        .rect(width, top_snap_thickness + top_snap_lip_step)
        .extrude(-top_snap_lip_height)
        .edges("<Z and >Y").chamfer(top_snap_thickness + top_snap_lip_step - 0.00001)
        # .faces(">Y").edges(">Z").chamfer(top_snap_lip_step / 2)
        .rotate((0, 0, 0), (0, 0, 1), angle)
    )
    # First clear space all around the column
    negative = (
        base_plane()
        .rarray(pitch, 1, count, 1)
        .rect(width + 2 * top_snap_side_relief, top_snap_thickness + 3 * plate_wall_thickness)
        .extrude(-plate_wall_height)
        .rotate((0, 0, 0), (0, 0, 1), angle)
    ) - positive
    # Then fillet the negative to avoid stress risers at bottom of relief cut
    negative = negative.faces(">Z").fillet(top_snap_side_relief * 0.4999)
    return Feature(positive, negative)


def hose_cutout():
    plate_hole_diameter = hose_hole_diameter - fitting_thread_crest
    return Feature(
        (
            cq.Workplane()
            .circle(plate_hole_diameter / 2)
            .extrude(plate_wall_height + plate_bottom_thickness)
        ).union(
            cq.Workplane()
            .workplane(offset=plate_wall_height + plate_bottom_thickness)
            .circle(plate_hole_diameter / 2 + plate_edge_chamfer)
            .extrude(-plate_edge_chamfer - 0.0001)
            .faces("<Z").chamfer(plate_edge_chamfer)
        ).union(
            cq.Workplane()
            .workplane(offset=plate_wall_height)
            .polarArray(hose_screw_ring / 2, 0, 360, hose_screw_count)
            .circle(hose_screw_loose / 2)
            .extrude(plate_bottom_thickness)
            .polarArray(hose_screw_ring / 2, 0, 360, hose_screw_count)
            .circle(hose_screw_cb_diameter / 2)
            .extrude(hose_screw_cb_depth)
        )
    ).invert()

def hose_interlock_groove():
    return Feature(
        None,
        (
            cq.Workplane()
            .circle(hose_groove_diameter / 2 + hose_groove_depth)
            .extrude(-hose_groove_depth)
            .circle(hose_groove_diameter / 2 - hose_groove_depth)
            .cutThruAll()
            .faces("<Z").chamfer(hose_groove_depth * 0.9999)
        )
    )

def magnet_holes():
    return Feature(
        cq.Workplane("XY")
        .rarray((plate_width - 2 * magnet_hole_edge_inset) / 2, (plate_height - 2 * magnet_hole_edge_inset) / 2, 3, 3)
        .circle(magnet_hole_diameter / 2)
        .extrude(magnet_hole_depth)
    ).invert()

plate = resolve_features(
    plate_base(),
    tabs(),
    hose_cutout(),
    hose_interlock_groove().translateZ(plate_wall_height + plate_bottom_thickness),
    snap_fits(top_snap_width, top_snap_pitch, top_snap_count, plate_height / 2, 0),
    snap_fits(side_snap_width, 1, 1, plate_width / 2, 90),
    snap_fits(side_snap_width, 1, 1, plate_width / 2, -90),
    magnet_holes().translateZ(plate_wall_height)
)

def fitting_base():
    ring_thickness = (fitting_diameter - hose_hole_diameter) / 2
    return Feature(
        (
            cq.Workplane("XY")
            .circle(fitting_diameter / 2)
            .extrude(fitting_length)
            .faces("<Z")
            .chamfer(min(fitting_length, ring_thickness * 0.7))
            .circle(hose_hole_diameter / 2)
            .cutThruAll()
            .faces(">Z")
            .chamfer(ring_thickness * 0.1)
        ),
        (
            cq.Workplane("XY")
            .circle(hose_hole_diameter / 2 + ring_thickness * 0.1)
            .extrude(ring_thickness * 0.1)
            .faces(">Z").chamfer(ring_thickness * 0.0999)
        )
    )

def fitting_screw_holes():
    return Feature(
        cq.Workplane("XY")
        .workplane(offset=fitting_length)
        .polarArray(hose_screw_ring / 2, 0, 360, hose_screw_count)
        .circle(hose_screw_tight / 2)
        .extrude(-fitting_length * 0.5)
    ).invert()

def fitting_thread():
    unthreaded_length = fitting_thread_pitch * 0.25
    extrusion_length = fitting_length - fitting_thread_pitch - unthreaded_length
    n_twists = extrusion_length / fitting_thread_pitch

    r = hose_hole_diameter / 2
    t = fitting_thread_crest
    p = fitting_thread_pitch
    e = t * 0.01

    return Feature(
        cq.Workplane("XY")
        .workplane(offset=unthreaded_length / 2)
        .polyline([
            (r + e, 0, p * 0.08),
            (r - t, 0, p * 0.45),
            (r - t, 0, p * 0.55),
            (r + e, 0, p * 0.92)
        ]).close()
        .twistExtrude(extrusion_length, (-360 if fitting_lefthanded else 360) * n_twists)
    )

def filter_plate():
    zone_spacing_x = (filter_width  - 2 * filter_edge_width + filter_rib_width) / filter_zones
    zone_spacing_y = (filter_height - 2 * filter_edge_width + filter_rib_width) / filter_zones
    base = (
        cq.Workplane("XY")
        .rect(filter_width, filter_height)
        .extrude(filter_edge_thickness)
        .edges("|Z").fillet(filter_corner_radius)
        .faces(">Z").chamfer(filter_top_chamfer)
        .rect(filter_width - 2 * filter_edge_width, filter_height - 2 * filter_edge_width)
        .cutThruAll()
        .faces("<Z").chamfer(filter_bottom_chamfer)
    ).union(
        cq.Workplane("XY")
        .workplane(offset=filter_edge_thickness - filter_rib_thickness)
        .rarray(zone_spacing_x, 1, filter_zones - 1, 1)
        .rect(filter_rib_width, filter_height - 2 * filter_edge_width)
        .extrude(filter_rib_thickness)
        .rarray(1, zone_spacing_y, 1, filter_zones - 1)
        .rect(filter_width - 2 * filter_edge_width, filter_rib_width)
        .extrude(filter_rib_thickness)
        .faces("<Z").chamfer(filter_top_chamfer)
    )
    base = base - magnet_holes().invert().resolve()
    count_x = round((filter_width - 2 * filter_edge_width) / filter_line_pitch)
    count_y = round((filter_height - 2 * filter_line_width) / filter_line_pitch)
    for layer in range(round(filter_thickness / filter_line_thickness)):
        # The epsilon here is to prevent the layers from touching, as that makes
        # the CSG engine shit the bed
        base = base.faces(">Z").workplane(offset=-layer * filter_line_thickness * 1.001)
        if layer % 2 == 0:
            base = (
                base
                .rarray(filter_line_pitch, 1, count_x, 1)
                .rect(filter_line_width, filter_height - 2 * filter_edge_width)
                .extrude(-filter_line_thickness)
            )
        else:
            base = (
                base
                .rarray(1, filter_line_pitch, 1, count_y)
                .rect(filter_width - 2 * filter_edge_width, filter_line_width)
                .extrude(-filter_line_thickness)
            )

    return base

# Flip for correct print orientation. Note you will need tree supports for the
# overhangs on the snaps and tabs. I recommend increasing line width for the
# top/bottom skin to reduce print time. Test print was on K1 Max.
plate = plate.rotate((0, 0, 0), (1, 0, 0), 180)

safe_write_stl(plate, "hot_intake_plate.stl")

fitting = resolve_features(
    fitting_base(),
    hose_interlock_groove().rotate((1, 0, 0), 180).translateZ(fitting_length).invert(),
    fitting_screw_holes(),
    fitting_thread()
)

safe_write_stl(fitting, "hot_intake_fitting.stl")

filter = filter_plate()

safe_write_stl(filter, "hot_intake_filter.stl")

if "show_object" in globals():
    show_object(plate)
    show_object(fitting.rotate((0, 0, 0), (1, 0, 0), 0).translate((0, 0, -100)), options={"color": "red"})
    show_object(filter.translate((0, 0, 100)), options={"color": "blue"})
