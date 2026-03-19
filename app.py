"""
🚛 Gestor de Carga de Camiones – Streamlit app
Dimensions displayed/entered in cm; stored in meters internally.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import inspect as _inspect
import json

import database as db
import packing
import visualization as viz
from translations import get_t

st.set_page_config(page_title="Truck Loader", page_icon="🚛",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container{padding-top:1.5rem}
div[data-testid="metric-container"]{background:linear-gradient(135deg,#1a1a2e,#16213e);
  border-radius:12px;padding:1rem 1.4rem;color:white}
div[data-testid="metric-container"] label{color:#a8dadc!important;font-size:.85rem}
div[data-testid="metric-container"] div[data-testid="stMetricValue"]
  {color:white!important;font-size:1.8rem;font-weight:700}
[data-testid="stSidebar"]{background:#16213e}
[data-testid="stSidebar"] *{color:#e0e0e0}
.stButton>button{border-radius:8px;font-weight:600;transition:.2s}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.3)}
.eff-bar-wrap{background:#ddd;border-radius:20px;height:22px;overflow:hidden;margin:4px 0 2px}
.eff-bar{height:100%;border-radius:20px;transition:width .6s ease}
.tag-pill{display:inline-block;padding:1px 8px;border-radius:12px;font-size:.72rem;
  font-weight:600;margin:1px 2px;background:#e9ecef;color:#495057}
.cat-pill{display:inline-block;padding:2px 10px;border-radius:12px;font-size:.78rem;
  font-weight:700;margin:1px 2px;background:#264653;color:#a8dadc}
.badge-yes{display:inline-block;padding:1px 7px;border-radius:10px;font-size:.7rem;
  font-weight:700;background:#2A9D8F;color:white}
.badge-no{display:inline-block;padding:1px 7px;border-radius:10px;font-size:.7rem;
  font-weight:700;background:#E63946;color:white}
.badge-info{display:inline-block;padding:1px 7px;border-radius:10px;font-size:.7rem;
  font-weight:700;background:#457B9D;color:white}
.orient-card{border:2px solid #457B9D;border-radius:8px;padding:8px 10px;
  background:rgba(69,123,157,.08);margin:4px 0}
.orient-disabled{border:2px solid #aaa;border-radius:8px;padding:8px 10px;
  background:rgba(150,150,150,.06);margin:4px 0;opacity:.6}
.rule-box{border-left:4px solid #457B9D;padding:8px 12px;border-radius:4px;
  background:rgba(69,123,157,.08);margin:4px 0}
</style>
""", unsafe_allow_html=True)

db.init_db()

# ── Compatibility wrappers ────────────────────────────────────────────────────
_ADD_P  = set(_inspect.signature(db.add_package).parameters)
_UPD_P  = set(_inspect.signature(db.update_package).parameters)
_RUN_P  = set(_inspect.signature(packing.run_packing).parameters)

def _db_add(name, l, w, h, weight, desc, category, tags,
            stackable, rotatable, position_rule, load_priority, orient_rules):
    kw = dict(category=category, tags=tags, stackable=stackable, rotatable=rotatable)
    if "position_rule"  in _ADD_P: kw["position_rule"]  = position_rule
    if "load_priority"  in _ADD_P: kw["load_priority"]  = load_priority
    if "orient_rules"   in _ADD_P: kw["orient_rules"]   = orient_rules
    db.add_package(name, l, w, h, weight, desc, **kw)

def _db_upd(pid, name, l, w, h, weight, desc, category, tags,
            stackable, rotatable, position_rule, load_priority, orient_rules):
    kw = dict(category=category, tags=tags, stackable=stackable, rotatable=rotatable)
    if "position_rule"  in _UPD_P: kw["position_rule"]  = position_rule
    if "load_priority"  in _UPD_P: kw["load_priority"]  = load_priority
    if "orient_rules"   in _UPD_P: kw["orient_rules"]   = orient_rules
    db.update_package(pid, name, l, w, h, weight, desc, **kw)

