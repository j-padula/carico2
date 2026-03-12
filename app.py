"""
🚛 Gestor de Carga de Camiones
Streamlit app – main entry point.
"""

import streamlit as st
import pandas as pd
import json
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
/* Card-like sections */
.block-container { padding-top: 1.5rem; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
    border-radius: 12px; padding: 1rem 1.4rem;
    color: white;
}
div[data-testid="metric-container"] label { color: #a8dadc !important; font-size:.85rem; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"]
    { color: white !important; font-size:1.8rem; font-weight:700; }

/* Sidebar */
[data-testid="stSidebar"] { background:#16213e; }
[data-testid="stSidebar"] * { color:#e0e0e0; }
[data-testid="stSidebar"] .stRadio > label { font-size:.95rem; }

/* Buttons */
.stButton > button {
    border-radius:8px; font-weight:600; transition:.2s;
}
.stButton > button:hover { transform:translateY(-1px); box-shadow:0 4px 12px rgba(0,0,0,.3); }

/* Efficiency bar */
.eff-bar-wrap { background:#ddd; border-radius:20px; height:22px; overflow:hidden; }
.eff-bar { height:100%; border-radius:20px; transition:width .6s ease;
           background:linear-gradient(90deg,#2A9D8F,#E9C46A,#E63946); }
</style>
""", unsafe_allow_html=True)

# ── Init DB ───────────────────────────────────────────────────────────────────
db.init_db()

# ── Session state helpers ─────────────────────────────────────────────────────
def _ss(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚛 Carga de Camiones")
    st.markdown("---")
    page = st.radio(
        "Navegación",
        ["📦 Gestión de Bultos", "🗂️ Nuevo Plan de Carga", "📋 Historial de Planes"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    packages = db.get_packages()
    plans    = db.get_plans()
    st.metric("Bultos registrados", len(packages))
    st.metric("Planes guardados",   len(plans))


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 – GESTIÓN DE BULTOS
# ══════════════════════════════════════════════════════════════════════════════
if page == "📦 Gestión de Bultos":
    st.title("📦 Gestión de Bultos")
    st.markdown("Registrá todos los tipos de bultos con sus medidas para usarlos en los planes de carga.")

    # ── Add package ──────────────────────────────────────────────────────────
    with st.expander("➕ Agregar nuevo bulto", expanded=len(packages) == 0):
        with st.form("add_package_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Nombre del bulto *", placeholder="Ej: Caja grande")
                new_desc = st.text_input("Descripción", placeholder="Opcional")
            with col2:
                new_weight = st.number_input("Peso (kg)", min_value=0.0, step=0.5, value=0.0)

            st.markdown("**Dimensiones (metros)**")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_l = st.number_input("Largo", min_value=0.01, step=0.01, value=1.0, format="%.2f")
            with c2:
                new_w = st.number_input("Ancho", min_value=0.01, step=0.01, value=1.0, format="%.2f")
            with c3:
                new_h = st.number_input("Alto",  min_value=0.01, step=0.01, value=1.0, format="%.2f")

            submitted = st.form_submit_button("💾 Guardar bulto", use_container_width=True)
            if submitted:
                if not new_name.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    db.add_package(new_name.strip(), new_l, new_w, new_h, new_weight, new_desc)
                    st.success(f"✅ Bulto **{new_name}** agregado correctamente.")
                    st.rerun()

    st.markdown("---")

    # ── Package list ─────────────────────────────────────────────────────────
    packages = db.get_packages()
    if not packages:
        st.info("No hay bultos registrados. Agregá el primero usando el formulario de arriba.")
    else:
        st.subheader(f"Bultos registrados ({len(packages)})")

        # Edit state
        _ss("editing_pkg", None)

        for pkg in packages:
            with st.container():
                col_color, col_info, col_dims, col_actions = st.columns([0.05, 0.35, 0.35, 0.25])

                with col_color:
                    st.markdown(
                        f'<div style="width:28px;height:28px;border-radius:6px;'
                        f'background:{pkg["color"]};margin-top:4px;'
                        f'border:2px solid rgba(0,0,0,.2);"></div>',
                        unsafe_allow_html=True,
                    )
                with col_info:
                    st.markdown(f"**{pkg['name']}**")
                    if pkg.get("description"):
                        st.caption(pkg["description"])
                    if pkg.get("weight"):
                        st.caption(f"⚖️ {pkg['weight']} kg")
                with col_dims:
                    vol = pkg["length"] * pkg["width"] * pkg["height"]
                    st.markdown(
                        f"📐 `{pkg['length']:.2f}` × `{pkg['width']:.2f}` × `{pkg['height']:.2f}` m  "
                        f"&nbsp; Vol: `{vol:.3f} m³`",
                        unsafe_allow_html=True,
                    )
                with col_actions:
                    c_edit, c_del = st.columns(2)
                    with c_edit:
                        if st.button("✏️", key=f"edit_{pkg['id']}", help="Editar"):
                            st.session_state["editing_pkg"] = pkg["id"]
                    with c_del:
                        if st.button("🗑️", key=f"del_{pkg['id']}", help="Eliminar"):
                            db.delete_package(pkg["id"])
                            st.rerun()

                # Inline edit form
                if st.session_state.get("editing_pkg") == pkg["id"]:
                    with st.form(f"edit_form_{pkg['id']}"):
                        st.markdown(f"**Editando: {pkg['name']}**")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_name   = st.text_input("Nombre", value=pkg["name"])
                            e_desc   = st.text_input("Descripción", value=pkg.get("description", ""))
                        with ec2:
                            e_weight = st.number_input("Peso (kg)", value=float(pkg.get("weight", 0)), min_value=0.0, step=0.5)
                        ed1, ed2, ed3 = st.columns(3)
                        with ed1:
                            e_l = st.number_input("Largo", value=float(pkg["length"]), min_value=0.01, step=0.01, format="%.2f")
                        with ed2:
                            e_w = st.number_input("Ancho", value=float(pkg["width"]),  min_value=0.01, step=0.01, format="%.2f")
                        with ed3:
                            e_h = st.number_input("Alto",  value=float(pkg["height"]), min_value=0.01, step=0.01, format="%.2f")
                        sb1, sb2 = st.columns(2)
                        with sb1:
                            if st.form_submit_button("💾 Guardar cambios", use_container_width=True):
                                db.update_package(pkg["id"], e_name, e_l, e_w, e_h, e_weight, e_desc)
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
        st.warning("⚠️ No hay bultos registrados. Andá a **Gestión de Bultos** y creá algunos primero.")
        st.stop()

    # ── Step 1: Plan name & notes ─────────────────────────────────────────────
    st.subheader("1️⃣ Información del plan")
    col_n, col_notes = st.columns([1, 1])
    with col_n:
        plan_name = st.text_input(
            "Nombre del plan *",
            placeholder="Ej: Envío Buenos Aires – Semana 23",
            key="plan_name",
        )
        st.caption(f"📅 Fecha automática: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    with col_notes:
        plan_notes = st.text_area("Notas / observaciones", height=90, key="plan_notes",
                                   placeholder="Destino, transportista, observaciones…")

    st.markdown("---")

    # ── Step 2: Truck dimensions ──────────────────────────────────────────────
    st.subheader("2️⃣ Dimensiones del camión / contenedor")

    presets = {
        "Personalizado": None,
        "Camión mediano (7×2.4×2.5 m)": (7.0, 2.4, 2.5),
        "Semi-trailer (12×2.4×2.6 m)": (12.0, 2.4, 2.6),
        "Contenedor 20' (5.9×2.35×2.39 m)": (5.9, 2.35, 2.39),
        "Contenedor 40' (12×2.35×2.39 m)": (12.0, 2.35, 2.39),
        "Furgón pequeño (3×1.8×1.9 m)": (3.0, 1.8, 1.9),
    }
    preset_sel = st.selectbox("Plantilla de vehículo", list(presets.keys()))
    preset_vals = presets[preset_sel] or (7.0, 2.4, 2.5)

    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        truck_l = st.number_input("Largo (m)",  min_value=0.1, value=float(preset_vals[0]), step=0.1, format="%.2f")
    with tc2:
        truck_w = st.number_input("Ancho (m)",  min_value=0.1, value=float(preset_vals[1]), step=0.1, format="%.2f")
    with tc3:
        truck_h = st.number_input("Alto (m)",   min_value=0.1, value=float(preset_vals[2]), step=0.1, format="%.2f")

    truck_vol = truck_l * truck_w * truck_h
    st.info(f"📦 Volumen total del vehículo: **{truck_vol:.2f} m³**")

    st.markdown("---")

    # ── Step 3: Package selection ─────────────────────────────────────────────
    st.subheader("3️⃣ Selección de bultos")
    st.markdown("Indicá cuántas unidades de cada bulto querés cargar (0 = no incluir).")

    pkg_df_rows = []
    qty_inputs  = {}

    pkg_cols = st.columns(min(len(packages), 3))
    for i, pkg in enumerate(packages):
        col = pkg_cols[i % len(pkg_cols)]
        vol = pkg["length"] * pkg["width"] * pkg["height"]
        with col:
            st.markdown(
                f'<div style="border-left:4px solid {pkg["color"]};'
                f'padding:6px 10px;border-radius:4px;'
                f'background:rgba(0,0,0,.03);margin-bottom:2px;">'
                f'<strong>{pkg["name"]}</strong><br>'
                f'<small>📐 {pkg["length"]:.2f}×{pkg["width"]:.2f}×{pkg["height"]:.2f} m'
                f' | {vol:.3f} m³'
                + (f' | ⚖️ {pkg["weight"]} kg' if pkg.get("weight") else "")
                + "</small></div>",
                unsafe_allow_html=True,
            )
            qty = st.number_input(
                "Cantidad",
                min_value=0, max_value=500, step=1, value=0,
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
            "quantity":   qty_inputs[pkg["id"]],
        }
        for pkg in packages
        if qty_inputs[pkg["id"]] > 0
    ]

    total_boxes = sum(i["quantity"] for i in selected_items)
    total_vol_boxes = sum(
        i["length"] * i["width"] * i["height"] * i["quantity"]
        for i in selected_items
    )
    theoretical_eff = min(100, total_vol_boxes / truck_vol * 100) if truck_vol > 0 else 0

    if selected_items:
        st.markdown("---")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Total de bultos",  total_boxes)
        mc2.metric("Volumen de bultos", f"{total_vol_boxes:.2f} m³")
        mc3.metric("Eficiencia máx. posible", f"{theoretical_eff:.1f}%")

    st.markdown("---")

    # ── Generate plan ─────────────────────────────────────────────────────────
    if st.button("🚀 Generar Plan de Carga", type="primary", use_container_width=True,
                 disabled=len(selected_items) == 0):
        if not plan_name.strip():
            st.error("⚠️ Poné un nombre al plan antes de generarlo.")
        else:
            with st.spinner("⚙️ Calculando la mejor distribución…"):
                packed, unpacked, efficiency = packing.run_packing(
                    truck_l, truck_w, truck_h, selected_items
                )

            # Save to DB
            db.save_plan(
                name=plan_name.strip(),
                truck_l=truck_l, truck_w=truck_w, truck_h=truck_h,
                items=selected_items,
                packed_boxes=packed,
                unpacked_boxes=unpacked,
                notes=plan_notes,
            )

            # Store in session for display below
            st.session_state["last_packed"]   = packed
            st.session_state["last_unpacked"] = unpacked
            st.session_state["last_eff"]      = efficiency
            st.session_state["last_truck"]    = (truck_l, truck_w, truck_h)
            st.session_state["last_name"]     = plan_name.strip()
            st.rerun()

    # ── Display results ───────────────────────────────────────────────────────
    if st.session_state.get("last_packed") is not None:
        packed      = st.session_state["last_packed"]
        unpacked    = st.session_state["last_unpacked"]
        efficiency  = st.session_state["last_eff"]
        tl, tw, th  = st.session_state["last_truck"]

        st.success(f"✅ Plan generado y guardado: **{st.session_state['last_name']}**")

        # Metrics
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Bultos cargados",    len(packed))
        r2.metric("Sin cargar",         len(unpacked))
        r3.metric("Eficiencia",         f"{efficiency:.1f}%")
        used_vol = sum(b["placed_l"] * b["placed_w"] * b["placed_h"] for b in packed)
        r4.metric("Vol. utilizado",     f"{used_vol:.2f} m³")

        # Efficiency bar
        bar_color = "#2A9D8F" if efficiency >= 70 else ("#E9C46A" if efficiency >= 40 else "#E63946")
        st.markdown(
            f'<div class="eff-bar-wrap">'
            f'<div class="eff-bar" style="width:{efficiency}%;background:{bar_color};"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Eficiencia de llenado: {efficiency:.1f}%")

        # 3D figure
        st.plotly_chart(
            viz.build_figure(tl, tw, th, packed, unpacked, efficiency),
            use_container_width=True,
        )

        # Top-down 2D layer view
        if packed:
            st.subheader("🗺️ Vista superior por capas")
            fig2d = viz.build_2d_layers(tl, tw, th, packed)
            st.plotly_chart(fig2d, use_container_width=True)

        # Unpacked warning
        if unpacked:
            st.warning(
                f"⚠️ **{len(unpacked)} bulto(s) no pudieron ser cargados** porque no entraron en el camión.\n\n"
                + "\n".join(f"- {b['name']} ({b['length']:.2f}×{b['width']:.2f}×{b['height']:.2f} m)" for b in unpacked)
            )

        # Box list table
        with st.expander("📋 Detalle de posicionamiento"):
            rows = [
                {
                    "Bulto": b["name"],
                    "X (m)": f"{b['x']:.2f}",
                    "Y (m)": f"{b['y']:.2f}",
                    "Z (m)": f"{b['z']:.2f}",
                    "L×A×H": f"{b['placed_l']:.2f}×{b['placed_w']:.2f}×{b['placed_h']:.2f}",
                    "Vol (m³)": f"{b['placed_l']*b['placed_w']*b['placed_h']:.3f}",
                }
                for b in packed
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 – HISTORIAL DE PLANES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Historial de Planes":
    st.title("📋 Historial de Planes de Carga")

    plans = db.get_plans()
    if not plans:
        st.info("Aún no hay planes guardados. Creá uno desde **Nuevo Plan de Carga**.")
        st.stop()

    _ss("viewing_plan", None)

    # ── Plan list ─────────────────────────────────────────────────────────────
    for plan in plans:
        with st.container():
            c1, c2, c3 = st.columns([0.5, 0.35, 0.15])
            with c1:
                eff = plan["efficiency"]
                badge_color = "#2A9D8F" if eff >= 70 else ("#E9C46A" if eff >= 40 else "#E63946")
                st.markdown(
                    f'<span style="background:{badge_color};color:white;'
                    f'padding:2px 8px;border-radius:12px;font-size:.75rem;">'
                    f'{eff:.0f}%</span> &nbsp;'
                    f'<strong style="font-size:1.05rem;">{plan["name"]}</strong><br>'
                    f'<small style="color:#888;">📅 {plan["created_at"]}</small>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"📦 **{plan['packed_count']}** cargados"
                    + (f" | ⚠️ {plan['unpacked_count']} sin cargar" if plan["unpacked_count"] else "")
                    + f"<br><small>Camión: {plan['truck_length']}×{plan['truck_width']}×{plan['truck_height']} m</small>",
                    unsafe_allow_html=True,
                )
            with c3:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("👁️", key=f"view_{plan['id']}", help="Ver plan"):
                        if st.session_state.get("viewing_plan") == plan["id"]:
                            st.session_state["viewing_plan"] = None
                        else:
                            st.session_state["viewing_plan"] = plan["id"]
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️", key=f"dplan_{plan['id']}", help="Eliminar"):
                        db.delete_plan(plan["id"])
                        if st.session_state.get("viewing_plan") == plan["id"]:
                            st.session_state["viewing_plan"] = None
                        st.rerun()

            # ── Expanded view ─────────────────────────────────────────────────
            if st.session_state.get("viewing_plan") == plan["id"]:
                full = db.get_plan(plan["id"])
                packed   = full["packed_boxes"]
                unpacked = full["unpacked_boxes"]

                st.markdown("---")

                # Header info
                hi1, hi2, hi3, hi4 = st.columns(4)
                hi1.metric("Eficiencia",     f"{full['efficiency']:.1f}%")
                hi2.metric("Cargados",       full["packed_count"])
                hi3.metric("Sin cargar",     full["unpacked_count"])
                hi4.metric("Vol. utilizado", f"{full['used_volume']:.2f} m³")

                if full.get("notes"):
                    st.info(f"📝 {full['notes']}")

                if packed:
                    # 3D vis
                    fig = viz.build_figure(
                        full["truck_length"], full["truck_width"], full["truck_height"],
                        packed, unpacked, full["efficiency"]
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # 2D top-down
                    fig2d = viz.build_2d_layers(
                        full["truck_length"], full["truck_width"], full["truck_height"],
                        packed
                    )
                    st.plotly_chart(fig2d, use_container_width=True)

                    # Detail table
                    with st.expander("📋 Detalle de bultos cargados"):
                        rows = [
                            {
                                "Bulto": b["name"],
                                "Posición (X,Y,Z)": f"{b['x']:.2f},{b['y']:.2f},{b['z']:.2f}",
                                "Dimensiones": f"{b['placed_l']:.2f}×{b['placed_w']:.2f}×{b['placed_h']:.2f}",
                                "Vol (m³)": f"{b['placed_l']*b['placed_w']*b['placed_h']:.3f}",
                            }
                            for b in packed
                        ]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                if unpacked:
                    st.warning(
                        f"⚠️ **{len(unpacked)} bulto(s) no cargados:**\n"
                        + "\n".join(f"- {b['name']}" for b in unpacked)
                    )

                # Items summary
                with st.expander("📦 Resumen de bultos del plan"):
                    items = full.get("items", [])
                    if items:
                        rows2 = [
                            {
                                "Bulto":    it["name"],
                                "Cantidad": it["quantity"],
                                "L×A×H":    f"{it['length']:.2f}×{it['width']:.2f}×{it['height']:.2f} m",
                                "Vol unit": f"{it['length']*it['width']*it['height']:.3f} m³",
                                "Vol total":f"{it['length']*it['width']*it['height']*it['quantity']:.3f} m³",
                            }
                            for it in items
                        ]
                        st.dataframe(pd.DataFrame(rows2), use_container_width=True, hide_index=True)

                st.markdown("---")

        st.markdown("")   # spacing between cards
