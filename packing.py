"""
3D Bin Packing – Extreme Point Method with Contact-Maximisation scoring.

Key ideas
─────────
1. CONTACT SCORE   – for every (position, rotation) candidate we compute how
                     much face area is in contact with truck walls or already-
                     placed boxes.  The placement with the MOST contact wins.
                     This minimises air gaps and hugs boxes together tightly.

2. RICH EXTREME POINTS – after each placement we add 3 classic EPs PLUS all
                     XY combinations that arise from intersecting the new
                     box's edges with existing boxes at every height level.
                     This gives the algorithm far more candidate positions to
                     evaluate, so it can "slide" boxes into gaps.

3. ORDERING        – boxes are sorted height-descending first (tall items
                     placed before short ones so short boxes can fill gaps on
                     top), then base-area descending within the same height.

4. CONSTRAINTS kept from previous version:
   • UPRIGHT ONLY   – declared height is always Z; boxes never tipped.
   • ROTATABLE flag – if False, only the original L×W orientation is tried.
   • STACKABLE flag – if False, nothing may rest on top of that box.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Set


# ── Data class ────────────────────────────────────────────────────────────────

@dataclass
class PackBox:
    uid:        str
    package_id: int
    name:       str
    length:     float
    width:      float
    height:     float
    weight:     float
    color:      str
    stackable:  bool
    rotatable:  bool

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    placed_l: float = 0.0
    placed_w: float = 0.0
    placed_h: float = 0.0
    placed: bool = False

    def to_dict(self):
        return {
            "uid": self.uid, "package_id": self.package_id,
            "name": self.name, "length": self.length,
            "width": self.width, "height": self.height,
            "weight": self.weight, "color": self.color,
            "stackable": self.stackable, "rotatable": self.rotatable,
            "x": self.x, "y": self.y, "z": self.z,
            "placed_l": self.placed_l, "placed_w": self.placed_w,
            "placed_h": self.placed_h, "placed": self.placed,
        }


# ── Rotations ─────────────────────────────────────────────────────────────────

def _rotations(l: float, w: float, rotatable: bool) -> List[Tuple[float, float]]:
    if not rotatable or abs(l - w) < 1e-9:
        return [(l, w)]
    return [(l, w), (w, l)]


# ── Geometry ──────────────────────────────────────────────────────────────────

EPS = 1e-9

def _overlap_1d(a0, a1, b0, b1) -> float:
    """Overlap length of two intervals; 0 if they don't overlap."""
    return max(0.0, min(a1, b1) - max(a0, b0))

def _overlaps_3d(ax, ay, az, al, aw, ah,
                 bx, by, bz, bl, bw, bh) -> bool:
    return (
        ax + al > bx + EPS and bx + bl > ax + EPS and
        ay + aw > by + EPS and by + bw > ay + EPS and
        az + ah > bz + EPS and bz + bh > az + EPS
    )

def _overlaps_xy(ax, ay, al, aw, bx, by, bl, bw) -> bool:
    return ax + al > bx + EPS and bx + bl > ax + EPS and \
           ay + aw > by + EPS and by + bw > ay + EPS


# ── Contact-maximisation score ────────────────────────────────────────────────

def _contact_score(px, py, pz, rl, rw, h,
                   truck_l, truck_w, truck_h,
                   placed: List[PackBox]) -> float:
    """
    Returns total face area in contact with truck walls or placed boxes.
    Higher = better packing (fewer air gaps).
    We return the NEGATIVE so that callers can use min() to pick the best.
    """
    contact = 0.0

    # ── Contact with the 5 closed truck surfaces ──────────────────────────────
    if pz < EPS:                          contact += rl * rw        # floor
    if px < EPS:                          contact += rw * h         # left wall
    if py < EPS:                          contact += rl * h         # rear wall
    if abs(px + rl - truck_l) < EPS:     contact += rw * h         # right wall
    if abs(py + rw - truck_w) < EPS:     contact += rl * h         # front wall
    # (no ceiling contact – truck is open-top for loading)

    # ── Contact with placed boxes ─────────────────────────────────────────────
    for p in placed:
        pl, pw, ph = p.placed_l, p.placed_w, p.placed_h

        # bottom face of new resting on top face of p
        if abs(pz - (p.z + ph)) < EPS:
            ox = _overlap_1d(px, px+rl, p.x, p.x+pl)
            oy = _overlap_1d(py, py+rw, p.y, p.y+pw)
            contact += ox * oy

        # top face of new touching bottom face of p  (rare but valid EP)
        if abs(pz + h - p.z) < EPS:
            ox = _overlap_1d(px, px+rl, p.x, p.x+pl)
            oy = _overlap_1d(py, py+rw, p.y, p.y+pw)
            contact += ox * oy

        # X-facing side contacts
        if abs(px - (p.x + pl)) < EPS:   # new left face touches p's right
            oy = _overlap_1d(py, py+rw, p.y, p.y+pw)
            oz = _overlap_1d(pz, pz+h,  p.z, p.z+ph)
            contact += oy * oz
        if abs(px + rl - p.x) < EPS:     # new right face touches p's left
            oy = _overlap_1d(py, py+rw, p.y, p.y+pw)
            oz = _overlap_1d(pz, pz+h,  p.z, p.z+ph)
            contact += oy * oz

        # Y-facing side contacts
        if abs(py - (p.y + pw)) < EPS:   # new rear face touches p's front
            ox = _overlap_1d(px, px+rl, p.x, p.x+pl)
            oz = _overlap_1d(pz, pz+h,  p.z, p.z+ph)
            contact += ox * oz
        if abs(py + rw - p.y) < EPS:     # new front face touches p's rear
            ox = _overlap_1d(px, px+rl, p.x, p.x+pl)
            oz = _overlap_1d(pz, pz+h,  p.z, p.z+ph)
            contact += ox * oz

    return -contact   # negate → callers use min()


