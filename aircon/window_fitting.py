import cadquery as cq
import math
from util import *

# I ordered a 4mm acrylic plate to cover my open window, with 2x 15 cm holes cut
#in it. This file contains fittings to attach two 15cm AC hoses to those holes.
#
# Each hole gets a two-part fitting that screws through it. The inside side of
# the fitting has centering features and magnets to allow a third part to be
# clipped on, which has a threaded collar for an AC hose.

plate_hole_diameter = 148 # 150 minus clearance
plate_thickness = 4

fitting_thread_pitch = 3.2
fitting_thread_crest = 1.6
fitting_thread_clearance = 0.8
fitting_id = plate_hole_diameter - 8
fitting_face_chamfer = 6
fitting_fit_chamfer = 1

fitting_flange_thickness = 8
fitting_flange_width = 15

magnet_ring_diameter = (plate_hole_diameter + fitting_id) / 2 + fitting_flange_width
magnet_diameter = 6.6
magnet_depth = 3.2
magnet_count = 8

def fitting_inner_base():
    return Feature(
        cq.Workplane("XY")
        .circle(fitting_flange_width + plate_hole_diameter / 2)
        .extrude(fitting_flange_thickness)
        .circle(plate_hole_diameter / 2)
        .extrude(2 * fitting_flange_thickness + plate_thickness)
        .circle(fitting_id / 2)
        .cutThruAll()
        .faces("<Z").chamfer(fitting_face_chamfer)
        .faces(">Z").chamfer(fitting_fit_chamfer)
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
    )

def magnet_holes():
    return Feature(
        cq.Workplane("XY")
        .polarArray(magnet_ring_diameter / 2, 0, 360, magnet_count)
        .circle(magnet_diameter / 2)
        .extrude(magnet_depth)
    ).invert()

def extruded_thread(pitch, crest, od, length, lefthanded=False, od_flat_fraction=0.2, id_flat_fraction=0.2):
    r0 = od / 2 + crest * 0.01
    r1 = od / 2 - crest
    z0 = pitch * od_flat_fraction / 2 
    z1 = pitch * (0.5 - id_flat_fraction / 2)
    z2 = pitch * (0.5 + id_flat_fraction / 2)
    z3 = pitch * (1 - od_flat_fraction / 2)
    return Feature(
        cq.Workplane("XY")
        .polyline([
            (r0, 0, z0),
            (r1, 0, z1),
            (r1, 0, z2),
            (r0, 0, z3),
        ]).close()
        .twistExtrude(length - pitch, (-360 if lefthanded else 360) * (length - pitch) / pitch)
    )
         

fitting_inner = resolve_features(
    fitting_inner_base(),
    extruded_thread(
        fitting_thread_pitch,
        fitting_thread_crest,
        plate_hole_diameter,
        plate_thickness + fitting_flange_thickness + 3 * fitting_thread_pitch
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

safe_write_stl(fitting_inner, "window_fitting_inner.stl")
safe_write_stl(fitting_outer, "window_fitting_outer.stl")
