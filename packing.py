"""
3D Bin Packing – Extreme Point Method.

Key rules enforced:
  • UPRIGHT ONLY  – boxes are never laid on their side; the declared
                    height always stays as the Z dimension.
  • STACKABLE     – if a box is marked stackable=False nothing may be
                    placed on top of it (its XY footprint above is blocked).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional


# ── Data class ────────────────────────────────────────────────────────────────

@dataclass
class PackBox:
    uid:        str
    package_id: int
    name:       str
    length:     float   # original declared length  (horizontal)
    width:      float   # original declared width   (horizontal)
    height:     float   # original declared height  (VERTICAL – never rotated)
    weight:     float
    color:      str
    stackable:  bool    # False → nothing may sit on top of this box

    # Filled after placement
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    placed_l: float = 0.0
    placed_w: float = 0.0
    placed_h: float = 0.0
    placed: bool = False

    def to_dict(self):
        return {
            "uid":        self.uid,
            "package_id": self.package_id,
            "name":       self.name,
            "length":     self.length,
            "width":      self.width,
            "height":     self.height,
            "weight":     self.weight,
            "color":      self.color,
            "stackable":  self.stackable,
            "x": self.x, "y": self.y, "z": self.z,
            "placed_l":   self.placed_l,
            "placed_w":   self.placed_w,
            "placed_h":   self.placed_h,
            "placed":     self.placed,
        }


# ── Upright-only rotations ────────────────────────────────────────────────────

def get_upright_rotations(l: float, w: float) -> List[Tuple[float, float]]:
    """
    Only rotate in the horizontal plane (XY).
    Height (Z) is always the declared height – boxes stay upright.
    Returns unique (rl, rw) pairs.
    """
    return list({(l, w), (w, l)})


# ── Geometry helpers ──────────────────────────────────────────────────────────

def _overlaps_xy(ax, ay, al, aw, bx, by, bl, bw) -> bool:
    """True if two rectangles overlap in the XY plane."""
    return not (ax + al <= bx or bx + bl <= ax or
                ay + aw <= by or by + bw <= ay)


def _overlaps_3d(ax, ay, az, al, aw, ah,
                 bx, by, bz, bl, bw, bh) -> bool:
    """True if two boxes share interior volume."""
    return not (
        ax + al <= bx or bx + bl <= ax or
        ay + aw <= by or by + bw <= ay or
        az + ah <= bz or bz + bh <= az
    )


def can_place(rl, rw, h, px, py, pz,
              truck_l, truck_w, truck_h,
              placed: List[PackBox]) -> bool:
    """
    Return True if a box of footprint (rl×rw) and height h can be
    placed at (px, py, pz) without:
      1. Leaving the truck bounds.
      2. Overlapping any already-placed box.
      3. Sitting on top of a non-stackable box.
    """
    EPS = 1e-9

    # 1. Truck bounds
    if px + rl > truck_l + EPS: return False
    if py + rw > truck_w + EPS: return False
    if pz + h  > truck_h + EPS: return False

    for p in placed:
        # 2. 3-D collision
        if _overlaps_3d(px, py, pz, rl, rw, h,
                        p.x, p.y, p.z, p.placed_l, p.placed_w, p.placed_h):
            return False

        # 3. Stackable constraint:
        #    If P is NOT stackable, no box may rest on top of it,
        #    i.e. the new box cannot start at P's top face (pz ≥ P.z + P.placed_h - EPS)
        #    while overlapping P in XY.
        if not p.stackable:
            p_top = p.z + p.placed_h
            if pz >= p_top - EPS:          # new box is at or above P's top
                if _overlaps_xy(px, py, rl, rw,
                                p.x, p.y, p.placed_l, p.placed_w):
                    return False

    return True


# ── Extreme-point bin packing ─────────────────────────────────────────────────

def pack(truck_l: float, truck_w: float, truck_h: float,
         boxes: List[PackBox]) -> Tuple[List[PackBox], List[PackBox]]:
    """
    Pack boxes using the Extreme Point heuristic.
    Returns (placed_boxes, unpacked_boxes).
    """
    placed:   List[PackBox] = []
    unpacked: List[PackBox] = []

    # Largest-volume-first ordering helps fill the truck efficiently
    order = sorted(boxes, key=lambda b: b.length * b.width * b.height, reverse=True)

    eps: List[Tuple[float, float, float]] = [(0.0, 0.0, 0.0)]

    def _add_ep(pt):
        if pt not in eps:
            eps.append(pt)

    for box in order:
        best_pos   = None
        best_rot   = None          # (rl, rw) – height is always box.height
        best_score = float("inf")

        rotations = get_upright_rotations(box.length, box.width)

        for ep in eps:
            px, py, pz = ep
            for rl, rw in rotations:
                if can_place(rl, rw, box.height, px, py, pz,
                             truck_l, truck_w, truck_h, placed):
                    # Score: prefer lower z first (fill bottom layers),
                    # then smaller x, then smaller y
                    score = pz * 1000 + px * 10 + py
                    if score < best_score:
                        best_score = score
                        best_pos   = ep
                        best_rot   = (rl, rw)

        if best_pos and best_rot:
            px, py, pz = best_pos
            rl, rw     = best_rot
            box.x, box.y, box.z        = px, py, pz
            box.placed_l, box.placed_w, box.placed_h = rl, rw, box.height
            box.placed = True
            placed.append(box)

            # Generate three new extreme points from the placed box corner
            _add_ep((px + rl, py,      pz         ))
            _add_ep((px,      py + rw, pz         ))
            _add_ep((px,      py,      pz + box.height))

            # Prune points outside truck (with tiny margin)
            eps[:] = [
                ep for ep in eps
                if ep[0] < truck_l - 1e-9
                and ep[1] < truck_w - 1e-9
                and ep[2] < truck_h - 1e-9
            ]
            # Sort: lowest z → smallest x → smallest y
            eps.sort(key=lambda p: p[2] * 1000 + p[0] * 10 + p[1])
        else:
            unpacked.append(box)

    return placed, unpacked


# ── Public interface ──────────────────────────────────────────────────────────

def run_packing(
    truck_l: float,
    truck_w: float,
    truck_h: float,
    items: List[dict],   # each dict has keys matching PackBox fields + "quantity"
) -> Tuple[List[dict], List[dict], float]:
    """
    Expand items by quantity, run packing, return
    (packed_dicts, unpacked_dicts, efficiency_pct).
    """
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
