"""
3D Bin Packing – Extreme Point + Contact Maximisation + Dual-Pass

The algorithm runs TWICE per packing request:
  Pass A – original box orientations tried first
  Pass B – rotated orientations tried first

Then it keeps whichever pass loaded more boxes (tie → better volume efficiency).
This guarantees we never miss a better rotation because the contact-area score
is symmetric (both rotations touch the same walls at position 0,0,0 with
equal area), which means a single-pass algorithm always picks the first
rotation in the list.

Constraints respected in both passes:
  • UPRIGHT ONLY  – declared height stays as Z; boxes are never tipped.
  • ROTATABLE     – if False, only original L×W orientation is tried (passes are
                    identical for non-rotatable boxes – no wasted work).
  • STACKABLE     – if False, nothing may rest on top of that box.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import copy

EPS = 1e-9


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

    def reset(self):
        self.x = self.y = self.z = 0.0
        self.placed_l = self.placed_w = self.placed_h = 0.0
        self.placed = False


# ── Rotations ─────────────────────────────────────────────────────────────────

def _rotations(l: float, w: float,
               rotatable: bool,
               prefer_rotated: bool) -> List[Tuple[float, float]]:
    """
    Returns the list of (length, width) orientations to try.
    prefer_rotated=True means we try (w, l) before (l, w).
    For non-rotatable boxes returns a single-element list regardless.
    """
    if not rotatable or abs(l - w) < EPS:
        return [(l, w)]
    if prefer_rotated:
        return [(w, l), (l, w)]
    return [(l, w), (w, l)]


# ── Geometry ──────────────────────────────────────────────────────────────────

def _ov1d(a0, a1, b0, b1) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))

def _overlaps_3d(ax, ay, az, al, aw, ah,
                 bx, by, bz, bl, bw, bh) -> bool:
    return (ax + al > bx + EPS and bx + bl > ax + EPS and
            ay + aw > by + EPS and by + bw > ay + EPS and
            az + ah > bz + EPS and bz + bh > az + EPS)

def _overlaps_xy(ax, ay, al, aw, bx, by, bl, bw) -> bool:
    return (ax + al > bx + EPS and bx + bl > ax + EPS and
            ay + aw > by + EPS and by + bw > ay + EPS)


# ── Contact-area score (higher = better packing) ──────────────────────────────

def _contact(px, py, pz, rl, rw, h,
             truck_l, truck_w, truck_h,
             placed: List[PackBox]) -> float:
    c = 0.0
    if pz          < EPS: c += rl * rw
    if px          < EPS: c += rw * h
    if py          < EPS: c += rl * h
    if abs(px+rl - truck_l) < EPS: c += rw * h
    if abs(py+rw - truck_w) < EPS: c += rl * h

    for p in placed:
        pl, pw, ph = p.placed_l, p.placed_w, p.placed_h
        if abs(pz      - (p.z+ph)) < EPS:
            c += _ov1d(px,px+rl,p.x,p.x+pl) * _ov1d(py,py+rw,p.y,p.y+pw)
        if abs(pz+h    -  p.z    ) < EPS:
            c += _ov1d(px,px+rl,p.x,p.x+pl) * _ov1d(py,py+rw,p.y,p.y+pw)
        if abs(px      - (p.x+pl)) < EPS:
            c += _ov1d(py,py+rw,p.y,p.y+pw) * _ov1d(pz,pz+h, p.z,p.z+ph)
        if abs(px+rl   -  p.x    ) < EPS:
            c += _ov1d(py,py+rw,p.y,p.y+pw) * _ov1d(pz,pz+h, p.z,p.z+ph)
        if abs(py      - (p.y+pw)) < EPS:
            c += _ov1d(px,px+rl,p.x,p.x+pl) * _ov1d(pz,pz+h, p.z,p.z+ph)
        if abs(py+rw   -  p.y    ) < EPS:
            c += _ov1d(px,px+rl,p.x,p.x+pl) * _ov1d(pz,pz+h, p.z,p.z+ph)
    return c


# ── Waste ratio (lower = better: fewer leftover gaps when tiling) ─────────────

def _waste(rl, rw, px, py, truck_l, truck_w) -> float:
    """
    Fractional wasted space when tiling this rotation in the remaining area.
    0.0 means the box divides the remaining space exactly.
    """
    rem_l = truck_l - px
    rem_w = truck_w - py
    if rem_l < EPS or rem_w < EPS:
        return 1.0
    wl = (rem_l % rl) / rem_l if rl > EPS else 0.0
    ww = (rem_w % rw) / rem_w if rw > EPS else 0.0
    return wl + ww


# ── Combined score tuple (for min() selection) ────────────────────────────────

def _score(px, py, pz, rl, rw, h,
           truck_l, truck_w, truck_h,
           placed: List[PackBox]) -> tuple:
    """
    Tuple compared lexicographically via min():
      (-contact, waste, pz, px, py)
    → maximise contact, then minimise waste, then prefer low positions.
    """
    ca = _contact(px, py, pz, rl, rw, h, truck_l, truck_w, truck_h, placed)
    wt = _waste(rl, rw, px, py, truck_l, truck_w)
    return (-ca, wt, pz, px, py)


# ── Placement validity ────────────────────────────────────────────────────────

def _can_place(rl, rw, h, px, py, pz,
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
            if pz >= (p.z + p.placed_h) - EPS:
                if _overlaps_xy(px, py, rl, rw,
                                p.x, p.y, p.placed_l, p.placed_w):
                    return False
    return True


# ── Extreme point update ──────────────────────────────────────────────────────

def _add_eps(eps: set, px, py, pz, rl, rw, h,
             truck_l, truck_w, truck_h,
             placed: List[PackBox]):
    """
    Classic 3-EP plus cross-coordinate candidates at current Z levels.
    """
    candidates = [
        (px + rl, py,      pz     ),
        (px,      py + rw, pz     ),
        (px,      py,      pz + h ),
    ]
    # Cross-products of all existing edges at the same Z layers
    xs = {0.0} | {p.x + p.placed_l for p in placed}
    ys = {0.0} | {p.y + p.placed_w for p in placed}
    for zl in {0.0, pz, pz + h}:
        for x in xs:
            for y in ys:
                candidates.append((x, y, zl))

    for pt in candidates:
        x, y, z = pt
        if (x < truck_l - EPS and
            y < truck_w - EPS and
            z < truck_h - EPS):
            eps.add(pt)


# ── Single-pass packer ────────────────────────────────────────────────────────

def _pack_once(truck_l: float, truck_w: float, truck_h: float,
               boxes: List[PackBox],
               prefer_rotated: bool) -> Tuple[List[PackBox], List[PackBox]]:
    """
    One pass of the EP algorithm.
    prefer_rotated controls which orientation is tried first.
    Returns (placed, unpacked).
    """
    # Deep-copy so we can run multiple passes without state pollution
    boxes = [copy.copy(b) for b in boxes]
    for b in boxes:
        b.reset()

    placed:   List[PackBox] = []
    unpacked: List[PackBox] = []

    # Largest-volume-first ordering
    order = sorted(boxes,
                   key=lambda b: b.length * b.width * b.height,
                   reverse=True)

    eps: set = {(0.0, 0.0, 0.0)}

    for box in order:
        best_score = None
        best_pos   = None
        best_rot   = None

        rots = _rotations(box.length, box.width, box.rotatable, prefer_rotated)

        for (px, py, pz) in list(eps):
            for (rl, rw) in rots:
                if _can_place(rl, rw, box.height, px, py, pz,
                              truck_l, truck_w, truck_h, placed):
                    sc = _score(px, py, pz, rl, rw, box.height,
                                truck_l, truck_w, truck_h, placed)
                    if best_score is None or sc < best_score:
                        best_score = sc
                        best_pos   = (px, py, pz)
                        best_rot   = (rl, rw)

        if best_pos is not None:
            px, py, pz = best_pos
            rl, rw     = best_rot
            box.x, box.y, box.z              = px, py, pz
            box.placed_l, box.placed_w, box.placed_h = rl, rw, box.height
            box.placed = True
            placed.append(box)
            eps.discard(best_pos)
            _add_eps(eps, px, py, pz, rl, rw, box.height,
                     truck_l, truck_w, truck_h, placed)
        else:
            unpacked.append(box)

    return placed, unpacked


# ── Dual-pass main entry ──────────────────────────────────────────────────────

def pack(truck_l: float, truck_w: float, truck_h: float,
         boxes: List[PackBox]) -> Tuple[List[PackBox], List[PackBox]]:
    """
    Run the packer twice (original orientation first vs rotated first)
    and return whichever result fits more boxes.
    Tie on count → prefer higher volume utilisation.
    """
    placed_a, unpacked_a = _pack_once(truck_l, truck_w, truck_h, boxes, prefer_rotated=False)
    placed_b, unpacked_b = _pack_once(truck_l, truck_w, truck_h, boxes, prefer_rotated=True)

    vol_a = sum(b.placed_l * b.placed_w * b.placed_h for b in placed_a)
    vol_b = sum(b.placed_l * b.placed_w * b.placed_h for b in placed_b)

    # Primary: more boxes loaded; secondary: better volume
    if len(placed_b) > len(placed_a):
        return placed_b, unpacked_b
    elif len(placed_a) > len(placed_b):
        return placed_a, unpacked_a
    else:
        return (placed_b, unpacked_b) if vol_b >= vol_a else (placed_a, unpacked_a)


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
