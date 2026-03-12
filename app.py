"""
🚛 Gestor de Carga de Camiones
Streamlit app – main entry point.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

import database as db
import packing
import visualization as viz

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gestor de Carga de Camiones",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }

div[data-testid="metric-container"] {
    background: linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
    border-radius: 12px; padding: 1rem 1.4rem; color: white;
}
div[data-testid="metric-container"] label { color: #a8dadc !important; font-size:.85rem; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"]
    { color: white !important; font-size:1.8rem; font-weight:700; }

[data-testid="stSidebar"] { background:#16213e; }
[data-testid="stSidebar"] * { color:#e0e0e0; }

.stButton > button {
    border-radius:8px; font-weight:600; transition:.2s;
}
.stButton > button:hover { transform:translateY(-1px); box-shadow:0 4px 12px rgba(0,0,0,.3); }

.eff-bar-wrap { background:#ddd; border-radius:20px; height:22px; overflow:hidden; margin:4px 0 2px; }
.eff-bar { height:100%; border-radius:20px; transition:width .6s ease; }

/* Tag pill */
.tag-pill {
    display:inline-block; padding:1px 8px; border-radius:12px;
    font-size:.72rem; font-weight:600; margin:1px 2px;
    background:#e9ecef; color:#495057;
}
.cat-pill {
    display:inline-block; padding:2px 10px; border-radius:12px;
    font-size:.78rem; font-weight:700; margin:1px 2px;
    background:#264653; color:#a8dadc;
}
.badge-stackable {
    display:inline-block; padding:1px 7px; border-radius:10px;
    font-size:.7rem; font-weight:700; background:#2A9D8F; color:white;
}
.badge-no-stack {
    display:inline-block; padding:1px 7px; border-radius:10px;
    font-size:.7rem; font-weight:700; background:#E63946; color:white;
}
</style>
""", unsafe_allow_html=True)

# ── Init DB ───────────────────────────────────────────────────────────────────
db.init_db()