def _run_pack(tl, tw, th, items, loading_dir, prefer_columns):
    kw = {}
    if "loading_dir"    in _RUN_P: kw["loading_dir"]    = loading_dir
    if "prefer_columns" in _RUN_P: kw["prefer_columns"] = prefer_columns
    return packing.run_packing(tl, tw, th, items, **kw)

def _viz_fig(tl,tw,th,packed,unpacked,eff,t_fn):
    sig = _inspect.signature(viz.build_figure)
    return viz.build_figure(tl,tw,th,packed,unpacked,eff,t=t_fn) \
           if "t" in sig.parameters else viz.build_figure(tl,tw,th,packed,unpacked,eff)

def _viz_2d(tl,tw,th,packed,t_fn):
    sig = _inspect.signature(viz.build_2d_layers)
    return viz.build_2d_layers(tl,tw,th,packed,t=t_fn) \
           if "t" in sig.parameters else viz.build_2d_layers(tl,tw,th,packed)

# ── Language ──────────────────────────────────────────────────────────────────
_LANGS = {"🇦🇷 Español":"es","🇮🇹 Italiano":"it","🇬🇧 English":"en"}
if "lang" not in st.session_state: st.session_state["lang"] = "es"

with st.sidebar:
    lbl = st.selectbox("🌐 Idioma / Language", list(_LANGS.keys()),
                       index=list(_LANGS.values()).index(st.session_state["lang"]),
                       key="lang_sel")
    st.session_state["lang"] = _LANGS[lbl]

t = get_t(st.session_state["lang"])

# ── Orientation rules helpers ─────────────────────────────────────────────────
RULE_VALS = lambda: {
    "disabled": t("rule_disabled"),
    "any":      t("rule_any"),
    "floor_only":t("rule_floor"),
    "top_only": t("rule_top"),
    "no_floor": t("rule_no_floor"),
}

def _orient_selector(key_prefix, label, default_rule, disabled=False):
    """Renders one orientation card; returns selected rule key."""
    rv = RULE_VALS()
    opts = list(rv.values())
    vals = list(rv.keys())
    idx  = vals.index(default_rule) if default_rule in vals else 1
    st.markdown(
        f'<div class="{"orient-disabled" if disabled else "orient-card"}">'
        f'<small><b>{label}</b></small></div>',
        unsafe_allow_html=True,
    )
    sel = st.selectbox("", opts, index=idx,
                       key=f"{key_prefix}_rule",
                       label_visibility="collapsed",
                       disabled=disabled)
    return vals[opts.index(sel)]

# ── Generic helpers ───────────────────────────────────────────────────────────
def _ss(k, d):
    if k not in st.session_state: st.session_state[k] = d
    return st.session_state[k]

def _tag_html(s):
    return "".join(f'<span class="tag-pill">#{x.strip()}</span>'
                   for x in (s or "").split(",") if x.strip())

def _badges(pkg):
    parts = []
    if pkg.get("category"):
        parts.append(f'<span class="cat-pill">{pkg["category"]}</span>')
    parts.append(f'<span class="badge-yes">{t("badge_stackable")}</span>'
                 if bool(pkg.get("stackable",1)) else
                 f'<span class="badge-no">{t("badge_no_stack")}</span>')
    parts.append(f'<span class="badge-info">{t("badge_rotatable")}</span>'
                 if bool(pkg.get("rotatable",1)) else
                 f'<span class="badge-no">{t("badge_no_rotate")}</span>')
    prio = int(pkg.get("load_priority",5))
    if prio != 5:
        cls = "badge-yes" if prio>=7 else ("badge-info" if prio>=4 else "badge-no")
        parts.append(f'<span class="{cls}">{t("badge_prio",p=prio)}</span>')
    tags = _tag_html(pkg.get("tags",""))
    if tags: parts.append(tags)
    return " ".join(parts)

def _eff_bar(e):
    c = "#2A9D8F" if e>=70 else ("#E9C46A" if e>=40 else "#E63946")
    st.markdown(
        f'<div class="eff-bar-wrap"><div class="eff-bar" '
        f'style="width:{e:.1f}%;background:{c};"></div></div>',
        unsafe_allow_html=True)
    st.caption(t("eff_caption",e=e))

