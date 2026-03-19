"""
translations.py – all UI strings for ES / IT / EN.
Access via:  t = get_t(lang)  then  t("key")
"""

_T = {
    # ── Sidebar / nav ─────────────────────────────────────────────────────────
    "app_title":           {"es":"Carga de Camiones",         "it":"Carico Camion",            "en":"Truck Loader"},
    "nav_packages":        {"es":"📦 Gestión de Bultos",      "it":"📦 Gestione Colli",        "en":"📦 Package Management"},
    "nav_new_plan":        {"es":"🗂️ Nuevo Plan de Carga",    "it":"🗂️ Nuovo Piano di Carico", "en":"🗂️ New Loading Plan"},
    "nav_history":         {"es":"📋 Historial de Planes",    "it":"📋 Storico Piani",         "en":"📋 Plan History"},
    "sidebar_packages":    {"es":"Bultos registrados",        "it":"Colli registrati",         "en":"Registered packages"},
    "sidebar_plans":       {"es":"Planes guardados",          "it":"Piani salvati",            "en":"Saved plans"},
    "sidebar_categories":  {"es":"**Categorías**",            "it":"**Categorie**",            "en":"**Categories**"},
    "lang_label":          {"es":"Idioma / Language",         "it":"Lingua / Language",        "en":"Language / Idioma"},

    # ── Page 1 ────────────────────────────────────────────────────────────────
    "pg1_title":           {"es":"📦 Gestión de Bultos",      "it":"📦 Gestione Colli",        "en":"📦 Package Management"},
    "pg1_subtitle":        {"es":"Registrá todos los tipos de bultos con sus medidas, categoría, etiquetas y reglas de carga.",
                            "it":"Registra tutti i tipi di collo con misure, categoria, etichette e regole di carico.",
                            "en":"Register all package types with dimensions, category, tags and loading rules."},
    "add_package_expander":{"es":"➕ Agregar nuevo bulto",    "it":"➕ Aggiungi nuovo collo",  "en":"➕ Add new package"},
    "field_name":          {"es":"Nombre del bulto *",        "it":"Nome del collo *",         "en":"Package name *"},
    "field_name_ph":       {"es":"Ej: Caja grande",           "it":"Es: Scatola grande",       "en":"E.g.: Large box"},
    "field_desc":          {"es":"Descripción",               "it":"Descrizione",              "en":"Description"},
    "field_desc_ph":       {"es":"Opcional",                  "it":"Opzionale",                "en":"Optional"},
    "field_cat_existing":  {"es":"Categoría existente",       "it":"Categoria esistente",      "en":"Existing category"},
    "field_cat_none":      {"es":"— sin categoría —",         "it":"— senza categoria —",      "en":"— no category —"},
    "field_cat_new":       {"es":"…o nueva categoría",        "it":"…o nuova categoria",       "en":"…or new category"},
    "field_cat_new_ph":    {"es":"Ej: Electrónica",           "it":"Es: Elettronica",          "en":"E.g.: Electronics"},
    "field_tags":          {"es":"Etiquetas (coma)",          "it":"Etichette (virgola)",      "en":"Tags (comma)"},
    "field_tags_ph":       {"es":"frágil, urgente",           "it":"fragile, urgente",         "en":"fragile, urgent"},
    "dims_title":          {"es":"**Dimensiones (metros)** — la altura siempre queda vertical",
                            "it":"**Dimensioni (metri)** — l'altezza rimane sempre verticale",
                            "en":"**Dimensions (meters)** — height always stays vertical"},
    "field_length":        {"es":"Largo",    "it":"Lunghezza", "en":"Length"},
    "field_width":         {"es":"Ancho",    "it":"Larghezza", "en":"Width"},
    "field_height":        {"es":"Alto",     "it":"Altezza",   "en":"Height"},
    "field_weight":        {"es":"Peso (kg)","it":"Peso (kg)", "en":"Weight (kg)"},

    # Behaviour section
    "behaviour_title":     {"es":"**Comportamiento y reglas de carga**",
                            "it":"**Comportamento e regole di carico**",
                            "en":"**Behaviour and loading rules**"},
    "chk_stackable":       {"es":"⬆ Se puede apilar encima",  "it":"⬆ Si può impilare sopra", "en":"⬆ Can stack on top"},
    "chk_stackable_help":  {"es":"Otros bultos pueden apoyarse encima de éste.",
                            "it":"Altri colli possono essere posizionati sopra.",
                            "en":"Other packages can be placed on top of this one."},
    "chk_rotatable":       {"es":"🔄 Se puede girar 90°",     "it":"🔄 Ruotabile di 90°",      "en":"🔄 Can rotate 90°"},
    "chk_rotatable_help":  {"es":"El algoritmo puede rotar el bulto en el plano horizontal.",
                            "it":"L'algoritmo può ruotare il collo nel piano orizzontale.",
                            "en":"The algorithm can rotate the package horizontally."},

    # Position rule
    "field_pos_rule":      {"es":"📍 Posición vertical permitida",
                            "it":"📍 Posizione verticale consentita",
                            "en":"📍 Allowed vertical position"},
    "pos_any":             {"es":"🔀 Cualquier posición",     "it":"🔀 Qualsiasi posizione",   "en":"🔀 Any position"},
    "pos_floor":           {"es":"🏗️ Solo en el piso",        "it":"🏗️ Solo a pavimento",     "en":"🏗️ Floor only"},
    "pos_top":             {"es":"⬆ Solo encima de otros",    "it":"⬆ Solo sopra altri",       "en":"⬆ On top of others only"},
    "pos_no_floor":        {"es":"🚫 No en el piso (encima)", "it":"🚫 Non a pavimento",       "en":"🚫 Not on floor (on top)"},
    "pos_rule_help":       {"es":"Solo piso: ideal para items pesados o altos. Solo encima: para items livianos. No piso: igual que 'solo encima'.",
                            "it":"Solo pavimento: ideale per articoli pesanti o alti. Solo sopra: per articoli leggeri. Non a pavimento: uguale a 'solo sopra'.",
                            "en":"Floor only: ideal for heavy/tall items. On top only: for light items. Not on floor: same as on top."},

    # Load priority
    "field_priority":      {"es":"🚦 Prioridad de carga (1=última, 10=primera)",
                            "it":"🚦 Priorità di carico (1=ultima, 10=prima)",
                            "en":"🚦 Load priority (1=last, 10=first)"},
    "field_priority_help": {"es":"Los bultos con mayor prioridad se cargan primero y quedan más cerca de la puerta del camión.",
                            "it":"I colli con priorità maggiore vengono caricati per primi e si trovano più vicino alla porta del camion.",
                            "en":"Higher priority packages are loaded first and placed closest to the truck door."},

    # Badges
    "badge_stackable":     {"es":"⬆ Apilable",       "it":"⬆ Impilabile",       "en":"⬆ Stackable"},
    "badge_no_stack":      {"es":"⛔ No apilable",    "it":"⛔ Non impilabile",   "en":"⛔ Not stackable"},
    "badge_rotatable":     {"es":"🔄 Girable",        "it":"🔄 Ruotabile",        "en":"🔄 Rotatable"},
    "badge_no_rotate":     {"es":"📌 No girable",     "it":"📌 Non ruotabile",    "en":"📌 Fixed orient."},
    "badge_pos_any":       {"es":"🔀 Libre",          "it":"🔀 Libero",           "en":"🔀 Any pos."},
    "badge_pos_floor":     {"es":"🏗️ Solo piso",      "it":"🏗️ Solo pavim.",     "en":"🏗️ Floor only"},
    "badge_pos_top":       {"es":"⬆ Solo encima",     "it":"⬆ Solo sopra",       "en":"⬆ Top only"},
    "badge_pos_no_floor":  {"es":"🚫 No piso",        "it":"🚫 Non a pav.",       "en":"🚫 Not floor"},
    "badge_prio":          {"es":"P{p}",              "it":"P{p}",               "en":"P{p}"},

    # Buttons / common
    "btn_save_package":    {"es":"💾 Guardar bulto",  "it":"💾 Salva collo",      "en":"💾 Save package"},
    "btn_save":            {"es":"💾 Guardar",        "it":"💾 Salva",            "en":"💾 Save"},
    "btn_cancel":          {"es":"✖ Cancelar",        "it":"✖ Annulla",           "en":"✖ Cancel"},
    "btn_edit":            {"es":"Editar",            "it":"Modifica",            "en":"Edit"},
    "btn_delete":          {"es":"Eliminar",          "it":"Elimina",             "en":"Delete"},
    "btn_view":            {"es":"Ver",               "it":"Vedi",               "en":"View"},
    "msg_name_required":   {"es":"El nombre es obligatorio.", "it":"Il nome è obbligatorio.", "en":"Name is required."},
    "msg_pkg_added":       {"es":"✅ **{name}** agregado.",   "it":"✅ **{name}** aggiunto.",  "en":"✅ **{name}** added."},

    # Filters
    "filter_category":     {"es":"Filtrar por categoría",   "it":"Filtra per categoria",    "en":"Filter by category"},
    "filter_all":          {"es":"Todas",                   "it":"Tutte",                   "en":"All"},
    "filter_search":       {"es":"🔍 Buscar por nombre",     "it":"🔍 Cerca per nome",       "en":"🔍 Search by name"},
    "filter_search_ph":    {"es":"Escribí para filtrar…",   "it":"Scrivi per filtrare…",    "en":"Type to filter…"},
    "pkg_list_title":      {"es":"Bultos registrados ({n})","it":"Colli registrati ({n})",  "en":"Registered packages ({n})"},
    "no_packages":         {"es":"No hay bultos que coincidan con el filtro.",
                            "it":"Nessun collo corrisponde al filtro.",
                            "en":"No packages match the filter."},

    # Edit form
    "edit_title":          {"es":"**Editando:** {name}","it":"**Modifica:** {name}","en":"**Editing:** {name}"},
    "field_cat_none_short":{"es":"— sin —",           "it":"— nessuna —",        "en":"— none —"},
    "field_cat_new_edit":  {"es":"Nueva categoría",   "it":"Nuova categoria",    "en":"New category"},

    # ── Page 2 ────────────────────────────────────────────────────────────────
    "pg2_title":           {"es":"🗂️ Nuevo Plan de Carga",   "it":"🗂️ Nuovo Piano di Carico","en":"🗂️ New Loading Plan"},
    "pg2_no_packages":     {"es":"⚠️ No hay bultos registrados. Andá a **Gestión de Bultos** primero.",
                            "it":"⚠️ Nessun collo registrato. Vai a **Gestione Colli** prima.",
                            "en":"⚠️ No packages registered. Go to **Package Management** first."},
    "step1_title":         {"es":"1️⃣ Información del plan", "it":"1️⃣ Informazioni piano",   "en":"1️⃣ Plan information"},
    "field_plan_name":     {"es":"Nombre del plan *",        "it":"Nome del piano *",        "en":"Plan name *"},
    "field_plan_name_ph":  {"es":"Ej: Envío CABA – Semana 23","it":"Es: Spedizione Milano – Sett. 23","en":"E.g.: Shipment NYC – Week 23"},
    "field_auto_date":     {"es":"📅 Fecha automática: {dt}","it":"📅 Data automatica: {dt}","en":"📅 Auto date: {dt}"},
    "field_notes":         {"es":"Notas",                   "it":"Note",                    "en":"Notes"},
    "field_notes_ph":      {"es":"Destino, transportista…", "it":"Destinazione, trasportatore…","en":"Destination, carrier…"},

    "step2_title":         {"es":"2️⃣ Camión y opciones de carga",
                            "it":"2️⃣ Camion e opzioni di carico",
                            "en":"2️⃣ Truck & loading options"},
    "truck_template":      {"es":"Plantilla",   "it":"Modello",   "en":"Template"},
    "truck_custom":        {"es":"Personalizado","it":"Personalizzato","en":"Custom"},
    "truck_medium":        {"es":"Camión mediano (7×2.4×2.5 m)","it":"Camion medio (7×2.4×2.5 m)","en":"Medium truck (7×2.4×2.5 m)"},
    "truck_semi":          {"es":"Semi-trailer (12×2.4×2.6 m)","it":"Semirimorchio (12×2.4×2.6 m)","en":"Semi-trailer (12×2.4×2.6 m)"},
    "truck_20ft":          {"es":"Contenedor 20' (5.9×2.35×2.39 m)","it":"Container 20' (5.9×2.35×2.39 m)","en":"20' Container (5.9×2.35×2.39 m)"},
    "truck_40ft":          {"es":"Contenedor 40' (12×2.35×2.39 m)","it":"Container 40' (12×2.35×2.39 m)","en":"40' Container (12×2.35×2.39 m)"},
    "truck_van":           {"es":"Furgón pequeño (3×1.8×1.9 m)","it":"Furgone piccolo (3×1.8×1.9 m)","en":"Small van (3×1.8×1.9 m)"},
    "truck_length_m":      {"es":"Largo (m)",  "it":"Lunghezza (m)","en":"Length (m)"},
    "truck_width_m":       {"es":"Ancho (m)",  "it":"Larghezza (m)","en":"Width (m)"},
    "truck_height_m":      {"es":"Alto (m)",   "it":"Altezza (m)",  "en":"Height (m)"},
    "truck_total_vol":     {"es":"📦 Volumen total: **{v:.2f} m³**","it":"📦 Volume totale: **{v:.2f} m³**","en":"📦 Total volume: **{v:.2f} m³**"},

    # Loading options (plan-level)
    "loading_opts_title":  {"es":"⚙️ **Opciones de carga del plan**",
                            "it":"⚙️ **Opzioni di carico del piano**",
                            "en":"⚙️ **Plan loading options**"},
    "field_loading_dir":   {"es":"↔ Dirección de carga",    "it":"↔ Direzione di carico",   "en":"↔ Loading direction"},
    "dir_front_back":      {"es":"⬅ Frente → Fondo (rellena desde la cabina)",
                            "it":"⬅ Fronte → Fondo (riempie dal lato cabina)",
                            "en":"⬅ Front → Back (fills from cab side)"},
    "dir_back_front":      {"es":"➡ Fondo → Frente (alta prioridad cerca de la puerta)",
                            "it":"➡ Fondo → Fronte (alta priorità vicino alla porta)",
                            "en":"➡ Back → Front (high priority near door)"},
    "chk_columns":         {"es":"🗼 Preferir orden columnar (mismo tipo apilado)",
                            "it":"🗼 Preferire ordine colonnare (stesso tipo impilato)",
                            "en":"🗼 Prefer columnar order (same type stacked)"},
    "chk_columns_help":    {"es":"Intenta apilar bultos del mismo tipo en columnas verticales.",
                            "it":"Cerca di impilare colli dello stesso tipo in colonne verticali.",
                            "en":"Tries to stack packages of the same type in vertical columns."},

    "step3_title":         {"es":"3️⃣ Selección de bultos",  "it":"3️⃣ Selezione colli",      "en":"3️⃣ Package selection"},
    "step3_subtitle":      {"es":"Indicá cuántas unidades de cada bulto querés cargar.",
                            "it":"Indica quante unità di ogni collo vuoi caricare.",
                            "en":"Indicate how many units of each package to load."},
    "metric_total_boxes":  {"es":"Total de bultos",         "it":"Totale colli",            "en":"Total packages"},
    "metric_total_vol":    {"es":"Volumen de bultos",       "it":"Volume colli",            "en":"Package volume"},
    "metric_max_eff":      {"es":"Eficiencia máx. posible", "it":"Efficienza max possibile","en":"Max possible efficiency"},
    "warn_no_stack":       {"es":"⛔ **No apilables**: {names}","it":"⛔ **Non impilabili**: {names}","en":"⛔ **Not stackable**: {names}"},
    "warn_no_rotate":      {"es":"📌 **No girables**: {names}","it":"📌 **Non ruotabili**: {names}","en":"📌 **Fixed orientation**: {names}"},
    "warn_floor_only":     {"es":"🏗️ **Solo piso**: {names}","it":"🏗️ **Solo pavimento**: {names}","en":"🏗️ **Floor only**: {names}"},
    "warn_top_only":       {"es":"⬆ **Solo encima**: {names}","it":"⬆ **Solo sopra**: {names}","en":"⬆ **On top only**: {names}"},

    "btn_generate":        {"es":"🚀 Generar Plan de Carga","it":"🚀 Genera Piano di Carico","en":"🚀 Generate Loading Plan"},
    "spinner_packing":     {"es":"⚙️ Calculando distribución óptima…","it":"⚙️ Calcolo distribuzione ottimale…","en":"⚙️ Calculating optimal distribution…"},
    "err_no_plan_name":    {"es":"⚠️ Poné un nombre al plan.","it":"⚠️ Inserisci un nome.","en":"⚠️ Please enter a plan name."},
    "success_plan_saved":  {"es":"✅ Plan guardado: **{name}**","it":"✅ Piano salvato: **{name}**","en":"✅ Plan saved: **{name}**"},

    # Results
    "metric_loaded":       {"es":"Bultos cargados","it":"Colli caricati",    "en":"Loaded packages"},
    "metric_unloaded":     {"es":"Sin cargar",     "it":"Non caricati",      "en":"Not loaded"},
    "metric_efficiency":   {"es":"Eficiencia",     "it":"Efficienza",        "en":"Efficiency"},
    "metric_vol_used":     {"es":"Vol. utilizado", "it":"Vol. utilizzato",   "en":"Used volume"},
    "metric_vol_used2":    {"es":"Vol. utilizado", "it":"Vol. utilizzato",   "en":"Used volume"},
    "eff_caption":         {"es":"Eficiencia de llenado: {e:.1f}%","it":"Efficienza di riempimento: {e:.1f}%","en":"Fill efficiency: {e:.1f}%"},
    "top_view_title":      {"es":"🗺️ Vista superior","it":"🗺️ Vista dall'alto","en":"🗺️ Top view"},
    "warn_unpacked":       {"es":"⚠️ **{n} bulto(s) no cargados** (no entran):","it":"⚠️ **{n} collo/i non caricato/i** (non entrano):","en":"⚠️ **{n} package(s) not loaded** (don't fit):"},
    "detail_expander":     {"es":"📋 Detalle de posicionamiento","it":"📋 Dettaglio posizionamento","en":"📋 Placement detail"},
    "col_package":         {"es":"Bulto",     "it":"Collo",     "en":"Package"},
    "col_x":               {"es":"X (m)",     "it":"X (m)",     "en":"X (m)"},
    "col_y":               {"es":"Y (m)",     "it":"Y (m)",     "en":"Y (m)"},
    "col_z":               {"es":"Z (m)",     "it":"Z (m)",     "en":"Z (m)"},
    "col_dims":            {"es":"L×A×H (m)", "it":"L×L×A (m)","en":"L×W×H (m)"},
    "col_vol":             {"es":"Vol (m³)",  "it":"Vol (m³)",  "en":"Vol (m³)"},
    "col_stackable":       {"es":"Apilable",  "it":"Impilabile","en":"Stackable"},
    "col_rotated":         {"es":"Girado",    "it":"Ruotato",   "en":"Rotated"},
    "col_priority":        {"es":"Prioridad", "it":"Priorità",  "en":"Priority"},
    "col_position":        {"es":"Pos",       "it":"Pos",       "en":"Pos"},
    "col_category":        {"es":"Categoría", "it":"Categoria", "en":"Category"},
    "col_qty":             {"es":"Cant.",     "it":"Qtà",       "en":"Qty"},
    "col_rotatable":       {"es":"Girable",   "it":"Ruotabile", "en":"Rotatable"},
    "col_pos_rule":        {"es":"Pos. regla","it":"Regola pos.","en":"Pos. rule"},

    # ── Page 3 ────────────────────────────────────────────────────────────────
    "pg3_title":           {"es":"📋 Historial de Planes de Carga","it":"📋 Storico Piani di Carico","en":"📋 Loading Plan History"},
    "pg3_no_plans":        {"es":"Aún no hay planes guardados.","it":"Nessun piano salvato ancora.","en":"No plans saved yet."},
    "lbl_loaded_n":        {"es":"📦 **{n}** cargados",    "it":"📦 **{n}** caricati",    "en":"📦 **{n}** loaded"},
    "lbl_unloaded_n":      {"es":" | ⚠️ {n} sin cargar",  "it":" | ⚠️ {n} non caricati","en":" | ⚠️ {n} not loaded"},
    "lbl_truck_dims":      {"es":"🚛 {l}×{w}×{h} m",     "it":"🚛 {l}×{w}×{h} m",     "en":"🚛 {l}×{w}×{h} m"},
    "lbl_unpacked_list":   {"es":" — no entraron.",       "it":" — non entravano.",     "en":" — didn't fit."},
    "summary_expander":    {"es":"📦 Resumen de bultos",  "it":"📦 Riepilogo colli",    "en":"📦 Package summary"},

    # ── Plot labels ───────────────────────────────────────────────────────────
    "plot_title":          {"es":"Plan de carga",   "it":"Piano di carico", "en":"Loading plan"},
    "plot_legend":         {"es":"Tipo de bulto",   "it":"Tipo di collo",   "en":"Package type"},
    "plot_x":              {"es":"Largo (m)",        "it":"Lunghezza (m)",   "en":"Length (m)"},
    "plot_y":              {"es":"Ancho (m)",         "it":"Larghezza (m)",   "en":"Width (m)"},
    "plot_z":              {"es":"Alto (m)",          "it":"Altezza (m)",     "en":"Height (m)"},
    "plot_truck":          {"es":"Camión",            "it":"Camion",          "en":"Truck"},
    "plot_2d_title":       {"es":"Vista superior (piso por piso)","it":"Vista dall'alto (piano per piano)","en":"Top view (floor by floor)"},
    "plot_eff_label":      {"es":"Eficiencia: ",      "it":"Efficienza: ",    "en":"Efficiency: "},
    "plot_loaded_label":   {"es":"Bultos cargados: ", "it":"Colli caricati: ","en":"Loaded packages: "},
    "plot_unloaded_label": {"es":"⚠️ Sin cargar: ",   "it":"⚠️ Non caricati: ","en":"⚠️ Not loaded: "},
}


def get_t(lang: str):
    lang = lang if lang in ("es","it","en") else "es"
    def t(key: str, **kw) -> str:
        entry = _T.get(key, {})
        text  = entry.get(lang, entry.get("es", f"[{key}]"))
        return text.format(**kw) if kw else text
    return t