# ── Helpers ───────────────────────────────────────────────────────────────────
def _ss(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def _tag_html(tags_str):
    if not tags_str:
        return ""
    pills = "".join(f'<span class="tag-pill">#{t.strip()}</span>'
                    for t in tags_str.split(",") if t.strip())
    return pills


def _stackable_badge(s):
    if s:
        return '<span class="badge-stackable">⬆ Apilable</span>'
    return '<span class="badge-no-stack">⛔ No apilable</span>'


def _eff_bar(efficiency):
    color = "#2A9D8F" if efficiency >= 70 else ("#E9C46A" if efficiency >= 40 else "#E63946")
    st.markdown(
        f'<div class="eff-bar-wrap">'
        f'<div class="eff-bar" style="width:{efficiency:.1f}%;background:{color};"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Eficiencia de llenado: {efficiency:.1f}%")


# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚛 Carga de Camiones")
    st.markdown("---")
    page = st.radio(
        "Navegación",
        ["📦 Gestión de Bultos", "🗂️ Nuevo Plan de Carga", "📋 Historial de Planes"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    all_pkgs  = db.get_packages()
    all_plans = db.get_plans()
    st.metric("Bultos registrados", len(all_pkgs))
    st.metric("Planes guardados",   len(all_plans))
    try:
        cats = db.get_categories()
        if cats:
            st.markdown("**Categorías**")
            for c in cats:
                st.markdown(f'<span class="cat-pill">{c}</span>', unsafe_allow_html=True)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 – GESTIÓN DE BULTOS
# ══════════════════════════════════════════════════════════════════════════════
if page == "📦 Gestión de Bultos":
    st.title("📦 Gestión de Bultos")
    st.markdown("Registrá todos los tipos de bultos con sus medidas, categoría, etiquetas y apilabilidad.")

    # ── Add package form ──────────────────────────────────────────────────────
    with st.expander("➕ Agregar nuevo bulto", expanded=len(all_pkgs) == 0):
        with st.form("add_pkg_form", clear_on_submit=True):
            fa1, fa2 = st.columns(2)
            with fa1:
                new_name = st.text_input("Nombre del bulto *", placeholder="Ej: Caja grande")
                new_desc = st.text_input("Descripción", placeholder="Opcional")
            with fa2:
                existing_cats = [""] + (db.get_categories() if hasattr(db, "get_categories") else [])
                cat_select = st.selectbox("Categoría existente", existing_cats,
                                          format_func=lambda x: "— sin categoría —" if x == "" else x)
                cat_new    = st.text_input("…o escribí una nueva categoría",
                                           placeholder="Ej: Electrónica, Alimentos…")
                new_tags   = st.text_input("Etiquetas (separadas por coma)",
                                           placeholder="Ej: frágil, refrigerado, urgente")

            st.markdown("**Dimensiones (metros)** — la altura se respeta siempre de pie")
            fd1, fd2, fd3, fd4 = st.columns(4)
            with fd1:
                new_l = st.number_input("Largo", min_value=0.01, step=0.01, value=1.0, format="%.2f")
            with fd2:
                new_w = st.number_input("Ancho", min_value=0.01, step=0.01, value=0.8, format="%.2f")
            with fd3:
                new_h = st.number_input("Alto",  min_value=0.01, step=0.01, value=1.2, format="%.2f")
            with fd4:
                new_weight = st.number_input("Peso (kg)", min_value=0.0, step=0.5, value=0.0)

            new_stackable = st.checkbox("✅ Permite apilar bultos encima", value=True)

            if st.form_submit_button("💾 Guardar bulto", use_container_width=True):
                if not new_name.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    final_cat = cat_new.strip() if cat_new.strip() else cat_select
                    db.add_package(
                        new_name.strip(), new_l, new_w, new_h, new_weight, new_desc,
                        category=final_cat, tags=new_tags, stackable=new_stackable,
                    )
                    st.success(f"✅ Bulto **{new_name}** agregado.")
                    st.rerun()

    st.markdown("---")

    # ── Filter by category ────────────────────────────────────────────────────
    cats = (db.get_categories() if hasattr(db, "get_categories") else [])
    filter_opts = ["Todas"] + cats
    col_filter, col_search = st.columns([1, 2])
    with col_filter:
        cat_filter = st.selectbox("Filtrar por categoría", filter_opts, key="cat_filter")
    with col_search:
        search_q = st.text_input("🔍 Buscar por nombre", placeholder="Escribí para filtrar…", key="search_q")

    packages = db.get_packages(category_filter=cat_filter if cat_filter != "Todas" else None)
    if search_q.strip():
        packages = [p for p in packages if search_q.lower() in p["name"].lower()]

    st.subheader(f"Bultos registrados ({len(packages)})")

    _ss("editing_pkg", None)

    if not packages:
        st.info("No hay bultos que coincidan con el filtro.")
    else:
        for pkg in packages:
            stackable = bool(pkg.get("stackable", 1))
            tags_html = _tag_html(pkg.get("tags", ""))
            cat_str   = pkg.get("category", "")
            vol       = pkg["length"] * pkg["width"] * pkg["height"]

            with st.container():
                c_col, info_col, dim_col, act_col = st.columns([0.05, 0.40, 0.35, 0.20])

                with c_col:
                    st.markdown(
                        f'<div style="width:28px;height:52px;border-radius:6px;'
                        f'background:{pkg["color"]};margin-top:2px;'
                        f'border:2px solid rgba(0,0,0,.2);"></div>',
                        unsafe_allow_html=True,
                    )

                with info_col:
                    header = f"**{pkg['name']}**"
                    st.markdown(header)
                    meta = ""
                    if cat_str:
                        meta += f'<span class="cat-pill">{cat_str}</span> '
                    meta += _stackable_badge(stackable)
                    if tags_html:
                        meta += " " + tags_html
                    st.markdown(meta, unsafe_allow_html=True)
                    if pkg.get("description"):
                        st.caption(pkg["description"])

                with dim_col:
                    st.markdown(
                        f"📐 `{pkg['length']:.2f}` × `{pkg['width']:.2f}` × `{pkg['height']:.2f}` m<br>"
                        f"<small>Vol: `{vol:.3f} m³`"
                        + (f"  |  ⚖️ {pkg['weight']} kg" if pkg.get("weight") else "")
                        + "</small>",
                        unsafe_allow_html=True,
                    )

                with act_col:
                    ce, cd = st.columns(2)
                    with ce:
                        if st.button("✏️", key=f"edit_{pkg['id']}", help="Editar"):
                            st.session_state["editing_pkg"] = (
                                None if st.session_state.get("editing_pkg") == pkg["id"]
                                else pkg["id"]
                            )
                    with cd:
                        if st.button("🗑️", key=f"del_{pkg['id']}", help="Eliminar"):
                            db.delete_package(pkg["id"])
                            st.rerun()

                # Inline edit form
                if st.session_state.get("editing_pkg") == pkg["id"]:
                    with st.form(f"edit_{pkg['id']}"):
                        st.markdown(f"**Editando:** {pkg['name']}")
                        ef1, ef2 = st.columns(2)
                        with ef1:
                            e_name = st.text_input("Nombre", value=pkg["name"])
                            e_desc = st.text_input("Descripción", value=pkg.get("description",""))
                        with ef2:
                            existing_cats_e = [""] + (db.get_categories() if hasattr(db, "get_categories") else [])
                            e_cat_idx = (existing_cats_e.index(pkg.get("category",""))
                                         if pkg.get("category","") in existing_cats_e else 0)
                            e_cat_sel = st.selectbox("Categoría", existing_cats_e,
                                                      index=e_cat_idx,
                                                      format_func=lambda x: "— sin categoría —" if x=="" else x)
                            e_cat_new = st.text_input("Nueva categoría", value="")
                            e_tags    = st.text_input("Etiquetas", value=pkg.get("tags",""))

                        ed1, ed2, ed3, ed4 = st.columns(4)
                        with ed1: e_l = st.number_input("Largo", value=float(pkg["length"]), min_value=0.01, step=0.01, format="%.2f")
                        with ed2: e_w = st.number_input("Ancho", value=float(pkg["width"]),  min_value=0.01, step=0.01, format="%.2f")
                        with ed3: e_h = st.number_input("Alto",  value=float(pkg["height"]), min_value=0.01, step=0.01, format="%.2f")
                        with ed4: e_weight = st.number_input("Peso (kg)", value=float(pkg.get("weight",0)), min_value=0.0, step=0.5)

                        e_stack = st.checkbox("✅ Permite apilar bultos encima",
                                              value=bool(pkg.get("stackable",1)))

                        sb1, sb2 = st.columns(2)
                        with sb1:
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                final_cat = e_cat_new.strip() if e_cat_new.strip() else e_cat_sel
                                db.update_package(
                                    pkg["id"], e_name, e_l, e_w, e_h, e_weight, e_desc,
                                    category=final_cat, tags=e_tags, stackable=e_stack,
                                )
                                st.session_state["editing_pkg"] = None
                                st.rerun()
                        with sb2:
                            if st.form_submit_button("✖ Cancelar", use_container_width=True):
                                st.session_state["editing_pkg"] = None
                                st.rerun()

                st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 – NUEVO PLAN DE CARGA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗂️ Nuevo Plan de Carga":
    st.title("🗂️ Nuevo Plan de Carga")

    packages = db.get_packages()
    if not packages:
        st.warning("⚠️ No hay bultos registrados. Andá a **Gestión de Bultos** primero.")
        st.stop()

    # ── Step 1: Name & notes ──────────────────────────────────────────────────
    st.subheader("1️⃣ Información del plan")
    p1, p2 = st.columns([1,1])
    with p1:
        plan_name  = st.text_input("Nombre del plan *", placeholder="Ej: Envío CABA – Semana 23", key="plan_name")
        st.caption(f"📅 Fecha automática: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    with p2:
        plan_notes = st.text_area("Notas", height=90, placeholder="Destino, transportista, obs…", key="plan_notes")

    st.markdown("---")

    # ── Step 2: Truck dimensions ──────────────────────────────────────────────
    st.subheader("2️⃣ Dimensiones del camión / contenedor")

    presets = {
        "Personalizado":                  None,
        "Camión mediano (7×2.4×2.5 m)":  (7.0, 2.4, 2.5),
        "Semi-trailer (12×2.4×2.6 m)":   (12.0, 2.4, 2.6),
        "Contenedor 20' (5.9×2.35×2.39 m)": (5.9, 2.35, 2.39),
        "Contenedor 40' (12×2.35×2.39 m)":  (12.0, 2.35, 2.39),
        "Furgón pequeño (3×1.8×1.9 m)":  (3.0, 1.8, 1.9),
    }
    preset_sel  = st.selectbox("Plantilla", list(presets.keys()))
    preset_vals = presets[preset_sel] or (7.0, 2.4, 2.5)

    tc1, tc2, tc3 = st.columns(3)
    with tc1: truck_l = st.number_input("Largo (m)", min_value=0.1, value=float(preset_vals[0]), step=0.1, format="%.2f")
    with tc2: truck_w = st.number_input("Ancho (m)", min_value=0.1, value=float(preset_vals[1]), step=0.1, format="%.2f")
    with tc3: truck_h = st.number_input("Alto (m)",  min_value=0.1, value=float(preset_vals[2]), step=0.1, format="%.2f")

    truck_vol = truck_l * truck_w * truck_h
    st.info(f"📦 Volumen total: **{truck_vol:.2f} m³**")
    st.markdown("---")

    # ── Step 3: Package selection ─────────────────────────────────────────────
    st.subheader("3️⃣ Selección de bultos")

    # Optional category filter for the plan selector
    cats_for_plan = ["Todas"] + (db.get_categories() if hasattr(db, "get_categories") else [])
    plan_cat_filter = st.selectbox("Filtrar bultos por categoría", cats_for_plan, key="plan_cat_filter")
    packages_for_plan = db.get_packages(
        category_filter=plan_cat_filter if plan_cat_filter != "Todas" else None
    )

    st.markdown("Indicá cuántas unidades de cada bulto querés cargar (0 = no incluir).")

    qty_inputs = {}
    cols_per_row = 3
    pkg_cols = st.columns(cols_per_row)

    for i, pkg in enumerate(packages_for_plan):
        col = pkg_cols[i % cols_per_row]
        vol = pkg["length"] * pkg["width"] * pkg["height"]
        stackable = bool(pkg.get("stackable", 1))
        with col:
            cat_badge  = f'<span class="cat-pill">{pkg["category"]}</span> ' if pkg.get("category") else ""
            stack_badge = _stackable_badge(stackable)
            tags_html  = _tag_html(pkg.get("tags",""))
            st.markdown(
                f'<div style="border-left:4px solid {pkg["color"]};'
                f'padding:6px 10px;border-radius:4px;'
                f'background:rgba(0,0,0,.03);margin-bottom:4px;">'
                f'<strong>{pkg["name"]}</strong><br>'
                f'{cat_badge}{stack_badge}'
                + (f' {tags_html}' if tags_html else '')
                + f'<br><small>📐 {pkg["length"]:.2f}×{pkg["width"]:.2f}×{pkg["height"]:.2f} m'
                  f' | {vol:.3f} m³'
                + (f' | ⚖️ {pkg["weight"]} kg' if pkg.get("weight") else "")
                + "</small></div>",
                unsafe_allow_html=True,
            )
            qty = st.number_input(
                "Cantidad", min_value=0, max_value=500, step=1, value=0,
                key=f"qty_{pkg['id']}",
                label_visibility="collapsed",
            )
            qty_inputs[pkg["id"]] = qty

    selected_items = [
        {
            "package_id": pkg["id"],
            "name":       pkg["name"],
            "length":     pkg["length"],
            "width":      pkg["width"],
            "height":     pkg["height"],
            "weight":     pkg.get("weight", 0),
            "color":      pkg["color"],
            "stackable":  bool(pkg.get("stackable", 1)),
            "category":   pkg.get("category", ""),
            "tags":       pkg.get("tags", ""),
            "quantity":   qty_inputs.get(pkg["id"], 0),
        }
        for pkg in packages_for_plan
        if qty_inputs.get(pkg["id"], 0) > 0
    ]

    total_boxes     = sum(i["quantity"] for i in selected_items)
    total_vol_boxes = sum(i["length"] * i["width"] * i["height"] * i["quantity"] for i in selected_items)
    theo_eff        = min(100, total_vol_boxes / truck_vol * 100) if truck_vol > 0 else 0

    if selected_items:
        st.markdown("---")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Total de bultos",        total_boxes)
        mc2.metric("Volumen de bultos",      f"{total_vol_boxes:.2f} m³")
        mc3.metric("Eficiencia máx. posible", f"{theo_eff:.1f}%")

        non_stack = [i["name"] for i in selected_items if not i["stackable"]]
        if non_stack:
            st.warning(f"⛔ Bultos **no apilables** en este plan (nada se pondrá encima): "
                       + ", ".join(f"**{n}**" for n in non_stack))

    st.markdown("---")

    # ── Generate ──────────────────────────────────────────────────────────────
    if st.button("🚀 Generar Plan de Carga", type="primary",
                 use_container_width=True, disabled=len(selected_items) == 0):
        if not plan_name.strip():
            st.error("⚠️ Poné un nombre al plan antes de generarlo.")
        else:
            with st.spinner("⚙️ Calculando la mejor distribución… todos los bultos de pie 🧍"):
                packed, unpacked, efficiency = packing.run_packing(
                    truck_l, truck_w, truck_h, selected_items
                )
            db.save_plan(
                name=plan_name.strip(),
                truck_l=truck_l, truck_w=truck_w, truck_h=truck_h,
                items=selected_items,
                packed_boxes=packed,
                unpacked_boxes=unpacked,
                notes=plan_notes,
            )
            st.session_state.update({
                "last_packed":   packed,
                "last_unpacked": unpacked,
                "last_eff":      efficiency,
                "last_truck":    (truck_l, truck_w, truck_h),
                "last_name":     plan_name.strip(),
            })
            st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.get("last_packed") is not None:
        packed     = st.session_state["last_packed"]
        unpacked   = st.session_state["last_unpacked"]
        efficiency = st.session_state["last_eff"]
        tl, tw, th = st.session_state["last_truck"]

        st.success(f"✅ Plan generado y guardado: **{st.session_state['last_name']}**")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Bultos cargados",  len(packed))
        r2.metric("Sin cargar",       len(unpacked))
        r3.metric("Eficiencia",       f"{efficiency:.1f}%")
        used_vol = sum(b["placed_l"] * b["placed_w"] * b["placed_h"] for b in packed)
        r4.metric("Vol. utilizado",   f"{used_vol:.2f} m³")

        _eff_bar(efficiency)

        st.plotly_chart(
            viz.build_figure(tl, tw, th, packed, unpacked, efficiency),
            use_container_width=True,
        )

        if packed:
            st.subheader("🗺️ Vista superior por capas")
            st.plotly_chart(viz.build_2d_layers(tl, tw, th, packed), use_container_width=True)

        if unpacked:
            st.warning(
                f"⚠️ **{len(unpacked)} bulto(s) no pudieron cargarse** (no entran en el camión):\n\n"
                + "\n".join(f"- {b['name']} ({b['length']:.2f}×{b['width']:.2f}×{b['height']:.2f} m)"
                            for b in unpacked)
            )

        with st.expander("📋 Detalle de posicionamiento"):
            rows = [
                {
                    "Bulto":      b["name"],
                    "X (m)":     f"{b['x']:.2f}",
                    "Y (m)":     f"{b['y']:.2f}",
                    "Z (m)":     f"{b['z']:.2f}",
                    "L×A×H (m)": f"{b['placed_l']:.2f}×{b['placed_w']:.2f}×{b['placed_h']:.2f}",
                    "Vol (m³)":  f"{b['placed_l']*b['placed_w']*b['placed_h']:.3f}",
                    "Apilable":  "✅" if b.get("stackable", True) else "⛔",
                }
                for b in packed
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 – HISTORIAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Historial de Planes":
    st.title("📋 Historial de Planes de Carga")

    plans = db.get_plans()
    if not plans:
        st.info("Aún no hay planes guardados. Creá uno desde **Nuevo Plan de Carga**.")
        st.stop()

    _ss("viewing_plan", None)

    for plan in plans:
        eff = plan["efficiency"]
        badge_color = "#2A9D8F" if eff >= 70 else ("#E9C46A" if eff >= 40 else "#E63946")

        with st.container():
            hc1, hc2, hc3 = st.columns([0.50, 0.35, 0.15])
            with hc1:
                st.markdown(
                    f'<span style="background:{badge_color};color:white;'
                    f'padding:2px 9px;border-radius:12px;font-size:.75rem;">'
                    f'{eff:.0f}%</span> &nbsp;'
                    f'<strong style="font-size:1.05rem;">{plan["name"]}</strong><br>'
                    f'<small style="color:#888;">📅 {plan["created_at"]}</small>',
                    unsafe_allow_html=True,
                )
            with hc2:
                st.markdown(
                    f"📦 **{plan['packed_count']}** cargados"
                    + (f" | ⚠️ {plan['unpacked_count']} sin cargar" if plan["unpacked_count"] else "")
                    + f"<br><small>🚛 {plan['truck_length']}×{plan['truck_width']}×{plan['truck_height']} m"
                    + f" = {plan['total_volume']:.1f} m³</small>",
                    unsafe_allow_html=True,
                )
            with hc3:
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("👁️", key=f"vp_{plan['id']}", help="Ver"):
                        st.session_state["viewing_plan"] = (
                            None if st.session_state.get("viewing_plan") == plan["id"]
                            else plan["id"]
                        )
                        st.rerun()
                with bc2:
                    if st.button("🗑️", key=f"dp_{plan['id']}", help="Eliminar"):
                        db.delete_plan(plan["id"])
                        if st.session_state.get("viewing_plan") == plan["id"]:
                            st.session_state["viewing_plan"] = None
                        st.rerun()

            # Expanded plan view
            if st.session_state.get("viewing_plan") == plan["id"]:
                full     = db.get_plan(plan["id"])
                packed   = full["packed_boxes"]
                unpacked = full["unpacked_boxes"]

                st.markdown("---")
                hi1, hi2, hi3, hi4 = st.columns(4)
                hi1.metric("Eficiencia",      f"{full['efficiency']:.1f}%")
                hi2.metric("Cargados",        full["packed_count"])
                hi3.metric("Sin cargar",      full["unpacked_count"])
                hi4.metric("Vol. utilizado",  f"{full['used_volume']:.2f} m³")

                _eff_bar(full["efficiency"])

                if full.get("notes"):
                    st.info(f"📝 {full['notes']}")

                if packed:
                    st.plotly_chart(
                        viz.build_figure(
                            full["truck_length"], full["truck_width"], full["truck_height"],
                            packed, unpacked, full["efficiency"]
                        ),
                        use_container_width=True,
                    )
                    st.subheader("🗺️ Vista superior")
                    st.plotly_chart(
                        viz.build_2d_layers(
                            full["truck_length"], full["truck_width"], full["truck_height"],
                            packed
                        ),
                        use_container_width=True,
                    )
                    with st.expander("📋 Detalle de posicionamiento"):
                        rows = [
                            {
                                "Bulto":      b["name"],
                                "X (m)":     f"{b['x']:.2f}",
                                "Y (m)":     f"{b['y']:.2f}",
                                "Z (m)":     f"{b['z']:.2f}",
                                "L×A×H (m)": f"{b['placed_l']:.2f}×{b['placed_w']:.2f}×{b['placed_h']:.2f}",
                                "Apilable":  "✅" if b.get("stackable", True) else "⛔",
                            }
                            for b in packed
                        ]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                if unpacked:
                    st.warning(
                        f"⚠️ **{len(unpacked)} sin cargar:** "
                        + ", ".join(b["name"] for b in unpacked)
                    )

                with st.expander("📦 Resumen de bultos del plan"):
                    items = full.get("items", [])
                    rows2 = [
                        {
                            "Bulto":     it["name"],
                            "Categoría": it.get("category",""),
                            "Etiquetas": it.get("tags",""),
                            "Cantidad":  it["quantity"],
                            "L×A×H":    f"{it['length']:.2f}×{it['width']:.2f}×{it['height']:.2f} m",
                            "Apilable":  "✅" if it.get("stackable",True) else "⛔",
                        }
                        for it in items
                    ]
                    st.dataframe(pd.DataFrame(rows2), use_container_width=True, hide_index=True)

                st.markdown("---")

        st.markdown("")
