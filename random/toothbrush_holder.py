import cadquery as cq

hole_diameters = [20, 40, 20]
wall_thickness = 6
base_thickness = 5
height = 60

edge_chamfer = wall_thickness * 0.4

width = sum(hole_diameters) + wall_thickness * (len(hole_diameters) + 1)
depth = max(hole_diameters) + wall_thickness * 2

def holes():
    w = cq.Workplane("XY")
    offset_next = 0
    for i, d in enumerate(hole_diameters):
        offset_next += wall_thickness + d / 2
        w = w.union(
            cq.Workplane("XY")
            .center(offset_next, wall_thickness + max(hole_diameters) / 2)
            .circle(d / 2)
            .extrude(height)
            .circle(d / 4)
            .extrude(height + 2 * base_thickness)
        )
        offset_next += d / 2
    return w

def base():
    return (
        cq.Workplane("XY")
        .center(width / 2, depth / 2)
        .rect(width, depth)
        .extrude(height + base_thickness)
        .edges("|Z and >Y")
        .fillet(max(hole_diameters) / 2 + wall_thickness)
    )


result = (
    (
        (
            base()
            .faces(">Z")
            .chamfer(edge_chamfer)
        ) - holes()
    ).faces("-Z or <Y")
    .chamfer(edge_chamfer)
)   

if "show_object" in globals():
    show_object(result)

cq.exporters.export(result.rotate((0, 0, 0,), (1, 0, 0), 180), "toothbrush_holder.stl")
