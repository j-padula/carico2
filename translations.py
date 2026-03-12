"""
translations.py – all UI strings for ES / IT / EN.
Access via:  t = get_t(lang)  then  t("key")
"""

_TRANSLATIONS = {

    # ── Sidebar / navigation ─────────────────────────────────────────────────
    "app_title":            {"es": "Carga de Camiones",        "it": "Carico Camion",           "en": "Truck Loader"},
    "nav_packages":         {"es": "📦 Gestión de Bultos",     "it": "📦 Gestione Colli",       "en": "📦 Package Management"},
    "nav_new_plan":         {"es": "🗂️ Nuevo Plan de Carga",   "it": "🗂️ Nuovo Piano di Carico","en": "🗂️ New Loading Plan"},
    "nav_history":          {"es": "📋 Historial de Planes",   "it": "📋 Storico Piani",        "en": "📋 Plan History"},
    "sidebar_packages":     {"es": "Bultos registrados",       "it": "Colli registrati",        "en": "Registered packages"},
    "sidebar_plans":        {"es": "Planes guardados",         "it": "Piani salvati",           "en": "Saved plans"},
    "sidebar_categories":   {"es": "**Categorías**",           "it": "**Categorie**",           "en": "**Categories**"},

    # ── Page 1 – Package management ──────────────────────────────────────────
    "pg1_title":            {"es": "📦 Gestión de Bultos",     "it": "📦 Gestione Colli",       "en": "📦 Package Management"},
    "pg1_subtitle":         {"es": "Registrá todos los tipos de bultos con sus medidas, categoría, etiquetas y apilabilidad.",
                             "it": "Registra tutti i tipi di collo con misure, categoria, etichette e impilabilità.",
                             "en": "Register all package types with dimensions, category, tags and stacking rules."},

    # Add form
    "add_package_expander": {"es": "➕ Agregar nuevo bulto",   "it": "➕ Aggiungi nuovo collo", "en": "➕ Add new package"},
    "field_name":           {"es": "Nombre del bulto *",       "it": "Nome del collo *",        "en": "Package name *"},
    "field_name_ph":        {"es": "Ej: Caja grande",          "it": "Es: Scatola grande",      "en": "E.g.: Large box"},
    "field_desc":           {"es": "Descripción",              "it": "Descrizione",             "en": "Description"},
    "field_desc_ph":        {"es": "Opcional",                 "it": "Opzionale",               "en": "Optional"},
    "field_cat_existing":   {"es": "Categoría existente",      "it": "Categoria esistente",     "en": "Existing category"},
    "field_cat_none":       {"es": "— sin categoría —",        "it": "— senza categoria —",     "en": "— no category —"},
    "field_cat_new":        {"es": "…o nueva categoría",       "it": "…o nuova categoria",      "en": "…or new category"},
    "field_cat_new_ph":     {"es": "Ej: Electrónica",          "it": "Es: Elettronica",         "en": "E.g.: Electronics"},
    "field_tags":           {"es": "Etiquetas (coma)",         "it": "Etichette (virgola)",     "en": "Tags (comma)"},
    "field_tags_ph":        {"es": "frágil, urgente",          "it": "fragile, urgente",        "en": "fragile, urgent"},
    "dims_title":           {"es": "**Dimensiones (metros)** — la altura siempre queda vertical",
                             "it": "**Dimensioni (metri)** — l'altezza rimane sempre verticale",
                             "en": "**Dimensions (meters)** — height always stays vertical"},
    "field_length":         {"es": "Largo",                    "it": "Lunghezza",               "en": "Length"},
    "field_width":          {"es": "Ancho",                    "it": "Larghezza",               "en": "Width"},
    "field_height":         {"es": "Alto",                     "it": "Altezza",                 "en": "Height"},
    "field_weight":         {"es": "Peso (kg)",                "it": "Peso (kg)",               "en": "Weight (kg)"},
    "behaviour_title":      {"es": "**Comportamiento**",       "it": "**Comportamento**",       "en": "**Behaviour**"},
    "chk_stackable":        {"es": "⬆ Se puede apilar encima", "it": "⬆ Si può impilare sopra", "en": "⬆ Can stack on top"},
    "chk_stackable_help":   {"es": "Si está marcado, otros bultos pueden ir encima de éste.",
                             "it": "Se selezionato, altri colli possono essere posizionati sopra.",
                             "en": "If checked, other packages can be placed on top of this one."},
    "chk_rotatable":        {"es": "🔄 Se puede girar 90°",    "it": "🔄 Ruotabile di 90°",     "en": "🔄 Can rotate 90°"},
    "chk_rotatable_help":   {"es": "Si está marcado, el algoritmo puede rotar el bulto en el plano horizontal.",
                             "it": "Se selezionato, l'algoritmo può ruotare il collo nel piano orizzontale.",
                             "en": "If checked, the algorithm can rotate the package horizontally."},
    "btn_save_package":     {"es": "💾 Guardar bulto",         "it": "💾 Salva collo",          "en": "💾 Save package"},
    "msg_name_required":    {"es": "El nombre es obligatorio.", "it": "Il nome è obbligatorio.", "en": "Name is required."},
    "msg_pkg_added":        {"es": "✅ **{name}** agregado.",   "it": "✅ **{name}** aggiunto.",  "en": "✅ **{name}** added."},

    # Package list
    "filter_category":      {"es": "Filtrar por categoría",    "it": "Filtra per categoria",    "en": "Filter by category"},
    "filter_all":           {"es": "Todas",                    "it": "Tutte",                   "en": "All"},
    "filter_search":        {"es": "🔍 Buscar por nombre",      "it": "🔍 Cerca per nome",       "en": "🔍 Search by name"},
    "filter_search_ph":     {"es": "Escribí para filtrar…",    "it": "Scrivi per filtrare…",    "en": "Type to filter…"},
    "pkg_list_title":       {"es": "Bultos registrados ({n})", "it": "Colli registrati ({n})",  "en": "Registered packages ({n})"},
    "no_packages":          {"es": "No hay bultos que coincidan con el filtro.",
                             "it": "Nessun collo corrisponde al filtro.",
                             "en": "No packages match the filter."},

    # Badges
    "badge_stackable":      {"es": "⬆ Apilable",              "it": "⬆ Impilabile",            "en": "⬆ Stackable"},
    "badge_no_stack":       {"es": "⛔ No apilable",           "it": "⛔ Non impilabile",        "en": "⛔ Not stackable"},
    "badge_rotatable":      {"es": "🔄 Girable",               "it": "🔄 Ruotabile",             "en": "🔄 Rotatable"},
    "badge_no_rotate":      {"es": "📌 No girable",            "it": "📌 Non ruotabile",         "en": "📌 Fixed orientation"},

    # Edit form
    "edit_title":           {"es": "**Editando:** {name}",     "it": "**Modifica:** {name}",    "en": "**Editing:** {name}"},
    "field_cat_none_short": {"es": "— sin —",                  "it": "— nessuna —",             "en": "— none —"},
    "field_cat_new_edit":   {"es": "Nueva categoría",          "it": "Nuova categoria",         "en": "New category"},
    "btn_save":             {"es": "💾 Guardar",               "it": "💾 Salva",                "en": "💾 Save"},
    "btn_cancel":           {"es": "✖ Cancelar",               "it": "✖ Annulla",               "en": "✖ Cancel"},
    "btn_edit":             {"es": "Editar",                   "it": "Modifica",                "en": "Edit"},
    "btn_delete":           {"es": "Eliminar",                 "it": "Elimina",                 "en": "Delete"},

    # ── Page 2 – New loading plan ─────────────────────────────────────────────
    "pg2_title":            {"es": "🗂️ Nuevo Plan de Carga",   "it": "🗂️ Nuovo Piano di Carico","en": "🗂️ New Loading Plan"},
    "pg2_no_packages":      {"es": "⚠️ No hay bultos registrados. Andá a **Gestión de Bultos** primero.",
                             "it": "⚠️ Nessun collo registrato. Vai a **Gestione Colli** prima.",
                             "en": "⚠️ No packages registered. Go to **Package Management** first."},

    "step1_title":          {"es": "1️⃣ Información del plan",  "it": "1️⃣ Informazioni piano",  "en": "1️⃣ Plan information"},
    "field_plan_name":      {"es": "Nombre del plan *",        "it": "Nome del piano *",        "en": "Plan name *"},
    "field_plan_name_ph":   {"es": "Ej: Envío CABA – Semana 23","it":"Es: Spedizione Milano – Sett. 23","en":"E.g.: Shipment NYC – Week 23"},
    "field_auto_date":      {"es": "📅 Fecha automática: {dt}","it": "📅 Data automatica: {dt}","en": "📅 Auto date: {dt}"},
    "field_notes":          {"es": "Notas",                    "it": "Note",                    "en": "Notes"},
    "field_notes_ph":       {"es": "Destino, transportista…",  "it": "Destinazione, trasportatore…","en": "Destination, carrier…"},

    "step2_title":          {"es": "2️⃣ Dimensiones del camión / contenedor",
                             "it": "2️⃣ Dimensioni del camion / container",
                             "en": "2️⃣ Truck / container dimensions"},
    "truck_template":       {"es": "Plantilla",                "it": "Modello",                 "en": "Template"},
    "truck_custom":         {"es": "Personalizado",            "it": "Personalizzato",          "en": "Custom"},
    "truck_medium":         {"es": "Camión mediano (7×2.4×2.5 m)","it":"Camion medio (7×2.4×2.5 m)","en":"Medium truck (7×2.4×2.5 m)"},
    "truck_semi":           {"es": "Semi-trailer (12×2.4×2.6 m)","it":"Semirimorchio (12×2.4×2.6 m)","en":"Semi-trailer (12×2.4×2.6 m)"},
    "truck_20ft":           {"es": "Contenedor 20' (5.9×2.35×2.39 m)","it":"Container 20' (5.9×2.35×2.39 m)","en":"20' Container (5.9×2.35×2.39 m)"},
    "truck_40ft":           {"es": "Contenedor 40' (12×2.35×2.39 m)","it":"Container 40' (12×2.35×2.39 m)","en":"40' Container (12×2.35×2.39 m)"},
    "truck_van":            {"es": "Furgón pequeño (3×1.8×1.9 m)","it":"Furgone piccolo (3×1.8×1.9 m)","en":"Small van (3×1.8×1.9 m)"},
    "truck_length_m":       {"es": "Largo (m)",                "it": "Lunghezza (m)",           "en": "Length (m)"},
    "truck_width_m":        {"es": "Ancho (m)",                "it": "Larghezza (m)",           "en": "Width (m)"},
    "truck_height_m":       {"es": "Alto (m)",                 "it": "Altezza (m)",             "en": "Height (m)"},
    "truck_total_vol":      {"es": "📦 Volumen total: **{v:.2f} m³**",
                             "it": "📦 Volume totale: **{v:.2f} m³**",
                             "en": "📦 Total volume: **{v:.2f} m³**"},

    "step3_title":          {"es": "3️⃣ Selección de bultos",   "it": "3️⃣ Selezione colli",     "en": "3️⃣ Package selection"},
    "step3_subtitle":       {"es": "Indicá cuántas unidades de cada bulto querés cargar.",
                             "it": "Indica quante unità di ogni collo vuoi caricare.",
                             "en": "Indicate how many units of each package to load."},
    "metric_total_boxes":   {"es": "Total de bultos",          "it": "Totale colli",            "en": "Total packages"},
    "metric_total_vol":     {"es": "Volumen de bultos",        "it": "Volume colli",            "en": "Package volume"},
    "metric_max_eff":       {"es": "Eficiencia máx. posible",  "it": "Efficienza max possibile","en": "Max possible efficiency"},
    "warn_no_stack":        {"es": "⛔ **No apilables** (nada encima): {names}",
                             "it": "⛔ **Non impilabili** (niente sopra): {names}",
                             "en": "⛔ **Not stackable** (nothing on top): {names}"},
    "warn_no_rotate":       {"es": "📌 **No girables** (orientación fija): {names}",
                             "it": "📌 **Non ruotabili** (orientazione fissa): {names}",
                             "en": "📌 **Fixed orientation** (no rotation): {names}"},

    "btn_generate":         {"es": "🚀 Generar Plan de Carga", "it": "🚀 Genera Piano di Carico","en": "🚀 Generate Loading Plan"},
    "spinner_packing":      {"es": "⚙️ Calculando distribución óptima…",
                             "it": "⚙️ Calcolo distribuzione ottimale…",
                             "en": "⚙️ Calculating optimal distribution…"},
    "err_no_plan_name":     {"es": "⚠️ Poné un nombre al plan.", "it": "⚠️ Inserisci un nome per il piano.","en": "⚠️ Please enter a plan name."},
    "success_plan_saved":   {"es": "✅ Plan guardado: **{name}**","it": "✅ Piano salvato: **{name}**","en": "✅ Plan saved: **{name}**"},

    # Results
    "metric_loaded":        {"es": "Bultos cargados",          "it": "Colli caricati",          "en": "Loaded packages"},
    "metric_unloaded":      {"es": "Sin cargar",               "it": "Non caricati",            "en": "Not loaded"},
    "metric_efficiency":    {"es": "Eficiencia",               "it": "Efficienza",              "en": "Efficiency"},
    "metric_vol_used":      {"es": "Vol. utilizado",           "it": "Vol. utilizzato",         "en": "Used volume"},
    "eff_caption":          {"es": "Eficiencia de llenado: {e:.1f}%",
                             "it": "Efficienza di riempimento: {e:.1f}%",
                             "en": "Fill efficiency: {e:.1f}%"},
    "top_view_title":       {"es": "🗺️ Vista superior",        "it": "🗺️ Vista dall'alto",      "en": "🗺️ Top view"},
    "warn_unpacked":        {"es": "⚠️ **{n} bulto(s) no cargados** (no entran):",
                             "it": "⚠️ **{n} collo/i non caricato/i** (non entrano):",
                             "en": "⚠️ **{n} package(s) not loaded** (don't fit):"},
    "detail_expander":      {"es": "📋 Detalle de posicionamiento","it":"📋 Dettaglio posizionamento","en":"📋 Placement detail"},
    "col_package":          {"es": "Bulto",                    "it": "Collo",                   "en": "Package"},
    "col_x":                {"es": "X (m)",                    "it": "X (m)",                   "en": "X (m)"},
    "col_y":                {"es": "Y (m)",                    "it": "Y (m)",                   "en": "Y (m)"},
    "col_z":                {"es": "Z (m)",                    "it": "Z (m)",                   "en": "Z (m)"},
    "col_dims":             {"es": "L×A×H (m)",                "it": "L×L×A (m)",               "en": "L×W×H (m)"},
    "col_vol":              {"es": "Vol (m³)",                 "it": "Vol (m³)",                "en": "Vol (m³)"},
    "col_stackable":        {"es": "Apilable",                 "it": "Impilabile",              "en": "Stackable"},
    "col_rotated":          {"es": "Girado",                   "it": "Ruotato",                 "en": "Rotated"},

    # ── Page 3 – History ──────────────────────────────────────────────────────
    "pg3_title":            {"es": "📋 Historial de Planes de Carga",
                             "it": "📋 Storico Piani di Carico",
                             "en": "📋 Loading Plan History"},
    "pg3_no_plans":         {"es": "Aún no hay planes guardados.",
                             "it": "Nessun piano salvato ancora.",
                             "en": "No plans saved yet."},
    "btn_view":             {"es": "Ver",                      "it": "Vedi",                    "en": "View"},
    "lbl_loaded_n":         {"es": "📦 **{n}** cargados",      "it": "📦 **{n}** caricati",     "en": "📦 **{n}** loaded"},
    "lbl_unloaded_n":       {"es": " | ⚠️ {n} sin cargar",     "it": " | ⚠️ {n} non caricati",  "en": " | ⚠️ {n} not loaded"},
    "lbl_truck_dims":       {"es": "🚛 {l}×{w}×{h} m",        "it": "🚛 {l}×{w}×{h} m",       "en": "🚛 {l}×{w}×{h} m"},
    "metric_vol_used2":     {"es": "Vol. utilizado",           "it": "Vol. utilizzato",         "en": "Used volume"},
    "lbl_unpacked_list":    {"es": " — no entraron.",          "it": " — non entravano.",       "en": " — didn't fit."},
    "summary_expander":     {"es": "📦 Resumen de bultos del plan","it":"📦 Riepilogo colli piano","en":"📦 Plan package summary"},
    "col_category":         {"es": "Categoría",                "it": "Categoria",               "en": "Category"},
    "col_qty":              {"es": "Cant.",                    "it": "Qtà",                     "en": "Qty"},
    "col_rotatable":        {"es": "Girable",                  "it": "Ruotabile",               "en": "Rotatable"},
    "col_position":         {"es": "Pos",                      "it": "Pos",                     "en": "Pos"},

    # ── Plot titles ───────────────────────────────────────────────────────────
    "plot_title":           {"es": "Plan de carga",            "it": "Piano di carico",         "en": "Loading plan"},
    "plot_legend":          {"es": "Tipo de bulto",            "it": "Tipo di collo",           "en": "Package type"},
    "plot_x":               {"es": "Largo (m)",                "it": "Lunghezza (m)",           "en": "Length (m)"},
    "plot_y":               {"es": "Ancho (m)",                "it": "Larghezza (m)",           "en": "Width (m)"},
    "plot_z":               {"es": "Alto (m)",                 "it": "Altezza (m)",             "en": "Height (m)"},
    "plot_truck":           {"es": "Camión",                   "it": "Camion",                  "en": "Truck"},
    "plot_2d_title":        {"es": "Vista superior (piso por piso)",
                             "it": "Vista dall'alto (piano per piano)",
                             "en": "Top view (floor by floor)"},
    "plot_eff_label":       {"es": "Eficiencia: ",             "it": "Efficienza: ",            "en": "Efficiency: "},
    "plot_loaded_label":    {"es": "Bultos cargados: ",        "it": "Colli caricati: ",        "en": "Loaded packages: "},
    "plot_unloaded_label":  {"es": "⚠️ Sin cargar: ",          "it": "⚠️ Non caricati: ",       "en": "⚠️ Not loaded: "},
    "lang_label":           {"es": "Idioma / Language",        "it": "Lingua / Language",       "en": "Language / Idioma"},
}


def get_t(lang: str):
    """Return a translator function for the given language code (es/it/en)."""
    lang = lang if lang in ("es", "it", "en") else "es"

    def t(key: str, **kwargs) -> str:
        entry = _TRANSLATIONS.get(key, {})
        text  = entry.get(lang, entry.get("es", f"[{key}]"))
        return text.format(**kwargs) if kwargs else text

    return t
