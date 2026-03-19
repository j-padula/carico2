"""
3D Bin Packing – Extreme Point, Wall-First scoring, Per-Orientation rules.

Per-orientation rules (orient_rules dict on each box):
  "A" → original orientation (length × width)
  "B" → rotated 90°        (width  × length)

  Each value: "disabled" | "any" | "floor_only" | "top_only" | "no_floor"

Plan-level options:
  loading_dir    – "front_back" | "back_front"
  prefer_columns – bool

Scoring: wall-first (fill width/height before advancing in length).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import copy

EPS = 1e-9


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
    orient_rules:  Dict[str, str]   # {"A": rule, "B": rule}
    load_priority: int

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
            "name": self.name,
            "length": self.length, "width": self.width, "height": self.height,
            "weight": self.weight, "color": self.color,
            "stackable": self.stackable, "rotatable": self.rotatable,
            "orient_rules": self.orient_rules,
            "load_priority": self.load_priority,
            "x": self.x, "y": self.y, "z": self.z,
            "placed_l": self.placed_l, "placed_w": self.placed_w,
            "placed_h": self.placed_h, "placed": self.placed,
        }

    def reset(self):
        self.x = self.y = self.z = 0.0
        self.placed_l = self.placed_w = self.placed_h = 0.0
        self.placed = False


# ── Orientations with per-rule ────────────────────────────────────────────────

def _get_orientations(box: PackBox, prefer_rotated: bool) -> List[Tuple[float, float, str]]:
    """
    Returns list of (rl, rw, rule) to try for this box.
    Disabled orientations are excluded.
    prefer_rotated=True: try B before A.
    """
    l, w = box.length, box.width
    rules = box.orient_rules

    a = (l, w, rules.get("A", "any"))
    b = (w, l, rules.get("B", "any")) if box.rotatable and abs(l - w) > EPS else None

    candidates = [b, a] if prefer_rotated else [a, b]
    return [(rl, rw, rule) for (rl, rw, rule) in candidates
            if (rl, rw, rule) is not None and rule != "disabled"]


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

def _has_support(px,py,pz,rl,rw, placed):
    if pz < EPS:
        return True
    for p in placed:
        if abs(p.z+p.placed_h-pz) < EPS:
            if _overlaps_xy(px,py,rl,rw, p.x,p.y,p.placed_l,p.placed_w):
                return True
    return False


# ── Position-rule check ───────────────────────────────────────────────────────

def _position_ok(rule, px, py, pz, rl, rw, placed):
    if rule == "floor_only":
        return pz < EPS
    if rule in ("top_only", "no_floor"):
        return pz > EPS and _has_support(px,py,pz,rl,rw, placed)
    return True   # "any"


# ── Placement validity ────────────────────────────────────────────────────────

def _can_place(rl,rw,h, px,py,pz, truck_l,truck_w,truck_h,
               placed, rule, stackable) -> bool:
    if px+rl > truck_l+EPS: return False
    if py+rw > truck_w+EPS: return False
    if pz+h  > truck_h+EPS: return False
    if not _position_ok(rule, px,py,pz,rl,rw, placed): return False
    for p in placed:
        if _overlaps_3d(px,py,pz,rl,rw,h,
                        p.x,p.y,p.z,p.placed_l,p.placed_w,p.placed_h):
            return False
        if not p.stackable:
            if pz >= (p.z+p.placed_h)-EPS:
                if _overlaps_xy(px,py,rl,rw, p.x,p.y,p.placed_l,p.placed_w):
                    return False
    return True


# ── Contact area ──────────────────────────────────────────────────────────────

def _contact(px,py,pz,rl,rw,h, truck_l,truck_w,truck_h, placed):
    c = 0.0
    if pz < EPS:              c += rl*rw
    if px < EPS:              c += rw*h
    if py < EPS:              c += rl*h
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


# ── Wall-first score ──────────────────────────────────────────────────────────

def _score(px,py,pz,rl,rw,h, truck_l,truck_w,truck_h,
           placed, box, prefer_columns):
    """
    (X_rounded, Z, Y_rounded, -contact)
    → fill low X (don't advance length), then fill Z, then fill Y.
    """
    ca = _contact(px,py,pz,rl,rw,h, truck_l,truck_w,truck_h, placed)
    if prefer_columns and pz > EPS:
        for p in placed:
            if p.package_id == box.package_id and abs(p.z+p.placed_h-pz) < EPS:
                ca += (_ov1d(px,px+rl,p.x,p.x+p.placed_l) *
                       _ov1d(py,py+rw,p.y,p.y+p.placed_w) * 3.0)
    return (round(px,3), pz, round(py,3), -ca)


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


# ── Single-pass packer ────────────────────────────────────────────────────────

def _pack_once(truck_l,truck_w,truck_h, boxes,
               prefer_rotated, prefer_columns):
    boxes = [copy.copy(b) for b in boxes]
    for b in boxes: b.reset()

    order = sorted(boxes,
                   key=lambda b: (b.load_priority, b.length*b.width*b.height),
                   reverse=True)

    placed = []
    unpacked = []
    eps: set = {(0.0,0.0,0.0)}

    for box in order:
        best_score = None
        best_pos   = None
        best_rot   = None

        orientations = _get_orientations(box, prefer_rotated)
        if not orientations:
            unpacked.append(box)
            continue

        for (px,py,pz) in list(eps):
            for (rl,rw,rule) in orientations:
                if _can_place(rl,rw,box.height,px,py,pz,
                              truck_l,truck_w,truck_h,placed,rule,box.stackable):
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


# ── X-mirror for back_front ───────────────────────────────────────────────────

def _mirror_x(placed, truck_l):
    for b in placed:
        b.x = truck_l - b.x - b.placed_l


# ── Dual-pass ────────────────────────────────────────────────────────────────

def pack(truck_l,truck_w,truck_h, boxes,
         loading_dir="front_back", prefer_columns=False):

    pa,ua = _pack_once(truck_l,truck_w,truck_h,boxes,False,prefer_columns)
    pb,ub = _pack_once(truck_l,truck_w,truck_h,boxes,True, prefer_columns)

    va = sum(b.placed_l*b.placed_w*b.placed_h for b in pa)
    vb = sum(b.placed_l*b.placed_w*b.placed_h for b in pb)

    if len(pb) > len(pa):
        best, ubest = pb, ub
    elif len(pa) > len(pb):
        best, ubest = pa, ua
    else:
        best, ubest = (pb,ub) if vb>=va else (pa,ua)

    if loading_dir == "back_front":
        _mirror_x(best, truck_l)

    return best, ubest


# ── Public ────────────────────────────────────────────────────────────────────

def run_packing(truck_l, truck_w, truck_h, items,
                loading_dir="front_back", prefer_columns=False):

    boxes = []
    for item in items:
        orient_rules = item.get("orient_rules") or {"A":"any","B":"any"}
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
                orient_rules  = orient_rules,
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
