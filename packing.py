"""
3D Bin Packing – Extreme Point Method with column-preference scoring.

Rules enforced:
  • UPRIGHT ONLY  – declared height always stays as Z (boxes never tipped).
  • ROTATABLE     – if rotatable=False the box can only sit in its original
                    L×W orientation (no 90° horizontal spin).
  • STACKABLE     – if stackable=False nothing may be placed on top of it.
  • STACKING      – the scoring function strongly prefers positions that are
                    directly above an existing box ("continue a column")
                    before opening a new floor position.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple


# ── Data class ────────────────────────────────────────────────────────────────

@dataclass
class PackBox:
    uid:        str
    package_id: int
    name:       str
    length:     float   # declared length  (horizontal, never becomes Z)
    width:      float   # declared width   (horizontal, never becomes Z)
    height:     float   # declared height  (always Z)
    weight:     float
    color:      str
    stackable:  bool    # False → nothing may rest on top of this box
    rotatable:  bool    # False → cannot rotate 90° in the horizontal plane

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
            "rotatable":  self.rotatable,
            "x": self.x, "y": self.y, "z": self.z,
            "placed_l":   self.placed_l,
            "placed_w":   self.placed_w,
            "placed_h":   self.placed_h,
            "placed":     self.placed,
        }


# ── Horizontal rotations (height never changes) ───────────────────────────────

def get_rotations(l: float, w: float, rotatable: bool) -> List[Tuple[float, float]]:
    """
    Returns the list of valid (length, width) orientations for a box.
    If rotatable=False, only the original orientation is returned.
    """
    if not rotatable or abs(l - w) < 1e-9:
        return [(l, w)]
    return [(l, w), (w, l)]


# ── Geometry ──────────────────────────────────────────────────────────────────

def _overlaps_xy(ax, ay, al, aw, bx, by, bl, bw) -> bool:
    return not (ax + al <= bx or bx + bl <= ax or
                ay + aw <= by or by + bw <= ay)


def _overlaps_3d(ax, ay, az, al, aw, ah,
                 bx, by, bz, bl, bw, bh) -> bool:
    return not (
        ax + al <= bx or bx + bl <= ax or
        ay + aw <= by or by + bw <= ay or
        az + ah <= bz or bz + bh <= az
    )


def _is_on_top_of(px, py, pz, placed: List[PackBox]) -> bool:
    """
    True if point (px,py,pz) sits exactly on the top face of some
    already-placed box (i.e. this is a legitimate stacking position,
    not a floating position).
    The extreme-point method only generates z-level EPs from box tops,
    so this check also guards against numeric-drift false-positives.
    """
    if pz < 1e-9:
        return False   # on the truck floor – not stacking
    EPS = 1e-6
    for p in placed:
        if abs(p.z + p.placed_h - pz) < EPS:
            # the candidate sits at the top surface of p;
            # check that the x,y start matches (exact EP match)
            if abs(p.x - px) < EPS and abs(p.y - py) < EPS:
                return True
    return False


def can_place(rl, rw, h, px, py, pz,
              truck_l, truck_w, truck_h,
              placed: List[PackBox]) -> bool:
    """
    Return True if a box with footprint rl×rw and height h can be
    placed at (px, py, pz) respecting:
      1. Truck bounds.
      2. No 3D overlap with already-placed boxes.
      3. Stackable constraint (nothing above a non-stackable box).
    """
    EPS = 1e-9

    # 1. Bounds
    if px + rl > truck_l + EPS: return False
    if py + rw > truck_w + EPS: return False
    if pz + h  > truck_h + EPS: return False

    for p in placed:
        # 2. Collision
        if _overlaps_3d(px, py, pz, rl, rw, h,
                        p.x, p.y, p.z, p.placed_l, p.placed_w, p.placed_h):
            return False

        # 3. Non-stackable: block anything above this box's footprint
        if not p.stackable:
            p_top = p.z + p.placed_h
            if pz >= p_top - EPS:
                if _overlaps_xy(px, py, rl, rw,
                                p.x, p.y, p.placed_l, p.placed_w):
                    return False

    return True


# ── Scoring ───────────────────────────────────────────────────────────────────

def _score(px, py, pz, placed: List[PackBox]) -> float:
    """
    Column-preference scoring:

      ① Directly above an existing box ("continue a column"):
            score = px*0.5 + py*0.05 + pz*0.1
         → very low numbers → strongly preferred

      ② On the truck floor (pz ≈ 0):
            score = 10 + px*2 + py*0.2
         → slightly higher than column-continuation

      ③ Any other elevated position (unsupported / new height):
            score = 500 + pz*100 + px*2 + py*0.2
         → effectively avoided; only happens when floor is full
           and no column top is available

    Result: the algorithm builds columns upward before spreading
    on the floor, while still filling the floor left-to-right.
    """
    if _is_on_top_of(px, py, pz, placed):
        # ① Continue an existing column — almost free
        return px * 0.5 + py * 0.05 + pz * 0.1

    if pz < 1e-9:
        # ② New floor position
        return 10 + px * 2 + py * 0.2

    # ③ Elevated but not directly above a known box
    return 500 + pz * 100 + px * 2 + py * 0.2


# ── Extreme-point packing ─────────────────────────────────────────────────────

def pack(truck_l: float, truck_w: float, truck_h: float,
         boxes: List[PackBox]) -> Tuple[List[PackBox], List[PackBox]]:
    """
    Pack boxes using the Extreme Point heuristic.
    Returns (placed_boxes, unpacked_boxes).
    """
    placed:   List[PackBox] = []
    unpacked: List[PackBox] = []

    # Largest-volume-first so big boxes anchor the layout
    order = sorted(boxes, key=lambda b: b.length * b.width * b.height, reverse=True)

    eps: List[Tuple[float, float, float]] = [(0.0, 0.0, 0.0)]

    def _add_ep(pt):
        if pt not in eps:
            eps.append(pt)

    for box in order:
        best_pos   = None
        best_rot   = None
        best_score = float("inf")

        rotations = get_rotations(box.length, box.width, box.rotatable)

        for ep in eps:
            px, py, pz = ep
            for rl, rw in rotations:
                if can_place(rl, rw, box.height, px, py, pz,
                             truck_l, truck_w, truck_h, placed):
                    sc = _score(px, py, pz, placed)
                    if sc < best_score:
                        best_score = sc
                        best_pos   = ep
                        best_rot   = (rl, rw)

        if best_pos and best_rot:
            px, py, pz = best_pos
            rl, rw     = best_rot
            box.x, box.y, box.z              = px, py, pz
            box.placed_l, box.placed_w, box.placed_h = rl, rw, box.height
            box.placed = True
            placed.append(box)

            # Three new extreme points from the top-right-front corner
            _add_ep((px + rl, py,      pz            ))
            _add_ep((px,      py + rw, pz            ))
            _add_ep((px,      py,      pz + box.height))

            # Prune points that are outside the truck
            eps[:] = [
                ep for ep in eps
                if ep[0] < truck_l - 1e-9
                and ep[1] < truck_w - 1e-9
                and ep[2] < truck_h - 1e-9
            ]
            # Sort so column-top EPs come first in the iteration
            eps.sort(key=lambda p: _score(p[0], p[1], p[2], placed))
        else:
            unpacked.append(box)

    return placed, unpacked


# ── Public interface ──────────────────────────────────────────────────────────

def run_packing(
    truck_l: float,
    truck_w: float,
    truck_h: float,
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
