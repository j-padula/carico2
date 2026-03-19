"""
🚛 Gestor de Carga de Camiones / Gestore Carico Camion / Truck Loader
Streamlit app – multilingual (ES / IT / EN)  +  PackVol-style loading rules
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import inspect as _inspect

import database as db
import packing
import visualization as viz
from translations import get_t

# ── DB compatibility: works with old database.py (no position_rule/load_priority)
# and new database.py (with those params). Checked once at startup. ──────────
_RUN_PACKING_PARAMS = set(_inspect.signature(packing.run_packing).parameters)

def _run_packing(truck_l, truck_w, truck_h, items, loading_dir, prefer_columns):
    kwargs = {}
    if "loading_dir"     in _RUN_PACKING_PARAMS: kwargs["loading_dir"]     = loading_dir
    if "prefer_columns"  in _RUN_PACKING_PARAMS: kwargs["prefer_columns"]  = prefer_columns
    return packing.run_packing(truck_l, truck_w, truck_h, items, **kwargs)
_UPD_PKG_PARAMS  = set(_inspect.signature(db.update_package).parameters)

def _db_add_package(name, l, w, h, weight, desc,
                    category, tags, stackable, rotatable,
                    position_rule, load_priority):
    kwargs = dict(category=category, tags=tags,
                  stackable=stackable, rotatable=rotatable)
    if "position_rule" in _ADD_PKG_PARAMS:
        kwargs["position_rule"] = position_rule
    if "load_priority" in _ADD_PKG_PARAMS:
        kwargs["load_priority"] = load_priority
    db.add_package(name, l, w, h, weight, desc, **kwargs)

def _db_update_package(pkg_id, name, l, w, h, weight, desc,
                       category, tags, stackable, rotatable,
                       position_rule, load_priority):
    kwargs = dict(category=category, tags=tags,
                  stackable=stackable, rotatable=rotatable)
    if "position_rule" in _UPD_PKG_PARAMS:
        kwargs["position_rule"] = position_rule
    if "load_priority" in _UPD_PKG_PARAMS:
        kwargs["load_priority"] = load_priority
    db.update_package(pkg_id, name, l, w, h, weight, desc, **kwargs)

st.set_page_config(
    page_title="Truck Loader", page_icon="🚛",
    layout="wide", initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
    border-radius:12px; padding:1rem 1.4rem; color:white;
}
div[data-testid="metric-container"] label { color:#a8dadc!important; font-size:.85rem; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"]
    { color:white!important; font-size:1.8rem; font-weight:700; }
[data-testid="stSidebar"] { background:#16213e; }
[data-testid="stSidebar"] * { color:#e0e0e0; }
.stButton > button { border-radius:8px; font-weight:600; transition:.2s; }
.stButton > button:hover { transform:translateY(-1px); box-shadow:0 4px 12px rgba(0,0,0,.3); }
.eff-bar-wrap { background:#ddd; border-radius:20px; height:22px; overflow:hidden; margin:4px 0 2px; }
.eff-bar { height:100%; border-radius:20px; transition:width .6s ease; }
.tag-pill { display:inline-block; padding:1px 8px; border-radius:12px;
            font-size:.72rem; font-weight:600; margin:1px 2px; background:#e9ecef; color:#495057; }
.cat-pill { display:inline-block; padding:2px 10px; border-radius:12px;
            font-size:.78rem; font-weight:700; margin:1px 2px; background:#264653; color:#a8dadc; }
.badge-yes { display:inline-block; padding:1px 7px; border-radius:10px;
             font-size:.7rem; font-weight:700; background:#2A9D8F; color:white; }
.badge-no  { display:inline-block; padding:1px 7px; border-radius:10px;
             font-size:.7rem; font-weight:700; background:#E63946; color:white; }
.badge-info{ display:inline-block; padding:1px 7px; border-radius:10px;
             font-size:.7rem; font-weight:700; background:#457B9D; color:white; }
.badge-warn{ display:inline-block; padding:1px 7px; border-radius:10px;
             font-size:.7rem; font-weight:700; background:#E9C46A; color:#333; }
.rule-box  { border-left:4px solid #457B9D; padding:8px 12px; border-radius:4px;
             background:rgba(69,123,157,.08); margin:6px 0; }
</style>
""", unsafe_allow_html=True)

db.init_db()

