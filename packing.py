"""
3D Bin Packing – Extreme Point + Contact Maximisation + PackVol-style rules

Per-box rules (stored in DB, passed via items dict):
  stackable     – False → nothing may rest on top of this box
  rotatable     – False → only original L×W orientation tried
  position_rule – "any"        : no restriction
                  "floor_only" : must sit on truck floor (z ≈ 0)
                  "top_only"   : must rest on top of another box (z > 0)
                  "no_floor"   : same as top_only
  load_priority – 1 (placed last / deepest) … 10 (placed first / near door)

Plan-level options (passed to run_packing):
  loading_dir    – "front_back" : fill from x=0 → truck_l (default)
                   "back_front" : fill from x=truck_l → 0
                   Implementation: always pack front_back internally,
                   then MIRROR all x coords if back_front requested.
                   This is exact and avoids EP-seed issues.
  prefer_columns – True: reward stacking same package_id in columns

Algorithm: dual-pass (original orientation first vs rotated first) keeping
the pass that fits more boxes.  Height is always the Z axis (upright).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import copy

EPS = 1e-9


# ── Data class ────────────────────────────────────────────────────────────────

@dataclass
class PackBox:
    uid:           str
    package_id:    int
    name:          str
    length:        float
    width:         float
    height:        float
    weight:        float
    color:         str
    stackable:     bool
    rotatable:     bool
    position_rule: str   # "any" | "floor_only" | "top_only" | "no_floor"
    load_priority: int   # 1–10

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
            "position_rule": self.position_rule,
            "load_priority": self.load_priority,
            "x": self.x, "y": self.y, "z": self.z,
            "placed_l": self.placed_l, "placed_w": self.placed_w,
            "placed_h": self.placed_h, "placed": self.placed,
        }

    def reset(self):
        self.x = self.y = self.z = 0.0
        self.placed_l = self.placed_w = self.placed_h = 0.0
        self.placed = False


# ── Rotations ─────────────────────────────────────────────────────────────────

def _rotations(l, w, rotatable, prefer_rotated) -> List[Tuple[float, float]]:
    if not rotatable or abs(l - w) < EPS:
        return [(l, w)]
    return [(w, l), (l, w)] if prefer_rotated else [(l, w), (w, l)]


# ── Geometry ──────────────────────────────────────────────────────────────────

def _ov1d(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))

def _overlaps_3d(ax,ay,az,al,aw,ah, bx,by,bz,bl,bw,bh):
    return (ax+al>bx+EPS and bx+bl>ax+EPS and
            ay+aw>by+EPS and by+bw>ay+EPS and
            az+ah>bz+EPS and bz+bh>az+EPS)

def _overlaps_xy(ax,ay,al,aw, bx,by,bl,bw):
    return (ax+al>bx+EPS and bx+bl>ax+EPS and
            ay+aw>by+EPS and by+bw>ay+EPS)

def _has_support(px,py,pz,rl,rw, placed) -> bool:
    """True if box footprint is on the floor or resting on a placed box."""
    if pz < EPS:
        return True
    for p in placed:
        if abs(p.z+p.placed_h-pz) < EPS:
            if _overlaps_xy(px,py,rl,rw, p.x,p.y,p.placed_l,p.placed_w):
                return True
    return False


# ── Position-rule check ───────────────────────────────────────────────────────

def _position_ok(rule, px,py,pz,rl,rw,h, placed) -> bool:
    if rule == "floor_only":
        return pz < EPS
    if rule in ("top_only", "no_floor"):
        return pz > EPS and _has_support(px,py,pz,rl,rw, placed)
    return True


# ── Placement validity ────────────────────────────────────────────────────────

def _can_place(rl,rw,h, px,py,pz, truck_l,truck_w,truck_h,
               placed, box) -> bool:
    if px+rl > truck_l+EPS: return False
    if py+rw > truck_w+EPS: return False
    if pz+h  > truck_h+EPS: return False
    if not _position_ok(box.position_rule,px,py,pz,rl,rw,h, placed):
        return False
    for p in placed:
        if _overlaps_3d(px,py,pz,rl,rw,h,
                        p.x,p.y,p.z,p.placed_l,p.placed_w,p.placed_h):
            return False
        if not p.stackable:
            if pz >= (p.z+p.placed_h)-EPS:
                if _overlaps_xy(px,py,rl,rw, p.x,p.y,p.placed_l,p.placed_w):
                    return False
    return True


# ── Contact area (higher = better) ───────────────────────────────────────────

def _contact(px,py,pz,rl,rw,h, truck_l,truck_w,truck_h, placed) -> float:
    c = 0.0
    if pz          < EPS: c += rl*rw
    if px          < EPS: c += rw*h
    if py          < EPS: c += rl*h
    if abs(px+rl-truck_l)<EPS: c += rw*h
    if abs(py+rw-truck_w)<EPS: c += rl*h
    for p in placed:
        pl,pw,ph = p.placed_l,p.placed_w,p.placed_h
        if abs(pz-(p.z+ph))<EPS:
            c += _ov1d(px,px+rl,p.x,p.x+pl)*_ov1d(py,py+rw,p.y,p.y+pw)
        if abs(pz+h-p.z)<EPS:
            c += _ov1d(px,px+rl,p.x,p.x+pl)*_ov1d(py,py+rw,p.y,p.y+pw)
        if abs(px-(p.x+pl))<EPS:
            c += _ov1d(py,py+rw,p.y,p.y+pw)*_ov1d(pz,pz+h,p.z,p.z+ph)
        if abs(px+rl-p.x)<EPS:
            c += _ov1d(py,py+rw,p.y,p.y+pw)*_ov1d(pz,pz+h,p.z,p.z+ph)
        if abs(py-(p.y+pw))<EPS:
            c += _ov1d(px,px+rl,p.x,p.x+pl)*_ov1d(pz,pz+h,p.z,p.z+ph)
        if abs(py+rw-p.y)<EPS:
            c += _ov1d(px,px+rl,p.x,p.x+pl)*_ov1d(pz,pz+h,p.z,p.z+ph)
    return c


# ── Score tuple (for min()) – WALL-FIRST approach ────────────────────────────
#
# Priority:
#   1. Minimum X  → never advance in length until current "wall" is full
#   2. Minimum Z  → fill floor before stacking
#   3. Minimum Y  → fill width left-to-right
#   4. Max contact → tiebreaker for identical positions
#
# Removing _waste entirely: that function was rewarding rotations that divide
# remaining space cleanly, which caused the staircase/gap-filling pattern.
# Now the algorithm only rotates if both orientations share the same X slot;
# it never rotates just to plug a lengthwise gap.

def _score(px, py, pz, rl, rw, h, truck_l, truck_w, truck_h,
           placed, box, prefer_columns) -> tuple:

    ca = _contact(px, py, pz, rl, rw, h, truck_l, truck_w, truck_h, placed)

    if prefer_columns and pz > EPS:
        for p in placed:
            if p.package_id == box.package_id and abs(p.z + p.placed_h - pz) < EPS:
                ca += (_ov1d(px, px+rl, p.x, p.x+p.placed_l) *
                       _ov1d(py, py+rw, p.y, p.y+p.placed_w) * 3.0)

    # Round X to 3 decimal places so floating-point noise doesn't break grouping
    return (round(px, 3), pz, round(py, 3), -ca)


# ── EP generation ─────────────────────────────────────────────────────────────

def _add_eps(eps:set, px,py,pz,rl,rw,h, truck_l,truck_w,truck_h, placed):
    xs = {0.0} | {p.x+p.placed_l for p in placed}
    ys = {0.0} | {p.y+p.placed_w for p in placed}
    cands = [(px+rl,py,pz),(px,py+rw,pz),(px,py,pz+h)]
    for zl in {0.0, pz, pz+h}:
        for x in xs:
            for y in ys:
                cands.append((x,y,zl))
    for (x,y,z) in cands:
        if x<truck_l-EPS and y<truck_w-EPS and z<truck_h-EPS:
            eps.add((x,y,z))


# ── Single-pass packer (always fills front→back, i.e. from x=0) ──────────────

def _pack_once(truck_l,truck_w,truck_h, boxes,
               prefer_rotated, prefer_columns) -> Tuple[list,list]:

    boxes = [copy.copy(b) for b in boxes]
    for b in boxes: b.reset()

    # Higher priority placed first (will end up at low x = near x=0).
    # After optional X-mirror, high-priority items end up near the door.
    order = sorted(boxes,
                   key=lambda b: (b.load_priority,
                                  b.length*b.width*b.height),
                   reverse=True)

    placed = []
    unpacked = []
    eps: set = {(0.0,0.0,0.0)}

    for box in order:
        best_score = None
        best_pos   = None
        best_rot   = None

        rots = _rotations(box.length,box.width,box.rotatable,prefer_rotated)

        for (px,py,pz) in list(eps):
            for (rl,rw) in rots:
                if _can_place(rl,rw,box.height,px,py,pz,
                              truck_l,truck_w,truck_h,placed,box):
                    sc = _score(px,py,pz,rl,rw,box.height,
                                truck_l,truck_w,truck_h,
                                placed,box,prefer_columns)
                    if best_score is None or sc < best_score:
                        best_score = sc
                        best_pos   = (px,py,pz)
                        best_rot   = (rl,rw)

        if best_pos is not None:
            px,py,pz = best_pos
            rl,rw    = best_rot
            box.x,box.y,box.z              = px,py,pz
            box.placed_l,box.placed_w,box.placed_h = rl,rw,box.height
            box.placed = True
            placed.append(box)
            eps.discard(best_pos)
            _add_eps(eps,px,py,pz,rl,rw,box.height,
                     truck_l,truck_w,truck_h,placed)
        else:
            unpacked.append(box)

    return placed, unpacked


# ── X-mirror transform ────────────────────────────────────────────────────────

def _mirror_x(placed, truck_l):
    """
    Reflect all placed boxes along the X axis:
        x_real = truck_l - x_packed - placed_l
    Used to convert a front→back result into a back→front result.
    High-priority boxes (placed first, near x=0) end up near x=truck_l
    (the door/rear of the truck) — exactly what we want for back_front.
    Non-overlap and upright constraints are preserved by the reflection.
    """
    for b in placed:
        b.x = truck_l - b.x - b.placed_l


# ── Dual-pass entry ───────────────────────────────────────────────────────────

def pack(truck_l,truck_w,truck_h, boxes,
         loading_dir="front_back", prefer_columns=False):

    placed_a,unpacked_a = _pack_once(truck_l,truck_w,truck_h,boxes,
                                     False,prefer_columns)
    placed_b,unpacked_b = _pack_once(truck_l,truck_w,truck_h,boxes,
                                     True, prefer_columns)

    vol_a = sum(b.placed_l*b.placed_w*b.placed_h for b in placed_a)
    vol_b = sum(b.placed_l*b.placed_w*b.placed_h for b in placed_b)

    if len(placed_b) > len(placed_a):
        best_placed, best_unpacked = placed_b, unpacked_b
    elif len(placed_a) > len(placed_b):
        best_placed, best_unpacked = placed_a, unpacked_a
    else:
        best_placed, best_unpacked = (
            (placed_b, unpacked_b) if vol_b >= vol_a else (placed_a, unpacked_a)
        )

    if loading_dir == "back_front":
        _mirror_x(best_placed, truck_l)

    return best_placed, best_unpacked


# ── Public interface ──────────────────────────────────────────────────────────

def run_packing(truck_l, truck_w, truck_h, items,
                loading_dir="front_back",
                prefer_columns=False):

    boxes = []
    for item in items:
        for i in range(item["quantity"]):
            boxes.append(PackBox(
                uid           = f"pkg{item['package_id']}_{i}",
                package_id    = item["package_id"],
                name          = item["name"],
                length        = item["length"],
                width         = item["width"],
                height        = item["height"],
                weight        = item.get("weight", 0),
                color         = item["color"],
                stackable     = item.get("stackable", True),
                rotatable     = item.get("rotatable", True),
                position_rule = item.get("position_rule", "any"),
                load_priority = item.get("load_priority", 5),
            ))

    placed, unpacked = pack(truck_l,truck_w,truck_h,boxes,
                            loading_dir=loading_dir,
                            prefer_columns=prefer_columns)

    total_vol  = truck_l*truck_w*truck_h
    used_vol   = sum(b.placed_l*b.placed_w*b.placed_h for b in placed)
    efficiency = (used_vol/total_vol*100) if total_vol>0 else 0.0

    return (
        [b.to_dict() for b in placed],
        [b.to_dict() for b in unpacked],
        round(efficiency,2),
    )
