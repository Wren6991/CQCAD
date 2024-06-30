import cadquery as cq
import math
from util import *

# I ordered a 4mm acrylic plate to cover my open window, with 2x 15 cm holes cut
#in it. This file contains fittings to attach two 15cm AC hoses to those holes.
#
# Each hole gets a two-part fitting that screws through it. The inside side of
# the fitting has centering features and magnets to allow a third part to be
# clipped on, which has a threaded collar for an AC hose.

# All dimensions in mm.

plate_hole_diameter      = 148 # 150 minus clearance
plate_thickness          = 4

fitting_thread_pitch     = 3.2
fitting_thread_crest     = 1.6
fitting_thread_clearance = 0.8
fitting_id               = plate_hole_diameter - 8
fitting_face_chamfer     = 3.5
fitting_fit_chamfer      = 1

fitting_flange_thickness = 8
fitting_flange_width     = 12

magnet_ring_diameter     = (plate_hole_diameter + fitting_id) / 2 + fitting_flange_width
magnet_diameter          = 6.6
magnet_depth             = 3.2
magnet_count             = 8

grip_groove_count        = 24
grip_groove_depth        = 0.8
grip_groove_radius       = grip_groove_depth * 10

hose_diameter = 150
hose_pitch_lh = 10
hose_pitch_rh = 8
hose_crest = 5

collar_wall_thickness = 6

def fitting_inner_base():
    return Feature(
        (
            cq.Workplane("XY")
            .circle(fitting_flange_width + plate_hole_diameter / 2)
            .extrude(fitting_flange_thickness)
        ).union(
            cq.Workplane("XY")
            .circle(plate_hole_diameter / 2)
            .extrude(fitting_flange_thickness * 2 + plate_thickness)
        )
        .circle(fitting_id / 2)
        .cutThruAll()
        .faces("<Z").chamfer(fitting_face_chamfer)
        .faces(">Z").chamfer(fitting_fit_chamfer)
        .polarArray(fitting_flange_width + plate_hole_diameter / 2 + grip_groove_radius - grip_groove_depth, 0, 360, grip_groove_count)
        .circle(grip_groove_radius)
        .cutThruAll()
    )

def fitting_outer_base():
    return Feature(
        cq.Workplane("XY")
        .circle(fitting_flange_width + plate_hole_diameter / 2)
        .extrude(fitting_flange_thickness)
        .faces("<Z").chamfer(fitting_face_chamfer)
        .faces(">Z").chamfer(fitting_fit_chamfer)
        .circle(plate_hole_diameter / 2 + fitting_thread_clearance)
        .cutThruAll()
        .polarArray(fitting_flange_width + plate_hole_diameter / 2 + grip_groove_radius - grip_groove_depth, 0, 360, grip_groove_count)
        .circle(grip_groove_radius)
        .cutThruAll()
    )

def magnet_holes():
    return Feature(
        cq.Workplane("XY")
        .polarArray(magnet_ring_diameter / 2, 0, 360, magnet_count)
        .circle(magnet_diameter / 2)
        .extrude(magnet_depth)
    ).invert()

fitting_inner = resolve_features(
    fitting_inner_base(),
    extruded_thread(
        fitting_thread_pitch,
        fitting_thread_crest,
        plate_hole_diameter,
        plate_thickness + fitting_flange_thickness + fitting_thread_pitch
    ).translateZ(fitting_flange_thickness).invert(),
    magnet_holes()
)

fitting_outer = resolve_features(
    fitting_outer_base(),
    extruded_thread(
        fitting_thread_pitch,
        fitting_thread_crest,
        plate_hole_diameter + 2 * fitting_thread_clearance,
        fitting_flange_thickness 
    )
)

def antichamfer_cutout():
    return Feature(
        cq.Workplane("XY")
        .circle(fitting_flange_width + plate_hole_diameter / 2)
        .extrude(fitting_flange_thickness)
        .circle(fitting_id / 2)
        .cutThruAll()
        .faces("<Z").chamfer(fitting_face_chamfer)
    ).translateZ(fitting_flange_thickness - fitting_face_chamfer).invert()

def threaded_collar(thread_pitch, thread_lefthanded):
    n_threads = 2

    base = Feature(
        cq.Workplane("XY")
        .circle(fitting_flange_width + plate_hole_diameter / 2)
        .extrude(fitting_flange_thickness)
        .circle(fitting_id / 2)
        .cutThruAll()
        .faces("<Z").chamfer((hose_diameter - fitting_id) / 2)
        .faces("<Z").workplane()
        .circle(hose_diameter / 2)
        .circle(hose_diameter / 2 + collar_wall_thickness)
        .extrude(thread_pitch * (n_threads + 1))
        .faces("<Z")
        .chamfer(fitting_fit_chamfer)
    )
    thread = extruded_thread(
        thread_pitch,
        hose_crest,
        hose_diameter,
        thread_pitch * (n_threads + 1),
        lefthanded = thread_lefthanded,
        od_flat_fraction = 0.16,
        id_flat_fraction = 0.1
    )
    return resolve_features(
        base,
        antichamfer_cutout(),
        magnet_holes().translateZ(fitting_flange_thickness - fitting_face_chamfer - magnet_depth),
        thread.translateZ(-thread_pitch * (n_threads + 1))
    )

def fitting_cover():
    base = Feature(
        cq.Workplane("XY")
        .circle(fitting_flange_width + plate_hole_diameter / 2)
        .extrude(fitting_flange_thickness)
        .faces("<Z").chamfer((hose_diameter - fitting_id) / 2)
    )
    return resolve_features(
        base,
        magnet_holes().translateZ(fitting_flange_thickness - fitting_face_chamfer - magnet_depth),
        antichamfer_cutout()
    )

safe_write_stl(fitting_inner, "window_fitting_inner.stl")
safe_write_stl(fitting_outer, "window_fitting_outer.stl")

collar_intake = threaded_collar(10, True)
collar_exhaust = threaded_collar(8, False)
collar_blocked = fitting_cover()

safe_write_stl(collar_intake, "window_collar_intake.stl")
safe_write_stl(collar_exhaust, "window_collar_exhaust.stl")
safe_write_stl(collar_blocked, "window_collar_blocked.stl")

if "show_object" in globals():
    show_object(fitting_inner)
    show_object(fitting_outer.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, 100)))
    show_object(collar_intake.translate((0, 0, -100)))
    show_object(collar_exhaust.translate((0, 0, -200)))
    show_object(collar_blocked.translate((0, 0, -300)))