# ── Language ──────────────────────────────────────────────────────────────────
_LANG_OPTIONS = {"🇦🇷 Español":"es","🇮🇹 Italiano":"it","🇬🇧 English":"en"}
if "lang" not in st.session_state:
    st.session_state["lang"] = "es"

with st.sidebar:
    lang_label = st.selectbox(
        "🌐 Idioma / Language", list(_LANG_OPTIONS.keys()),
        index=list(_LANG_OPTIONS.values()).index(st.session_state["lang"]),
        key="lang_select",
    )
    st.session_state["lang"] = _LANG_OPTIONS[lang_label]

t    = get_t(st.session_state["lang"])
lang = st.session_state["lang"]

# ── Position-rule maps ────────────────────────────────────────────────────────
POS_RULE_LABELS = lambda: {
    "any":       t("pos_any"),
    "floor_only":t("pos_floor"),
    "top_only":  t("pos_top"),
    "no_floor":  t("pos_no_floor"),
}
POS_BADGE = {
    "any":       ("badge-info", "badge_pos_any"),
    "floor_only":("badge-warn", "badge_pos_floor"),
    "top_only":  ("badge-yes",  "badge_pos_top"),
    "no_floor":  ("badge-no",   "badge_pos_no_floor"),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def _ss(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

def _tag_html(tags_str):
    return "".join(
        f'<span class="tag-pill">#{s.strip()}</span>'
        for s in (tags_str or "").split(",") if s.strip()
    )

def _pos_badge_html(rule):
    cls, key = POS_BADGE.get(rule, ("badge-info","badge_pos_any"))
    return f'<span class="{cls}">{t(key)}</span>'

def _badges(pkg):
    parts = []
    if pkg.get("category"):
        parts.append(f'<span class="cat-pill">{pkg["category"]}</span>')
    parts.append(
        f'<span class="badge-yes">{t("badge_stackable")}</span>'
        if bool(pkg.get("stackable",1)) else
        f'<span class="badge-no">{t("badge_no_stack")}</span>'
    )
    parts.append(
        f'<span class="badge-info">{t("badge_rotatable")}</span>'
        if bool(pkg.get("rotatable",1)) else
        f'<span class="badge-no">{t("badge_no_rotate")}</span>'
    )
    parts.append(_pos_badge_html(pkg.get("position_rule","any")))
    prio = pkg.get("load_priority", 5)
    if prio != 5:
        cls = "badge-yes" if prio >= 7 else ("badge-warn" if prio >= 4 else "badge-no")
        parts.append(f'<span class="{cls}">{t("badge_prio",p=prio)}</span>')
    tags = _tag_html(pkg.get("tags",""))
    if tags: parts.append(tags)
    return " ".join(parts)

def _eff_bar(efficiency):
    color = "#2A9D8F" if efficiency>=70 else ("#E9C46A" if efficiency>=40 else "#E63946")
    st.markdown(
        f'<div class="eff-bar-wrap"><div class="eff-bar" style="width:{efficiency:.1f}%;background:{color};"></div></div>',
        unsafe_allow_html=True,
    )
    st.caption(t("eff_caption", e=efficiency))

def _safe_cats():
    try:
        return db.get_categories() if hasattr(db,"get_categories") else []
    except Exception:
        return []

def _viz_figure(tl,tw,th,packed,unpacked,eff,t_fn):
    sig = _inspect.signature(viz.build_figure)
    return viz.build_figure(tl,tw,th,packed,unpacked,eff,t=t_fn) if "t" in sig.parameters \
           else viz.build_figure(tl,tw,th,packed,unpacked,eff)

def _viz_2d(tl,tw,th,packed,t_fn):
    sig = _inspect.signature(viz.build_2d_layers)
    return viz.build_2d_layers(tl,tw,th,packed,t=t_fn) if "t" in sig.parameters \
           else viz.build_2d_layers(tl,tw,th,packed)

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 🚛 {t('app_title')}")
    st.markdown("---")
    nav_options = [t("nav_packages"),t("nav_new_plan"),t("nav_history")]
    page = st.radio("nav", nav_options, label_visibility="collapsed")
    st.markdown("---")
    all_pkgs  = db.get_packages()
    all_plans = db.get_plans()
    st.metric(t("sidebar_packages"), len(all_pkgs))
    st.metric(t("sidebar_plans"),    len(all_plans))
    cats = _safe_cats()
    if cats:
        st.markdown(t("sidebar_categories"))
        for c in cats:
            st.markdown(f'<span class="cat-pill">{c}</span>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 – PACKAGES
# ══════════════════════════════════════════════════════════════════════════════
if page == t("nav_packages"):
    st.title(t("pg1_title"))
    st.markdown(t("pg1_subtitle"))

    pos_labels = POS_RULE_LABELS()
    pos_keys   = list(pos_labels.keys())
    pos_vals   = list(pos_labels.values())

    with st.expander(t("add_package_expander"), expanded=len(all_pkgs)==0):
        with st.form("add_pkg", clear_on_submit=True):
            fa1, fa2 = st.columns(2)
            with fa1:
                new_name = st.text_input(t("field_name"), placeholder=t("field_name_ph"))
                new_desc = st.text_input(t("field_desc"), placeholder=t("field_desc_ph"))
            with fa2:
                ec = [""] + _safe_cats()
                cat_sel = st.selectbox(t("field_cat_existing"), ec,
                                       format_func=lambda x: t("field_cat_none") if x=="" else x)
                cat_new  = st.text_input(t("field_cat_new"), placeholder=t("field_cat_new_ph"))
                new_tags = st.text_input(t("field_tags"),    placeholder=t("field_tags_ph"))

            st.markdown(t("dims_title"))
            fd1,fd2,fd3,fd4 = st.columns(4)
            with fd1: new_l = st.number_input(t("field_length"), min_value=0.01,step=0.01,value=1.0,format="%.2f")
            with fd2: new_w = st.number_input(t("field_width"),  min_value=0.01,step=0.01,value=0.8,format="%.2f")
            with fd3: new_h = st.number_input(t("field_height"), min_value=0.01,step=0.01,value=1.2,format="%.2f")
            with fd4: new_weight = st.number_input(t("field_weight"), min_value=0.0,step=0.5,value=0.0)

            st.markdown(t("behaviour_title"))
            bc1,bc2 = st.columns(2)
            with bc1:
                new_stack = st.checkbox(t("chk_stackable"),value=True, help=t("chk_stackable_help"))
            with bc2:
                new_rot   = st.checkbox(t("chk_rotatable"),value=True, help=t("chk_rotatable_help"))

            bp1,bp2 = st.columns(2)
            with bp1:
                pos_sel = st.selectbox(t("field_pos_rule"), pos_vals,
                                       index=0, help=t("pos_rule_help"))
                new_pos_rule = pos_keys[pos_vals.index(pos_sel)]
            with bp2:
                new_prio = st.slider(t("field_priority"), 1, 10, 5,
                                     help=t("field_priority_help"))

            if st.form_submit_button(t("btn_save_package"), use_container_width=True):
                if not new_name.strip():
                    st.error(t("msg_name_required"))
                else:
                    final_cat = cat_new.strip() if cat_new.strip() else cat_sel
                    _db_add_package(
                        new_name.strip(), new_l, new_w, new_h, new_weight, new_desc,
                        category=final_cat, tags=new_tags,
                        stackable=new_stack, rotatable=new_rot,
                        position_rule=new_pos_rule, load_priority=new_prio,
                    )
                    st.success(t("msg_pkg_added", name=new_name.strip()))
                    st.rerun()

    st.markdown("---")

    cats = _safe_cats()
    fc1,fc2 = st.columns([1,2])
    with fc1:
        cat_filter = st.selectbox(t("filter_category"), [t("filter_all")]+cats, key="cat_filter")
    with fc2:
        search_q = st.text_input(t("filter_search"), placeholder=t("filter_search_ph"))

    packages = db.get_packages(category_filter=cat_filter if cat_filter!=t("filter_all") else None)
    if search_q.strip():
        packages = [p for p in packages if search_q.lower() in p["name"].lower()]

    st.subheader(t("pkg_list_title", n=len(packages)))
    _ss("editing_pkg", None)

    if not packages:
        st.info(t("no_packages"))

    for pkg in packages:
        vol = pkg["length"]*pkg["width"]*pkg["height"]
        with st.container():
            c_col,info_col,dim_col,act_col = st.columns([0.05,0.42,0.33,0.20])
            with c_col:
                st.markdown(
                    f'<div style="width:28px;height:60px;border-radius:6px;'
                    f'background:{pkg["color"]};margin-top:2px;'
                    f'border:2px solid rgba(0,0,0,.2);"></div>',
                    unsafe_allow_html=True,
                )
            with info_col:
                st.markdown(f"**{pkg['name']}**")
                st.markdown(_badges(pkg), unsafe_allow_html=True)
                if pkg.get("description"): st.caption(pkg["description"])
            with dim_col:
                st.markdown(
                    f"📐 `{pkg['length']:.2f}`×`{pkg['width']:.2f}`×`{pkg['height']:.2f}` m<br>"
                    f"<small>Vol: `{vol:.3f} m³`"
                    +(f"  |  ⚖️ {pkg['weight']} kg" if pkg.get("weight") else "")
                    +"</small>",
                    unsafe_allow_html=True,
                )
            with act_col:
                ce,cd = st.columns(2)
                with ce:
                    if st.button("✏️",key=f"edit_{pkg['id']}",help=t("btn_edit")):
                        st.session_state["editing_pkg"] = (
                            None if st.session_state.get("editing_pkg")==pkg["id"] else pkg["id"]
                        )
                with cd:
                    if st.button("🗑️",key=f"del_{pkg['id']}",help=t("btn_delete")):
                        db.delete_package(pkg["id"]); st.rerun()

            if st.session_state.get("editing_pkg")==pkg["id"]:
                with st.form(f"edit_{pkg['id']}"):
                    st.markdown(t("edit_title",name=pkg["name"]))
                    ef1,ef2 = st.columns(2)
                    with ef1:
                        e_name = st.text_input(t("field_name"),value=pkg["name"])
                        e_desc = st.text_input(t("field_desc"),value=pkg.get("description",""))
                    with ef2:
                        ec2  = [""]+_safe_cats()
                        ec_i = ec2.index(pkg.get("category","")) if pkg.get("category","") in ec2 else 0
                        e_cat_sel = st.selectbox(t("field_cat_existing"),ec2,index=ec_i,
                                                 format_func=lambda x: t("field_cat_none_short") if x=="" else x)
                        e_cat_new = st.text_input(t("field_cat_new_edit"),value="")
                        e_tags    = st.text_input(t("field_tags"),value=pkg.get("tags",""))
                    ed1,ed2,ed3,ed4 = st.columns(4)
                    with ed1: e_l = st.number_input(t("field_length"),value=float(pkg["length"]),min_value=0.01,step=0.01,format="%.2f")
                    with ed2: e_w = st.number_input(t("field_width"), value=float(pkg["width"]), min_value=0.01,step=0.01,format="%.2f")
                    with ed3: e_h = st.number_input(t("field_height"),value=float(pkg["height"]),min_value=0.01,step=0.01,format="%.2f")
                    with ed4: e_weight = st.number_input(t("field_weight"),value=float(pkg.get("weight",0)),min_value=0.0,step=0.5)
                    eb1,eb2 = st.columns(2)
                    with eb1: e_stack = st.checkbox(t("chk_stackable"),value=bool(pkg.get("stackable",1)))
                    with eb2: e_rot   = st.checkbox(t("chk_rotatable"),value=bool(pkg.get("rotatable",1)))
                    cur_rule = pkg.get("position_rule","any")
                    e_pos_val= st.selectbox(t("field_pos_rule"), pos_vals,
                                            index=pos_keys.index(cur_rule) if cur_rule in pos_keys else 0)
                    e_pos_rule = pos_keys[pos_vals.index(e_pos_val)]
                    e_prio = st.slider(t("field_priority"),1,10,int(pkg.get("load_priority",5)))
                    sb1,sb2 = st.columns(2)
                    with sb1:
                        if st.form_submit_button(t("btn_save"),use_container_width=True):
                            final_cat = e_cat_new.strip() if e_cat_new.strip() else e_cat_sel
                            _db_update_package(
                                pkg["id"],e_name,e_l,e_w,e_h,e_weight,e_desc,
                                category=final_cat,tags=e_tags,
                                stackable=e_stack,rotatable=e_rot,
                                position_rule=e_pos_rule,load_priority=e_prio,
                            )
                            st.session_state["editing_pkg"]=None; st.rerun()
                    with sb2:
                        if st.form_submit_button(t("btn_cancel"),use_container_width=True):
                            st.session_state["editing_pkg"]=None; st.rerun()

            st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 – NEW PLAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == t("nav_new_plan"):
    st.title(t("pg2_title"))

    packages = db.get_packages()
    if not packages:
        st.warning(t("pg2_no_packages")); st.stop()

    # Step 1
    st.subheader(t("step1_title"))
    p1,p2 = st.columns(2)
    with p1:
        plan_name  = st.text_input(t("field_plan_name"),placeholder=t("field_plan_name_ph"),key="plan_name")
        st.caption(t("field_auto_date",dt=datetime.now().strftime("%Y-%m-%d %H:%M")))
    with p2:
        plan_notes = st.text_area(t("field_notes"),height=90,placeholder=t("field_notes_ph"),key="plan_notes")

    st.markdown("---")

    # Step 2: truck + loading options
    st.subheader(t("step2_title"))
    preset_keys = ["truck_custom","truck_medium","truck_semi","truck_20ft","truck_40ft","truck_van"]
    preset_vals_map = {
        "truck_custom":(7.0,2.4,2.5),"truck_medium":(7.0,2.4,2.5),
        "truck_semi":(12.0,2.4,2.6),"truck_20ft":(5.9,2.35,2.39),
        "truck_40ft":(12.0,2.35,2.39),"truck_van":(3.0,1.8,1.9),
    }
    preset_labels = [t(k) for k in preset_keys]
    preset_sel    = st.selectbox(t("truck_template"),preset_labels)
    chosen_key    = preset_keys[preset_labels.index(preset_sel)]
    pv            = preset_vals_map[chosen_key]

    tc1,tc2,tc3 = st.columns(3)
    with tc1: truck_l = st.number_input(t("truck_length_m"),min_value=0.1,value=float(pv[0]),step=0.1,format="%.2f")
    with tc2: truck_w = st.number_input(t("truck_width_m"), min_value=0.1,value=float(pv[1]),step=0.1,format="%.2f")
    with tc3: truck_h = st.number_input(t("truck_height_m"),min_value=0.1,value=float(pv[2]),step=0.1,format="%.2f")
    truck_vol = truck_l*truck_w*truck_h
    st.info(t("truck_total_vol",v=truck_vol))

    # Loading options
    st.markdown(t("loading_opts_title"))
    lo1,lo2 = st.columns(2)
    with lo1:
        dir_options = [t("dir_front_back"), t("dir_back_front")]
        dir_sel     = st.selectbox(t("field_loading_dir"), dir_options, key="loading_dir")
        loading_dir = "back_front" if dir_sel==t("dir_back_front") else "front_back"
    with lo2:
        prefer_columns = st.checkbox(t("chk_columns"), value=False,
                                     help=t("chk_columns_help"), key="prefer_columns")

    st.markdown("---")

    # Step 3: packages
    st.subheader(t("step3_title"))
    cats_for_plan   = [t("filter_all")]+_safe_cats()
    plan_cat_filter = st.selectbox(t("filter_category"),cats_for_plan,key="plan_cat_filter")
    packages_plan   = db.get_packages(
        category_filter=plan_cat_filter if plan_cat_filter!=t("filter_all") else None
    )
    st.markdown(t("step3_subtitle"))

    qty_inputs = {}
    pkg_cols   = st.columns(min(len(packages_plan),3))
    for i,pkg in enumerate(packages_plan):
        col = pkg_cols[i%3]
        vol = pkg["length"]*pkg["width"]*pkg["height"]
        with col:
            st.markdown(
                f'<div class="rule-box">'
                f'<strong style="border-left:3px solid {pkg["color"]};padding-left:6px;">{pkg["name"]}</strong><br>'
                + _badges(pkg) +
                f'<br><small>📐 {pkg["length"]:.2f}×{pkg["width"]:.2f}×{pkg["height"]:.2f} m'
                f' | {vol:.3f} m³'
                +(f' | ⚖️ {pkg["weight"]} kg' if pkg.get("weight") else "")
                +'</small></div>',
                unsafe_allow_html=True,
            )
            qty = st.number_input("qty",min_value=0,max_value=500,step=1,value=0,
                                  key=f"qty_{pkg['id']}",label_visibility="collapsed")
            qty_inputs[pkg["id"]] = qty

    selected_items = [
        {
            "package_id":   pkg["id"],
            "name":         pkg["name"],
            "length":       pkg["length"],
            "width":        pkg["width"],
            "height":       pkg["height"],
            "weight":       pkg.get("weight",0),
            "color":        pkg["color"],
            "stackable":    bool(pkg.get("stackable",1)),
            "rotatable":    bool(pkg.get("rotatable",1)),
            "position_rule":pkg.get("position_rule","any"),
            "load_priority":int(pkg.get("load_priority",5)),
            "category":     pkg.get("category",""),
            "tags":         pkg.get("tags",""),
            "quantity":     qty_inputs.get(pkg["id"],0),
        }
        for pkg in packages_plan if qty_inputs.get(pkg["id"],0)>0
    ]

    if selected_items:
        st.markdown("---")
        mc1,mc2,mc3 = st.columns(3)
        tb  = sum(i["quantity"] for i in selected_items)
        tvb = sum(i["length"]*i["width"]*i["height"]*i["quantity"] for i in selected_items)
        mc1.metric(t("metric_total_boxes"), tb)
        mc2.metric(t("metric_total_vol"),   f"{tvb:.2f} m³")
        mc3.metric(t("metric_max_eff"),     f"{min(100,tvb/truck_vol*100):.1f}%")

        # Warnings per rule type
        for rule,warn_key in [("floor_only","warn_floor_only"),("top_only","warn_top_only"),
                               ("no_floor","warn_top_only")]:
            names = [i["name"] for i in selected_items if i["position_rule"]==rule]
            if names:
                st.warning(t(warn_key, names=", ".join(f"**{n}**" for n in names)))
        no_stack = [i["name"] for i in selected_items if not i["stackable"]]
        if no_stack:
            st.warning(t("warn_no_stack",names=", ".join(f"**{n}**" for n in no_stack)))
        no_rot = [i["name"] for i in selected_items if not i["rotatable"]]
        if no_rot:
            st.warning(t("warn_no_rotate",names=", ".join(f"**{n}**" for n in no_rot)))

    st.markdown("---")

    if st.button(t("btn_generate"),type="primary",
                 use_container_width=True,disabled=len(selected_items)==0):
        if not plan_name.strip():
            st.error(t("err_no_plan_name"))
        else:
            with st.spinner(t("spinner_packing")):
                packed,unpacked,efficiency = _run_packing(
                    truck_l,truck_w,truck_h,selected_items,
                    loading_dir=loading_dir,
                    prefer_columns=prefer_columns,
                )
            db.save_plan(
                name=plan_name.strip(),
                truck_l=truck_l,truck_w=truck_w,truck_h=truck_h,
                items=selected_items,
                packed_boxes=packed,unpacked_boxes=unpacked,
                notes=plan_notes,
            )
            st.session_state.update({
                "last_packed":packed,"last_unpacked":unpacked,
                "last_eff":efficiency,"last_truck":(truck_l,truck_w,truck_h),
                "last_name":plan_name.strip(),
            })
            st.rerun()

    if st.session_state.get("last_packed") is not None:
        packed     = st.session_state["last_packed"]
        unpacked   = st.session_state["last_unpacked"]
        efficiency = st.session_state["last_eff"]
        tl,tw,th   = st.session_state["last_truck"]

        st.success(t("success_plan_saved",name=st.session_state["last_name"]))
        r1,r2,r3,r4 = st.columns(4)
        r1.metric(t("metric_loaded"),   len(packed))
        r2.metric(t("metric_unloaded"), len(unpacked))
        r3.metric(t("metric_efficiency"),f"{efficiency:.1f}%")
        used_vol = sum(b["placed_l"]*b["placed_w"]*b["placed_h"] for b in packed)
        r4.metric(t("metric_vol_used"), f"{used_vol:.2f} m³")
        _eff_bar(efficiency)

        st.plotly_chart(_viz_figure(tl,tw,th,packed,unpacked,efficiency,t),use_container_width=True)

        if packed:
            st.subheader(t("top_view_title"))
            st.plotly_chart(_viz_2d(tl,tw,th,packed,t),use_container_width=True)

        if unpacked:
            st.warning(
                t("warn_unpacked",n=len(unpacked))+"\n\n"
                +"\n".join(f"- {b['name']} ({b['length']:.2f}×{b['width']:.2f}×{b['height']:.2f} m)" for b in unpacked)
            )

        with st.expander(t("detail_expander")):
            rows = [{
                t("col_package"): b["name"],
                t("col_x"):       f"{b['x']:.2f}",
                t("col_y"):       f"{b['y']:.2f}",
                t("col_z"):       f"{b['z']:.2f}",
                t("col_dims"):    f"{b['placed_l']:.2f}×{b['placed_w']:.2f}×{b['placed_h']:.2f}",
                t("col_stackable"):"✅" if b.get("stackable",True) else "⛔",
                t("col_rotated"): "🔄" if abs(b["placed_l"]-b["length"])>1e-3 else "—",
                t("col_priority"):b.get("load_priority",5),
            } for b in packed]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 – HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == t("nav_history"):
    st.title(t("pg3_title"))
    plans = db.get_plans()
    if not plans:
        st.info(t("pg3_no_plans")); st.stop()

    _ss("viewing_plan",None)

    for plan in plans:
        eff = plan["efficiency"]
        badge_color = "#2A9D8F" if eff>=70 else ("#E9C46A" if eff>=40 else "#E63946")
        with st.container():
            hc1,hc2,hc3 = st.columns([0.50,0.35,0.15])
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
                unl = t("lbl_unloaded_n",n=plan["unpacked_count"]) if plan["unpacked_count"] else ""
                st.markdown(
                    t("lbl_loaded_n",n=plan["packed_count"])+unl+
                    f'<br><small>'+t("lbl_truck_dims",l=plan["truck_length"],
                    w=plan["truck_width"],h=plan["truck_height"])+"</small>",
                    unsafe_allow_html=True,
                )
            with hc3:
                bc1,bc2 = st.columns(2)
                with bc1:
                    if st.button("👁️",key=f"vp_{plan['id']}",help=t("btn_view")):
                        st.session_state["viewing_plan"] = (
                            None if st.session_state.get("viewing_plan")==plan["id"] else plan["id"]
                        )
                        st.rerun()
                with bc2:
                    if st.button("🗑️",key=f"dp_{plan['id']}",help=t("btn_delete")):
                        db.delete_plan(plan["id"])
                        if st.session_state.get("viewing_plan")==plan["id"]:
                            st.session_state["viewing_plan"]=None
                        st.rerun()

            if st.session_state.get("viewing_plan")==plan["id"]:
                full     = db.get_plan(plan["id"])
                packed   = full["packed_boxes"]
                unpacked = full["unpacked_boxes"]
                st.markdown("---")
                hi1,hi2,hi3,hi4 = st.columns(4)
                hi1.metric(t("metric_efficiency"), f"{full['efficiency']:.1f}%")
                hi2.metric(t("metric_loaded"),     full["packed_count"])
                hi3.metric(t("metric_unloaded"),   full["unpacked_count"])
                hi4.metric(t("metric_vol_used2"),  f"{full['used_volume']:.2f} m³")
                _eff_bar(full["efficiency"])
                if full.get("notes"): st.info(f"📝 {full['notes']}")

                if packed:
                    st.plotly_chart(
                        _viz_figure(full["truck_length"],full["truck_width"],full["truck_height"],
                                    packed,unpacked,full["efficiency"],t),
                        use_container_width=True,
                    )
                    st.subheader(t("top_view_title"))
                    st.plotly_chart(
                        _viz_2d(full["truck_length"],full["truck_width"],full["truck_height"],packed,t),
                        use_container_width=True,
                    )
                    with st.expander(t("detail_expander")):
                        rows = [{
                            t("col_package"):  b["name"],
                            t("col_position"): f"({b['x']:.2f},{b['y']:.2f},{b['z']:.2f})",
                            t("col_dims"):     f"{b['placed_l']:.2f}×{b['placed_w']:.2f}×{b['placed_h']:.2f}",
                            t("col_stackable"):"✅" if b.get("stackable",True) else "⛔",
                            t("col_rotated"):  "🔄" if abs(b["placed_l"]-b["length"])>1e-3 else "—",
                            t("col_priority"): b.get("load_priority",5),
                        } for b in packed]
                        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

                if unpacked:
                    st.warning(", ".join(b["name"] for b in unpacked)+t("lbl_unpacked_list"))

                with st.expander(t("summary_expander")):
                    rows2 = [{
                        t("col_package"):   it["name"],
                        t("col_category"):  it.get("category",""),
                        t("col_qty"):       it["quantity"],
                        t("col_dims"):      f"{it['length']:.2f}×{it['width']:.2f}×{it['height']:.2f}",
                        t("col_stackable"): "✅" if it.get("stackable",True) else "⛔",
                        t("col_rotatable"): "🔄" if it.get("rotatable",True) else "📌",
                        t("col_pos_rule"):  it.get("position_rule","any"),
                        t("col_priority"):  it.get("load_priority",5),
                    } for it in full.get("items",[])]
                    st.dataframe(pd.DataFrame(rows2),use_container_width=True,hide_index=True)

                st.markdown("---")
        st.markdown("")
