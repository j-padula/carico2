"""
3D Bin Packing - Extreme Point Method with all 6 rotations.
Maximises truck utilisation by trying every rotation at every
extreme point and choosing the position closest to the truck origin.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import copy


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class PackBox:
    uid: str          # unique id per box instance, e.g. "pkg3_0"
    package_id: int
    name: str
    length: float
    width: float
    height: float
    weight: float
    color: str

    # filled after placement
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    placed_l: float = 0.0
    placed_w: float = 0.0
    placed_h: float = 0.0
    placed: bool = False

    def to_dict(self):
        return {
            "uid": self.uid,
            "package_id": self.package_id,
            "name": self.name,
            "length": self.length,
            "width": self.width,
            "height": self.height,
            "weight": self.weight,
            "color": self.color,
            "x": self.x, "y": self.y, "z": self.z,
            "placed_l": self.placed_l,
            "placed_w": self.placed_w,
            "placed_h": self.placed_h,
            "placed": self.placed,
        }


# ── Rotation helpers ──────────────────────────────────────────────────────────

def get_rotations(l: float, w: float, h: float) -> List[Tuple[float, float, float]]:
    """Return unique (l,w,h) tuples for all 6 orientations."""
    return list({
        (l, w, h), (l, h, w),
        (w, l, h), (w, h, l),
        (h, l, w), (h, w, l),
    })


# ── Collision / boundary checks ───────────────────────────────────────────────

def _overlaps(ax, ay, az, al, aw, ah,
               bx, by, bz, bl, bw, bh) -> bool:
    """True if two boxes overlap (share interior volume)."""
    return not (
        ax + al <= bx or bx + bl <= ax or
        ay + aw <= by or by + bw <= ay or
        az + ah <= bz or bz + bh <= az
    )


def can_place(bl, bw, bh, px, py, pz,
              truck_l, truck_w, truck_h,
              placed: List[PackBox]) -> bool:
    if px + bl > truck_l + 1e-9:
        return False
    if py + bw > truck_w + 1e-9:
        return False
    if pz + bh > truck_h + 1e-9:
        return False
    for p in placed:
        if _overlaps(px, py, pz, bl, bw, bh,
                     p.x, p.y, p.z, p.placed_l, p.placed_w, p.placed_h):
            return False
    return True


# ── Extreme-point bin packing ─────────────────────────────────────────────────

def pack(truck_l: float, truck_w: float, truck_h: float,
         boxes: List[PackBox]) -> Tuple[List[PackBox], List[PackBox]]:
    """
    Pack boxes into a truck using the Extreme Point method.
    Returns (placed_boxes, unpacked_boxes).
    """
    placed: List[PackBox] = []
    unpacked: List[PackBox] = []

    # Sort by volume descending so big boxes go first
    order = sorted(boxes, key=lambda b: b.length * b.width * b.height, reverse=True)

    # Extreme points initialised at the rear-bottom-left corner
    eps: List[Tuple[float, float, float]] = [(0.0, 0.0, 0.0)]

    def _add_ep(pt):
        if pt not in eps:
            eps.append(pt)

    for box in order:
        best_pos   = None
        best_rot   = None
        best_score = float("inf")

        rotations = get_rotations(box.length, box.width, box.height)

        for ep in eps:
            px, py, pz = ep
            for rot in rotations:
                rl, rw, rh = rot
                if can_place(rl, rw, rh, px, py, pz,
                             truck_l, truck_w, truck_h, placed):
                    # Scoring: prefer low-z (height) first, then x, then y
                    score = pz * 10 + px + py
                    if score < best_score:
                        best_score = score
                        best_pos   = ep
                        best_rot   = rot

        if best_pos and best_rot:
            px, py, pz       = best_pos
            rl, rw, rh       = best_rot
            box.x, box.y, box.z = px, py, pz
            box.placed_l, box.placed_w, box.placed_h = rl, rw, rh
            box.placed = True
            placed.append(box)

            # Three new extreme points generated from the placed corner
            _add_ep((px + rl, py,      pz     ))
            _add_ep((px,      py + rw, pz     ))
            _add_ep((px,      py,      pz + rh))

            # Prune extreme points outside truck bounds
            eps[:] = [
                ep for ep in eps
                if ep[0] < truck_l - 1e-9
                and ep[1] < truck_w - 1e-9
                and ep[2] < truck_h - 1e-9
            ]
            eps.sort(key=lambda p: p[2] * 10 + p[0] + p[1])
        else:
            unpacked.append(box)

    return placed, unpacked


# ── Public interface ──────────────────────────────────────────────────────────

def run_packing(truck_l: float, truck_w: float, truck_h: float,
                items: List[dict],          # [{package_id, name, length, width, height, weight, color, quantity}, ...]
                ) -> Tuple[List[dict], List[dict], float]:
    """
    Build box instances from items (respecting quantity), run packing,
    and return (packed_dicts, unpacked_dicts, efficiency_pct).
    """
    boxes: List[PackBox] = []
    for item in items:
        for i in range(item["quantity"]):
            uid = f"pkg{item['package_id']}_{i}"
            boxes.append(PackBox(
                uid        = uid,
                package_id = item["package_id"],
                name       = item["name"],
                length     = item["length"],
                width      = item["width"],
                height     = item["height"],
                weight     = item.get("weight", 0),
                color      = item["color"],
            ))

    placed, unpacked = pack(truck_l, truck_w, truck_h, boxes)

    total_vol = truck_l * truck_w * truck_h
    used_vol  = sum(b.placed_l * b.placed_w * b.placed_h for b in placed)
    efficiency = (used_vol / total_vol * 100) if total_vol > 0 else 0.0

    return (
        [b.to_dict() for b in placed],
        [b.to_dict() for b in unpacked],
        round(efficiency, 2),
    )
