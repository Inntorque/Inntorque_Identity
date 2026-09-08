"""Open the small uppercase Q counter while preserving its exterior and tail."""
from svgpathtools import CubicBezier, Line, Path as SvgPath

KAPPA = 0.5522847498307936

def ellipse(cx, cy, rx, ry):
    p = [complex(cx+rx, cy), complex(cx, cy+ry), complex(cx-rx, cy), complex(cx, cy-ry)]
    return SvgPath(
        CubicBezier(p[0], p[0]+1j*KAPPA*ry, p[1]+KAPPA*rx, p[1]),
        CubicBezier(p[1], p[1]-KAPPA*rx, p[2]+1j*KAPPA*ry, p[2]),
        CubicBezier(p[2], p[2]-1j*KAPPA*ry, p[3]-KAPPA*rx, p[3]),
        CubicBezier(p[3], p[3]+KAPPA*rx, p[0]-1j*KAPPA*ry, p[0]))

def softened_cap(before, corner1, corner2, after, radius):
    d1 = (corner1-before)/abs(corner1-before)
    d2 = (corner2-corner1)/abs(corner2-corner1)
    d3 = (after-corner2)/abs(after-corner2)
    p1, p2 = corner1-radius*d1, corner1+radius*d2
    p3, p4 = corner2-radius*d2, corner2+radius*d3
    return [Line(before, p1), CubicBezier(p1, p1+KAPPA*radius*d1, p2-KAPPA*radius*d2, p2),
            Line(p2, p3), CubicBezier(p3, p3+KAPPA*radius*d2, p4-KAPPA*radius*d3, p4), Line(p4, after)]

def intersection(curve, origin, direction):
    hits = curve.intersect(SvgPath(Line(origin, origin+direction*300)))
    assert len(hits) == 1
    return hits[0][0][0]

def remainder(curve, a, b):
    return list(curve.cropped(a, 1)) + list(curve.cropped(0, b))

def restore_q_weight(small_q, q_scale):
    x0, x1, y0, y1 = small_q.bbox()
    rx, ry = 66.9*q_scale, 65*q_scale
    cx, cy = x0+rx, y0+ry
    outer = ellipse(cx, cy, rx, ry)
    # Retain the prior counter center before opening its ellipse and retracting the inner tail.
    left, right, top, bottom = 31.2, 30.8, 30.0, 27.2
    icx, icy = cx+(left-right)/2, cy+(top-bottom)/2
    base_irx, base_iry = rx-(left+right)/2, ry-(top+bottom)/2
    counter_scale = 1.30
    irx, iry = base_irx*counter_scale, base_iry*counter_scale
    inner = ellipse(icx, icy, irx, iry)
    direction = complex(54, 48)/abs(complex(54, 48))
    normal = 1j*direction
    half_width, radius = 9.0, 2.2
    # Solve cap placement from its exact Bezier bounds, keeping Q width/height fixed.
    fb0, fa0 = -half_width*normal, half_width*normal
    cap = SvgPath(*softened_cap(fb0-100*direction, fb0, fa0, fa0-100*direction, radius))
    cap_bounds = cap.bbox()
    far = complex(x1-cap_bounds[1], y1-cap_bounds[3])
    counter_center = complex(icx, icy)
    projection = far+direction*((counter_center-far)*direction.conjugate()).real
    near = projection+8.0*direction
    a, b = near+half_width*normal, near-half_width*normal
    fa, fb = far+half_width*normal, far-half_width*normal
    for point in [a, b]:
        assert ((point.real-icx)/irx)**2+((point.imag-icy)/iry)**2 < 1
    ob, oa = intersection(outer, b, direction), intersection(outer, a, direction)
    ib, ia = intersection(inner, b, direction), intersection(inner, a, direction)
    assert ob < oa and ib < ia
    outside_arc, inside_arc = remainder(outer, oa, ob), remainder(inner, ia, ib)
    outside = SvgPath(*softened_cap(outside_arc[-1].end, fb, fa, outside_arc[0].start, radius), *outside_arc)
    counter = SvgPath(*softened_cap(inside_arc[-1].end, b, a, inside_arc[0].start, radius), *inside_arc)
    result = SvgPath(*outside, *counter)
    assert len(result.continuous_subpaths()) == 2
    assert max(abs(a-b) for a, b in zip(result.bbox(), small_q.bbox())) < 1e-8
    note = {
        'fixed_visible_bounds': [x0, y0, x1, y1],
        'outer_ellipse_center': [cx, cy], 'outer_ellipse_radii': [rx, ry],
        'counter_ellipse_center': [icx, icy], 'counter_ellipse_radii': [irx, iry],
        'previous_bowl_weights': {'left': left, 'right': right, 'top': top, 'bottom': bottom},
        'counter_radius_scale': counter_scale,
        'bowl_weights': {'left': icx-irx-(cx-rx), 'right': cx+rx-(icx+irx), 'top': icy-iry-(cy-ry), 'bottom': cy+ry-(icy+iry)},
        'tail_width': 2*half_width, 'tail_terminal_radius': radius,
        'tail_direction': [direction.real, direction.imag],
        'tail_far_center': [far.real, far.imag], 'tail_inner_cap_center': [near.real, near.imag],
        'contours': 2, 'filled_bodies': 1, 'counters': 1,
        'inner_tail_cap_projection_offset': 8.0,
        'method': 'Counter ellipse radii enlarged 1.30 and inner tail cap retracted four units along the unchanged tail direction; exterior outline, eighteen-unit outer tail and total Q bounds preserved.'}
    return result, note
