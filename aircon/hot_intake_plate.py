import cadquery as cq
import math
import os

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
top_snap_thickness     = 1.1
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
hose_screw_ring        = hose_hole_diameter + 25
hose_screw_count       = 8
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
fitting_length         = fitting_thread_pitch * 4

class Feature:
    
    """A tuple of a body (the positive) and the cuts made when combining that
    body with another Feature (the negative). After combining features with
    Feature.combine(), call Feature.resolve() to subtract the union of all
    negatives from the union of all positives."""

    def __init__(self, positive, negative=None):
        self.positive = positive
        self.negative = negative

    def combine(self, other):
        
        def union_optional(lhs, rhs):
            if lhs is None:
                return rhs
            elif rhs is None:
                return lhs
            else:
                return lhs.union(rhs)
        
        return Feature(
            union_optional(self.positive, other.positive),
            union_optional(self.negative, other.negative)
        )

    def invert(self):
        return Feature(self.negative, self.positive)

    def rotate(self, axis, angle):
        return Feature(
            None if self.positive is None else self.positive.rotate((0, 0, 0), axis, angle),
            None if self.negative is None else self.negative.rotate((0, 0, 0), axis, angle)
        )

    def translate(self, vec):
        return Feature(
            None if self.positive is None else self.positive.translate(vec),
            None if self.negative is None else self.negative.translate(vec)
        )

    def translateX(self, x):
        return self.translate((x, 0, 0))

    def translateY(self, y):
        return self.translate((0, y, 0))

    def translateZ(self, z):
        return self.translate((0, 0, z))

    def resolve(self):
        if self.negative is None:
            return self.positive
        else:
            return self.positive - self.negative


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
    return Feature(
        (
            cq.Workplane()
            .circle(hose_hole_diameter / 2)
            .extrude(plate_wall_height + plate_bottom_thickness)
        ).union(
            cq.Workplane()
            .workplane(offset=plate_wall_height + plate_bottom_thickness)
            .circle(hose_hole_diameter / 2 + plate_edge_chamfer)
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
        None,
        cq.Workplane("XY")
        .workplane(offset=plate_wall_height)
        .rarray((plate_width - 2 * magnet_hole_edge_inset) / 2, (plate_height - 2 * magnet_hole_edge_inset) / 2, 3, 3)
        .circle(magnet_hole_diameter / 2)
        .extrude(magnet_hole_depth)
    )

plate = (
    plate_base()
    .combine(tabs())
    .combine(hose_cutout())
    .combine(hose_interlock_groove().translateZ(plate_wall_height + plate_bottom_thickness))
    .combine(snap_fits(top_snap_width, top_snap_pitch, top_snap_count, plate_height / 2, 0))
    .combine(snap_fits(side_snap_width, 1, 1, plate_width / 2, 90))
    .combine(snap_fits(side_snap_width, 1, 1, plate_width / 2, -90))
    .combine(magnet_holes())
    .resolve()
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
    unthreaded_length = fitting_thread_pitch * 0.5
    extrusion_length = fitting_length - fitting_thread_pitch - unthreaded_length
    n_twists = extrusion_length / fitting_thread_pitch

    r = hose_hole_diameter / 2
    t = fitting_thread_crest
    p = fitting_thread_pitch
    e = t * 0.01
    
    return Feature(
        cq.Workplane("XY")
        .workplane(offset=unthreaded_length / 2)
        # .center(hose_hole_diameter / 2, 0)
        .polyline([
            (r + e, 0, p * 0.10),
            (r - t, 0, p * 0.45),
            (r - t, 0, p * 0.55),
            (r + e, 0, p * 0.90)
        ]).close()
        .twistExtrude(extrusion_length, 360 * n_twists)
    )

    
if "show_object" in globals(): show_object(plate)
# Flip for correct print orientation. Note you will need tree supports for the
# overhangs on the snaps and tabs. I recommend increasing line width for the
# top/bottom skin to reduce print time. Test print was on K1 Max.
plate = plate.rotate((0, 0, 0), (1, 0, 0), 180)

# Workaround issue with fstl reading the file mid-rewrite
def safe_write_stl(obj, fname):
    cq.exporters.export(obj, fname + ".tmp", exportType="STL")
    os.replace(fname + ".tmp", fname)

safe_write_stl(plate, "hot_intake_plate.stl")

fitting = (
    fitting_base()
    .combine(hose_interlock_groove().rotate((1, 0, 0), 180).translateZ(fitting_length).invert())
    .combine(fitting_screw_holes())
    .combine(fitting_thread())
    .resolve()
)

safe_write_stl(fitting, "hot_intake_fitting.stl")
