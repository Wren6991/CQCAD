import os
import cadquery as cq

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


def combine_features(*varg):
    accum = Feature(None)
    for arg in varg:
        accum = accum.combine(arg)
    return accum

def resolve_features(*varg):
    return combine_features(*varg).resolve()

# Workaround issue with fstl reading the file mid-rewrite
def safe_write_stl(obj, fname):
    cq.exporters.export(obj, fname + ".tmp", exportType="STL")
    os.replace(fname + ".tmp", fname)

def thread_profile(pitch, crest, od, od_flat_fraction, id_flat_fraction):
    r0 = od / 2 + crest * 0.01
    r1 = od / 2 - crest
    z0 = pitch * od_flat_fraction / 2 
    z1 = pitch * (0.5 - id_flat_fraction / 2)
    z2 = pitch * (0.5 + id_flat_fraction / 2)
    z3 = pitch * (1 - od_flat_fraction / 2)
    return [
        (r0, 0, z0),
        (r1, 0, z1),
        (r1, 0, z2),
        (r0, 0, z3),
    ]

def extruded_thread(pitch, crest, od, length, lefthanded=False, od_flat_fraction=0.2, id_flat_fraction=0.2):
    turns = (length - pitch) / pitch
    assert(turns > 0)
    # twistExtrude behaves strangely for large angles, so extrude one turn at a
    # time and take a union.
    accum = cq.Workplane("XY")
    offset = 0
    while turns > 0:
        chunk = 1 if turns > 1 else turns
        turns -= chunk
        accum = accum.union(
            cq.Workplane("XY")
            .workplane(offset=offset)
            .polyline(thread_profile(pitch, crest, od, od_flat_fraction, id_flat_fraction)).close()
            .twistExtrude(pitch * chunk, (-360 if lefthanded else 360) * chunk)
        )
        offset += pitch
    return Feature(accum)         
