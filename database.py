import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("truck_loader.db")

COLORS = [
    "#E63946", "#457B9D", "#2A9D8F", "#E9C46A", "#F4A261",
    "#264653", "#A8DADC", "#6D6875", "#B5838D", "#FFAFCC",
    "#80B918", "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE"
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _column_exists(conn, table, column):
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    return column in cols


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # ── packages table ────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            length      REAL    NOT NULL,
            width       REAL    NOT NULL,
            height      REAL    NOT NULL,
            weight      REAL    DEFAULT 0,
            description TEXT    DEFAULT '',
            color       TEXT    NOT NULL,
            created_at  TEXT    NOT NULL,
            category    TEXT    DEFAULT '',
            tags        TEXT    DEFAULT '',
            stackable   INTEGER DEFAULT 1
        )
    """)

    # Migrations for existing databases that lack new columns
    for col, ddl in [
        ("category",  "TEXT    DEFAULT ''"),
        ("tags",      "TEXT    DEFAULT ''"),
        ("stackable", "INTEGER DEFAULT 1"),
    ]:
        if not _column_exists(conn, "packages", col):
            c.execute(f"ALTER TABLE packages ADD COLUMN {col} {ddl}")

    # ── loading_plans table ───────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS loading_plans (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            name                TEXT    NOT NULL,
            created_at          TEXT    NOT NULL,
            truck_length        REAL    NOT NULL,
            truck_width         REAL    NOT NULL,
            truck_height        REAL    NOT NULL,
            total_volume        REAL    NOT NULL,
            used_volume         REAL    NOT NULL,
            efficiency          REAL    NOT NULL,
            packed_count        INTEGER NOT NULL,
            unpacked_count      INTEGER NOT NULL,
            items_json          TEXT    NOT NULL,
            packed_boxes_json   TEXT    NOT NULL,
            unpacked_boxes_json TEXT    NOT NULL,
            notes               TEXT    DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()


# ── Category helpers ───────────────────────────────────────────────────────────

def get_categories():
    """Return sorted list of all distinct non-empty categories."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT category FROM packages WHERE category != '' ORDER BY category"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


# ── Packages ──────────────────────────────────────────────────────────────────

def add_package(name, length, width, height,
                weight=0, description="",
                category="", tags="", stackable=True):
    conn = get_connection()
    c = conn.cursor()
    used  = [r["color"] for r in c.execute("SELECT color FROM packages").fetchall()]
    color = next((col for col in COLORS if col not in used),
                 COLORS[len(used) % len(COLORS)])
    c.execute(
        "INSERT INTO packages "
        "(name,length,width,height,weight,description,color,created_at,category,tags,stackable) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (name, length, width, height, weight, description, color,
         datetime.now().isoformat(),
         category.strip(), tags.strip(), int(stackable))
    )
    conn.commit()
    conn.close()


def get_packages(category_filter=None):
    conn = get_connection()
    if category_filter and category_filter != "Todas":
        rows = conn.execute(
            "SELECT * FROM packages WHERE category=? ORDER BY name", (category_filter,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM packages ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_package(pkg_id, name, length, width, height,
                   weight, description, category="", tags="", stackable=True):
    conn = get_connection()
    conn.execute(
        "UPDATE packages "
        "SET name=?,length=?,width=?,height=?,weight=?,description=?,"
        "    category=?,tags=?,stackable=? "
        "WHERE id=?",
        (name, length, width, height, weight, description,
         category.strip(), tags.strip(), int(stackable), pkg_id)
    )
    conn.commit()
    conn.close()


def delete_package(pkg_id):
    conn = get_connection()
    conn.execute("DELETE FROM packages WHERE id=?", (pkg_id,))
    conn.commit()
    conn.close()


# ── Loading Plans ─────────────────────────────────────────────────────────────

def save_plan(name, truck_l, truck_w, truck_h, items,
              packed_boxes, unpacked_boxes, notes=""):
    total_vol  = truck_l * truck_w * truck_h
    used_vol   = sum(b["placed_l"] * b["placed_w"] * b["placed_h"] for b in packed_boxes)
    efficiency = (used_vol / total_vol * 100) if total_vol > 0 else 0

    conn = get_connection()
    conn.execute(
        """INSERT INTO loading_plans
           (name,created_at,truck_length,truck_width,truck_height,
            total_volume,used_volume,efficiency,
            packed_count,unpacked_count,
            items_json,packed_boxes_json,unpacked_boxes_json,notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (name, datetime.now().strftime("%Y-%m-%d %H:%M"),
         truck_l, truck_w, truck_h,
         round(total_vol, 3), round(used_vol, 3), round(efficiency, 2),
         len(packed_boxes), len(unpacked_boxes),
         json.dumps(items),
         json.dumps(packed_boxes),
         json.dumps(unpacked_boxes),
         notes)
    )
    conn.commit()
    conn.close()


def get_plans():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM loading_plans ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_plan(plan_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM loading_plans WHERE id=?", (plan_id,)
    ).fetchone()
    conn.close()
    if row:
        plan = dict(row)
        plan["items"]          = json.loads(plan["items_json"])
        plan["packed_boxes"]   = json.loads(plan["packed_boxes_json"])
        plan["unpacked_boxes"] = json.loads(plan["unpacked_boxes_json"])
        return plan
    return None


def delete_plan(plan_id):
    conn = get_connection()
    conn.execute("DELETE FROM loading_plans WHERE id=?", (plan_id,))
    conn.commit()
    conn.close()