def _safe_cats():
    try: return db.get_categories() if hasattr(db,"get_categories") else []
    except: return []

# cm ↔ m helpers
def _m2cm(v): return round(v * 100)
def _cm2m(v): return v / 100.0

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 🚛 {t('app_title')}")
    st.markdown("---")
    nav = [t("nav_packages"), t("nav_new_plan"), t("nav_history")]
    page = st.radio("nav", nav, label_visibility="collapsed")
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

    with st.expander(t("add_package_expander"), expanded=len(all_pkgs)==0):
        with st.form("add_pkg", clear_on_submit=True):
            fa1,fa2 = st.columns(2)
            with fa1:
                new_name = st.text_input(t("field_name"), placeholder=t("field_name_ph"))
                new_desc = st.text_input(t("field_desc"), placeholder=t("field_desc_ph"))
            with fa2:
                ec = [""]+_safe_cats()
                cat_sel = st.selectbox(t("field_cat_existing"), ec,
                                       format_func=lambda x: t("field_cat_none") if x=="" else x)
                cat_new  = st.text_input(t("field_cat_new"), placeholder=t("field_cat_new_ph"))
                new_tags = st.text_input(t("field_tags"), placeholder=t("field_tags_ph"))

            st.markdown(t("dims_title"))
            fd1,fd2,fd3,fd4 = st.columns(4)
            with fd1: new_l_cm = st.number_input(t("field_length"), min_value=1, step=1, value=100)
            with fd2: new_w_cm = st.number_input(t("field_width"),  min_value=1, step=1, value=80)
            with fd3: new_h_cm = st.number_input(t("field_height"), min_value=1, step=1, value=120)
            with fd4: new_weight = st.number_input(t("field_weight"), min_value=0.0, step=0.5, value=0.0)

            st.markdown(t("behaviour_title"))
            bc1,bc2,bc3 = st.columns(3)
            with bc1: new_stack = st.checkbox(t("chk_stackable"),value=True,help=t("chk_stackable_help"))
            with bc2: new_rot   = st.checkbox(t("chk_rotatable"),value=True,help=t("chk_rotatable_help"))
            with bc3: new_prio  = st.slider(t("field_priority"),1,10,5,help=t("field_priority_help"))

            # Orientation rules
            st.markdown(t("orient_title"))
            oc1,oc2 = st.columns(2)
            with oc1:
                lbl_a = f"{t('orient_A')}: {new_l_cm}×{new_w_cm} cm"
                rule_a = _orient_selector("new_A", lbl_a, "any")
            with oc2:
                lbl_b = f"{t('orient_B')}: {new_w_cm}×{new_l_cm} cm"
                rule_b = _orient_selector("new_B", lbl_b, "any", disabled=not new_rot)

            if st.form_submit_button(t("btn_save_package"), use_container_width=True):
                if not new_name.strip():
                    st.error(t("msg_name_required"))
                else:
                    final_cat = cat_new.strip() if cat_new.strip() else cat_sel
                    or_ = {"A": rule_a, "B": rule_b if new_rot else "disabled"}
                    _db_add(new_name.strip(),
                            _cm2m(new_l_cm), _cm2m(new_w_cm), _cm2m(new_h_cm),
                            new_weight, new_desc,
                            final_cat, new_tags, new_stack, new_rot,
                            "any", new_prio, or_)
                    st.success(t("msg_pkg_added",name=new_name.strip()))
                    st.rerun()

    st.markdown("---")

    cats = _safe_cats()
    fc1,fc2 = st.columns([1,2])
    with fc1:
        cat_filter = st.selectbox(t("filter_category"),[t("filter_all")]+cats,key="cf")
    with fc2:
        sq = st.text_input(t("filter_search"),placeholder=t("filter_search_ph"))

    packages = db.get_packages(category_filter=cat_filter if cat_filter!=t("filter_all") else None)
    if sq.strip(): packages=[p for p in packages if sq.lower() in p["name"].lower()]

    st.subheader(t("pkg_list_title",n=len(packages)))
    _ss("editing_pkg",None)
    if not packages: st.info(t("no_packages"))

    for pkg in packages:
        l_cm = _m2cm(pkg["length"]); w_cm = _m2cm(pkg["width"]); h_cm = _m2cm(pkg["height"])
        vol_cm3 = l_cm*w_cm*h_cm
        or_ = pkg.get("orient_rules") or {"A":"any","B":"any"}

        with st.container():
            cc,ic,dc,ac = st.columns([0.05,0.42,0.33,0.20])
            with cc:
                st.markdown(
                    f'<div style="width:28px;height:60px;border-radius:6px;'
                    f'background:{pkg["color"]};margin-top:2px;'
                    f'border:2px solid rgba(0,0,0,.2);"></div>',
                    unsafe_allow_html=True)
            with ic:
                st.markdown(f"**{pkg['name']}**")
                st.markdown(_badges(pkg),unsafe_allow_html=True)
                # Show orientation rules
                rv = RULE_VALS()
                a_txt = rv.get(or_.get("A","any"),or_.get("A","any"))
                b_txt = rv.get(or_.get("B","any"),or_.get("B","any")) if pkg.get("rotatable",1) else t("rule_disabled")
                st.caption(f"A: {l_cm}×{w_cm}cm → {a_txt}  |  B: {w_cm}×{l_cm}cm → {b_txt}")
                if pkg.get("description"): st.caption(pkg["description"])
            with dc:
                st.markdown(
                    f"📐 `{l_cm}`×`{w_cm}`×`{h_cm}` cm<br>"
                    f"<small>Vol: `{vol_cm3:,}` cm³"
                    +(f"  |  ⚖️ {pkg['weight']} kg" if pkg.get("weight") else "")
                    +"</small>", unsafe_allow_html=True)
            with ac:
                ce,cd = st.columns(2)
                with ce:
                    if st.button("✏️",key=f"e{pkg['id']}",help=t("btn_edit")):
                        st.session_state["editing_pkg"]=(
                            None if st.session_state.get("editing_pkg")==pkg["id"] else pkg["id"])
                with cd:
                    if st.button("🗑️",key=f"d{pkg['id']}",help=t("btn_delete")):
                        db.delete_package(pkg["id"]); st.rerun()

            # Inline edit
            if st.session_state.get("editing_pkg")==pkg["id"]:
                with st.form(f"ef{pkg['id']}"):
                    st.markdown(t("edit_title",name=pkg["name"]))
                    ef1,ef2 = st.columns(2)
                    with ef1:
                        e_name = st.text_input(t("field_name"),value=pkg["name"])
                        e_desc = st.text_input(t("field_desc"),value=pkg.get("description",""))
                    with ef2:
                        ec2   = [""]+_safe_cats()
                        ec_i  = ec2.index(pkg.get("category","")) if pkg.get("category","") in ec2 else 0
                        e_csel= st.selectbox(t("field_cat_existing"),ec2,index=ec_i,
                                             format_func=lambda x:t("field_cat_none_short") if x=="" else x)
                        e_cnew= st.text_input(t("field_cat_new_edit"),value="")
                        e_tags= st.text_input(t("field_tags"),value=pkg.get("tags",""))
                    ed1,ed2,ed3,ed4 = st.columns(4)
                    with ed1: e_l=st.number_input(t("field_length"),value=l_cm,min_value=1,step=1)
                    with ed2: e_w=st.number_input(t("field_width"), value=w_cm,min_value=1,step=1)
                    with ed3: e_h=st.number_input(t("field_height"),value=h_cm,min_value=1,step=1)
                    with ed4: e_wt=st.number_input(t("field_weight"),value=float(pkg.get("weight",0)),min_value=0.0,step=0.5)
                    eb1,eb2,eb3 = st.columns(3)
                    with eb1: e_stk=st.checkbox(t("chk_stackable"),value=bool(pkg.get("stackable",1)))
                    with eb2: e_rot=st.checkbox(t("chk_rotatable"),value=bool(pkg.get("rotatable",1)))
                    with eb3: e_prio=st.slider(t("field_priority"),1,10,int(pkg.get("load_priority",5)))

                    st.markdown(t("orient_title"))
                    eo1,eo2 = st.columns(2)
                    cur_or = pkg.get("orient_rules") or {"A":"any","B":"any"}
                    with eo1:
                        ea_lbl = f"{t('orient_A')}: {e_l}×{e_w} cm"
                        e_rule_a = _orient_selector(f"ea{pkg['id']}", ea_lbl, cur_or.get("A","any"))
                    with eo2:
                        eb_lbl = f"{t('orient_B')}: {e_w}×{e_l} cm"
                        e_rule_b = _orient_selector(f"eb{pkg['id']}", eb_lbl,
                                                    cur_or.get("B","any"), disabled=not e_rot)

                    sb1,sb2 = st.columns(2)
                    with sb1:
                        if st.form_submit_button(t("btn_save"),use_container_width=True):
                            fc2_ = e_cnew.strip() if e_cnew.strip() else e_csel
                            e_or = {"A":e_rule_a,"B":e_rule_b if e_rot else "disabled"}
                            _db_upd(pkg["id"],e_name,_cm2m(e_l),_cm2m(e_w),_cm2m(e_h),
                                    e_wt,e_desc,fc2_,e_tags,e_stk,e_rot,"any",e_prio,e_or)
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
    if not packages: st.warning(t("pg2_no_packages")); st.stop()

    # Step 1
    st.subheader(t("step1_title"))
    p1,p2 = st.columns(2)
    with p1:
        plan_name = st.text_input(t("field_plan_name"),placeholder=t("field_plan_name_ph"),key="pn")
        st.caption(t("field_auto_date",dt=datetime.now().strftime("%Y-%m-%d %H:%M")))
    with p2:
        plan_notes = st.text_area(t("field_notes"),height=90,placeholder=t("field_notes_ph"),key="notes")

    st.markdown("---")

    # Step 2: truck dimensions + options
    st.subheader(t("step2_title"))

    # Preset templates (values in cm for UI, convert to m for storage/packing)
    preset_keys = ["truck_custom","truck_medium","truck_semi","truck_20ft","truck_40ft","truck_van"]
    preset_cm   = {
        "truck_custom": None,
        "truck_medium": (700,240,250),
        "truck_semi":   (1200,240,260),
        "truck_20ft":   (590,235,239),
        "truck_40ft":   (1200,235,239),
        "truck_van":    (300,180,190),
    }
    preset_labels = [t(k) for k in preset_keys]

    # Saved trucks from DB
    saved_trucks = db.get_trucks() if hasattr(db,"get_trucks") else []

    # Truck selector
    sel_col1, sel_col2 = st.columns([2,1])
    with sel_col1:
        ps = st.selectbox(t("truck_template"), preset_labels, key="preset_sel")
        chosen_key = preset_keys[preset_labels.index(ps)]
        pv_cm = preset_cm[chosen_key]

    with sel_col2:
        if saved_trucks:
            saved_opts = [t("lbl_saved_trucks")] + [f"🚛 {tr['name']} ({_m2cm(tr['length'])}×{_m2cm(tr['width'])}×{_m2cm(tr['height'])} cm)"
                                                     for tr in saved_trucks]
            saved_sel = st.selectbox("", saved_opts, key="saved_truck_sel",
                                     label_visibility="collapsed")
            if saved_sel != t("lbl_saved_trucks"):
                idx = saved_opts.index(saved_sel)-1
                tr  = saved_trucks[idx]
                pv_cm = (_m2cm(tr["length"]), _m2cm(tr["width"]), _m2cm(tr["height"]))

    pv_cm = pv_cm or (700,240,250)

    tc1,tc2,tc3 = st.columns(3)
    with tc1: t_l_cm = st.number_input(t("truck_length_cm"),min_value=1,value=int(pv_cm[0]),step=1)
    with tc2: t_w_cm = st.number_input(t("truck_width_cm"), min_value=1,value=int(pv_cm[1]),step=1)
    with tc3: t_h_cm = st.number_input(t("truck_height_cm"),min_value=1,value=int(pv_cm[2]),step=1)

    truck_l = _cm2m(t_l_cm); truck_w = _cm2m(t_w_cm); truck_h = _cm2m(t_h_cm)
    vol_cm3 = t_l_cm*t_w_cm*t_h_cm
    st.info(t("truck_total_vol", v=vol_cm3, vm=truck_l*truck_w*truck_h))

    # Save truck button
    with st.expander(t("trucks_section"), expanded=False):
        if saved_trucks:
            for tr in saved_trucks:
                tc,td = st.columns([4,1])
                with tc:
                    st.markdown(f"**{tr['name']}** — {_m2cm(tr['length'])}×{_m2cm(tr['width'])}×{_m2cm(tr['height'])} cm")
                with td:
                    if st.button("🗑️",key=f"dtr{tr['id']}"):
                        db.delete_truck(tr["id"]); st.rerun()
        else:
            st.caption(t("no_saved_trucks"))

        st.markdown("---")
        stn1,stn2 = st.columns([3,1])
        with stn1: new_truck_name = st.text_input("",placeholder=t("truck_name_ph"),
                                                   label_visibility="collapsed",key="ntn")
        with stn2:
            if st.button(t("btn_save_truck"), use_container_width=True):
                if new_truck_name.strip() and hasattr(db,"add_truck"):
                    db.add_truck(new_truck_name.strip(), truck_l, truck_w, truck_h)
                    st.success(t("msg_truck_saved",name=new_truck_name.strip()))
                    st.rerun()

    # Loading options
    st.markdown(t("loading_opts_title"))
    lo1,lo2 = st.columns(2)
    with lo1:
        dir_opts = [t("dir_front_back"),t("dir_back_front")]
        dir_sel  = st.selectbox(t("field_loading_dir"),dir_opts,key="ldir")
        loading_dir = "back_front" if dir_sel==t("dir_back_front") else "front_back"
    with lo2:
        pref_cols = st.checkbox(t("chk_columns"),value=False,
                                help=t("chk_columns_help"),key="pcols")

    st.markdown("---")

    # Step 3
    st.subheader(t("step3_title"))
    cats_fp = [t("filter_all")]+_safe_cats()
    pcf = st.selectbox(t("filter_category"),cats_fp,key="pcf")
    pkgs_plan = db.get_packages(category_filter=pcf if pcf!=t("filter_all") else None)
    st.markdown(t("step3_subtitle"))

    qty_inp = {}
    pkg_cols = st.columns(min(len(pkgs_plan),3))
    for i,pkg in enumerate(pkgs_plan):
        col = pkg_cols[i%3]
        lc=_m2cm(pkg["length"]); wc=_m2cm(pkg["width"]); hc=_m2cm(pkg["height"])
        vol=lc*wc*hc
        with col:
            st.markdown(
                f'<div class="rule-box">'
                f'<strong style="border-left:3px solid {pkg["color"]};padding-left:6px;">{pkg["name"]}</strong><br>'
                +_badges(pkg)+
                f'<br><small>📐 {lc}×{wc}×{hc} cm | {vol:,} cm³'
                +(f' | ⚖️ {pkg["weight"]} kg' if pkg.get("weight") else "")
                +'</small></div>',
                unsafe_allow_html=True)
            qty = st.number_input("qty",min_value=0,max_value=500,step=1,value=0,
                                  key=f"q{pkg['id']}",label_visibility="collapsed")
            qty_inp[pkg["id"]] = qty

    selected = [
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
            "orient_rules": pkg.get("orient_rules") or {"A":"any","B":"any"},
            "load_priority":int(pkg.get("load_priority",5)),
            "category":     pkg.get("category",""),
            "quantity":     qty_inp.get(pkg["id"],0),
        }
        for pkg in pkgs_plan if qty_inp.get(pkg["id"],0)>0
    ]

    if selected:
        st.markdown("---")
        mc1,mc2,mc3 = st.columns(3)
        tb  = sum(i["quantity"] for i in selected)
        tvb = sum(i["length"]*i["width"]*i["height"]*i["quantity"] for i in selected)
        mc1.metric(t("metric_total_boxes"), tb)
        mc2.metric(t("metric_total_vol"),   f"{tvb*1e6:,.0f} cm³")
        mc3.metric(t("metric_max_eff"),     f"{min(100,tvb/(truck_l*truck_w*truck_h)*100):.1f}%")

    st.markdown("---")

    if st.button(t("btn_generate"),type="primary",
                 use_container_width=True,disabled=len(selected)==0):
        if not plan_name.strip():
            st.error(t("err_no_plan_name"))
        else:
            with st.spinner(t("spinner_packing")):
                packed,unpacked,efficiency = _run_pack(
                    truck_l,truck_w,truck_h,selected,loading_dir,pref_cols)
            db.save_plan(
                name=plan_name.strip(),
                truck_l=truck_l,truck_w=truck_w,truck_h=truck_h,
                items=selected,
                packed_boxes=packed,unpacked_boxes=unpacked,
                notes=plan_notes,
            )
            st.session_state.update({
                "lp":packed,"lu":unpacked,"le":efficiency,
                "lt":(truck_l,truck_w,truck_h),"ln":plan_name.strip()
            })
            st.rerun()

    if st.session_state.get("lp") is not None:
        packed=st.session_state["lp"]; unpacked=st.session_state["lu"]
        eff=st.session_state["le"]; tl,tw,th=st.session_state["lt"]

        st.success(t("success_plan_saved",name=st.session_state["ln"]))
        r1,r2,r3,r4 = st.columns(4)
        r1.metric(t("metric_loaded"),   len(packed))
        r2.metric(t("metric_unloaded"), len(unpacked))
        r3.metric(t("metric_efficiency"),f"{eff:.1f}%")
        uv = sum(b["placed_l"]*b["placed_w"]*b["placed_h"] for b in packed)
        r4.metric(t("metric_vol_used"), f"{uv*1e6:,.0f} cm³")
        _eff_bar(eff)

        st.plotly_chart(_viz_fig(tl,tw,th,packed,unpacked,eff,t),use_container_width=True)
        if packed:
            st.subheader(t("top_view_title"))
            st.plotly_chart(_viz_2d(tl,tw,th,packed,t),use_container_width=True)

        if unpacked:
            st.warning(t("warn_unpacked",n=len(unpacked))+"\n\n"
                       +"\n".join(f"- {b['name']} ({_m2cm(b['length'])}×{_m2cm(b['width'])}×{_m2cm(b['height'])} cm)"
                                  for b in unpacked))

        with st.expander(t("detail_expander")):
            rows=[{
                t("col_package"):b["name"],
                t("col_pos_cm"):f"({round(b['x']*100)},{round(b['y']*100)},{round(b['z']*100)})",
                t("col_dims_cm"):f"{round(b['placed_l']*100)}×{round(b['placed_w']*100)}×{round(b['placed_h']*100)}",
                t("col_stackable"):"✅" if b.get("stackable",True) else "⛔",
                t("col_rotated"):"🔄" if abs(b["placed_l"]-b["length"])>1e-3 else "—",
                t("col_priority"):b.get("load_priority",5),
            } for b in packed]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 – HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == t("nav_history"):
    st.title(t("pg3_title"))
    plans = db.get_plans()
    if not plans: st.info(t("pg3_no_plans")); st.stop()

    _ss("vp",None)

    for plan in plans:
        eff=plan["efficiency"]
        bc="#2A9D8F" if eff>=70 else ("#E9C46A" if eff>=40 else "#E63946")
        with st.container():
            h1,h2,h3 = st.columns([.50,.35,.15])
            with h1:
                st.markdown(
                    f'<span style="background:{bc};color:white;padding:2px 9px;'
                    f'border-radius:12px;font-size:.75rem;">{eff:.0f}%</span> &nbsp;'
                    f'<strong style="font-size:1.05rem;">{plan["name"]}</strong><br>'
                    f'<small style="color:#888;">📅 {plan["created_at"]}</small>',
                    unsafe_allow_html=True)
            with h2:
                unl = t("lbl_unloaded_n",n=plan["unpacked_count"]) if plan["unpacked_count"] else ""
                lc=round(plan["truck_length"]*100); wc=round(plan["truck_width"]*100); hc=round(plan["truck_height"]*100)
                st.markdown(
                    t("lbl_loaded_n",n=plan["packed_count"])+unl+
                    f'<br><small>'+t("lbl_truck_dims",l=lc,w=wc,h=hc)+"</small>",
                    unsafe_allow_html=True)
            with h3:
                bc1,bc2=st.columns(2)
                with bc1:
                    if st.button("👁️",key=f"vp{plan['id']}",help=t("btn_view")):
                        st.session_state["vp"]=(None if st.session_state.get("vp")==plan["id"] else plan["id"])
                        st.rerun()
                with bc2:
                    if st.button("🗑️",key=f"dp{plan['id']}",help=t("btn_delete")):
                        db.delete_plan(plan["id"])
                        if st.session_state.get("vp")==plan["id"]: st.session_state["vp"]=None
                        st.rerun()

            if st.session_state.get("vp")==plan["id"]:
                full=db.get_plan(plan["id"])
                packed=full["packed_boxes"]; unpacked=full["unpacked_boxes"]
                st.markdown("---")
                hi1,hi2,hi3,hi4=st.columns(4)
                hi1.metric(t("metric_efficiency"),f"{full['efficiency']:.1f}%")
                hi2.metric(t("metric_loaded"),    full["packed_count"])
                hi3.metric(t("metric_unloaded"),  full["unpacked_count"])
                hi4.metric(t("metric_vol_used2"), f"{full['used_volume']*1e6:,.0f} cm³")
                _eff_bar(full["efficiency"])
                if full.get("notes"): st.info(f"📝 {full['notes']}")

                if packed:
                    st.plotly_chart(
                        _viz_fig(full["truck_length"],full["truck_width"],full["truck_height"],
                                 packed,unpacked,full["efficiency"],t),
                        use_container_width=True)
                    st.subheader(t("top_view_title"))
                    st.plotly_chart(
                        _viz_2d(full["truck_length"],full["truck_width"],full["truck_height"],packed,t),
                        use_container_width=True)
                    with st.expander(t("detail_expander")):
                        rows=[{
                            t("col_package"):b["name"],
                            t("col_pos_cm"):f"({round(b['x']*100)},{round(b['y']*100)},{round(b['z']*100)})",
                            t("col_dims_cm"):f"{round(b['placed_l']*100)}×{round(b['placed_w']*100)}×{round(b['placed_h']*100)}",
                            t("col_stackable"):"✅" if b.get("stackable",True) else "⛔",
                            t("col_rotated"):"🔄" if abs(b["placed_l"]-b["length"])>1e-3 else "—",
                        } for b in packed]
                        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

                if unpacked:
                    st.warning(", ".join(b["name"] for b in unpacked)+t("lbl_unpacked_list"))

                with st.expander(t("summary_expander")):
                    rows2=[{
                        t("col_package"):it["name"],
                        t("col_category"):it.get("category",""),
                        t("col_qty"):it["quantity"],
                        t("col_dims_cm"):f"{_m2cm(it['length'])}×{_m2cm(it['width'])}×{_m2cm(it['height'])}",
                        t("col_stackable"):"✅" if it.get("stackable",True) else "⛔",
                        t("col_rotatable"):"🔄" if it.get("rotatable",True) else "📌",
                    } for it in full.get("items",[])]
                    st.dataframe(pd.DataFrame(rows2),use_container_width=True,hide_index=True)
                st.markdown("---")
        st.markdown("")