# ── Placement validity ────────────────────────────────────────────────────────

def can_place(rl, rw, h, px, py, pz,
              truck_l, truck_w, truck_h,
              placed: List[PackBox]) -> bool:
    if px + rl > truck_l + EPS: return False
    if py + rw > truck_w + EPS: return False
    if pz + h  > truck_h + EPS: return False

    for p in placed:
        if _overlaps_3d(px, py, pz, rl, rw, h,
                        p.x, p.y, p.z, p.placed_l, p.placed_w, p.placed_h):
            return False
        if not p.stackable:
            p_top = p.z + p.placed_h
            if pz >= p_top - EPS:
                if _overlaps_xy(px, py, rl, rw,
                                p.x, p.y, p.placed_l, p.placed_w):
                    return False
    return True


# ── Extreme-point generator ───────────────────────────────────────────────────

def _generate_eps(placed: List[PackBox],
                  truck_l: float, truck_w: float, truck_h: float
                  ) -> List[Tuple[float, float, float]]:
    """
    Build a rich set of extreme points from all placed box corners.
    For every combination of (x-edge, y-edge, z-edge) from placed boxes
    (plus walls) we generate a candidate EP.  Points outside the truck
    or already inside a placed box are discarded.
    """
    # Collect unique coordinate values along each axis
    xs: Set[float] = {0.0}
    ys: Set[float] = {0.0}
    zs: Set[float] = {0.0}

    for p in placed:
        xs.add(p.x + p.placed_l)
        ys.add(p.y + p.placed_w)
        zs.add(p.z + p.placed_h)

    eps: List[Tuple[float, float, float]] = []

    for x in xs:
        for y in ys:
            for z in zs:
                if x >= truck_l - EPS: continue
                if y >= truck_w - EPS: continue
                if z >= truck_h - EPS: continue
                # Reject points that are strictly inside any placed box
                inside = False
                for p in placed:
                    if (p.x + EPS < x < p.x + p.placed_l - EPS and
                        p.y + EPS < y < p.y + p.placed_w - EPS and
                        p.z + EPS < z < p.z + p.placed_h - EPS):
                        inside = True
                        break
                if not inside:
                    eps.append((x, y, z))

    return eps


# ── Main packing routine ──────────────────────────────────────────────────────

def pack(truck_l: float, truck_w: float, truck_h: float,
         boxes: List[PackBox]) -> Tuple[List[PackBox], List[PackBox]]:

    placed:   List[PackBox] = []
    unpacked: List[PackBox] = []

    # Sort: tallest first (fills height layers cleanly), then largest base area
    order = sorted(
        boxes,
        key=lambda b: (round(b.height, 3), b.length * b.width),
        reverse=True,
    )

    for box in order:
        best_score = float("inf")   # lower (more negative) = more contact
        best_pos   = None
        best_rot   = None

        # Get candidate positions: origin + all rich EPs from placed boxes
        eps = [(0.0, 0.0, 0.0)] + _generate_eps(placed, truck_l, truck_w, truck_h)
        # Deduplicate
        eps = list(dict.fromkeys(eps))

        rots = _rotations(box.length, box.width, box.rotatable)

        for (px, py, pz) in eps:
            for (rl, rw) in rots:
                if can_place(rl, rw, box.height, px, py, pz,
                             truck_l, truck_w, truck_h, placed):
                    sc = _contact_score(px, py, pz, rl, rw, box.height,
                                        truck_l, truck_w, truck_h, placed)
                    if sc < best_score:
                        best_score = sc
                        best_pos   = (px, py, pz)
                        best_rot   = (rl, rw)

        if best_pos:
            px, py, pz = best_pos
            rl, rw     = best_rot
            box.x, box.y, box.z              = px, py, pz
            box.placed_l, box.placed_w, box.placed_h = rl, rw, box.height
            box.placed = True
            placed.append(box)
        else:
            unpacked.append(box)

    return placed, unpacked


# ── Public interface ──────────────────────────────────────────────────────────

def run_packing(
    truck_l: float, truck_w: float, truck_h: float,
    items: List[dict],
) -> Tuple[List[dict], List[dict], float]:

    boxes: List[PackBox] = []
    for item in items:
        for i in range(item["quantity"]):
            boxes.append(PackBox(
                uid        = f"pkg{item['package_id']}_{i}",
                package_id = item["package_id"],
                name       = item["name"],
                length     = item["length"],
                width      = item["width"],
                height     = item["height"],
                weight     = item.get("weight", 0),
                color      = item["color"],
                stackable  = item.get("stackable", True),
                rotatable  = item.get("rotatable", True),
            ))

    placed, unpacked = pack(truck_l, truck_w, truck_h, boxes)

    total_vol  = truck_l * truck_w * truck_h
    used_vol   = sum(b.placed_l * b.placed_w * b.placed_h for b in placed)
    efficiency = (used_vol / total_vol * 100) if total_vol > 0 else 0.0

    return (
        [b.to_dict() for b in placed],
        [b.to_dict() for b in unpacked],
        round(efficiency, 2),
    )
