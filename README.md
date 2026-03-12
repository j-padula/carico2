# 🚛 Gestor de Carga de Camiones

Aplicación Streamlit para gestionar y optimizar la carga de camiones/contenedores usando un algoritmo de bin-packing 3D.

---

## 📁 Estructura del proyecto

```
truck_loader/
├── app.py            # Interfaz principal Streamlit
├── database.py       # Base de datos SQLite (bultos y planes)
├── packing.py        # Algoritmo 3D bin-packing (Extreme Point Method)
├── visualization.py  # Visualizaciones 3D y 2D con Plotly
├── requirements.txt  # Dependencias
└── README.md
```

---

## ⚙️ Instalación y uso local

```bash
# 1. Clonar / copiar los archivos a una carpeta
cd truck_loader

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app.py
```

La base de datos `truck_loader.db` se crea automáticamente en la misma carpeta al primer inicio.

---

## ☁️ Deploy en Streamlit Cloud

1. Subí la carpeta `truck_loader/` a un repositorio GitHub (público o privado).
2. Andá a [share.streamlit.io](https://share.streamlit.io) y conectá tu repo.
3. Configurá:
   - **Main file path:** `app.py`
   - **Python version:** 3.10+
4. Hacé clic en **Deploy**.

> ⚠️ En Streamlit Cloud la base de datos se resetea con cada redeploy.  
> Para persistencia en producción, reemplazá SQLite por **Supabase** o **PlanetScale** usando el mismo patrón de `database.py`.

---

## 🧠 Algoritmo de packing

Se usa el método de **Extreme Points** (variante del algoritmo 3D Bin Packing):

1. Se ordenan los bultos por volumen descendente (los más grandes primero).
2. Se prueban las **6 rotaciones** posibles de cada bulto.
3. Para cada punto extremo del espacio, se verifica si el bulto rotado entra sin superponerse.
4. Se elige la posición más cercana al piso-frente-izquierda (menor z·10 + x + y).
5. Al colocar un bulto se agregan 3 nuevos puntos extremos.

---

## 🚀 Funcionalidades

| Función | Descripción |
|---|---|
| 📦 Gestión de bultos | CRUD de tipos de bultos con dimensiones, peso y color |
| 🚛 Nuevo plan | Selección de camión (presets o manual), cantidades de bultos, generación del plan |
| 📊 Visualización 3D | Vista interactiva giratoria del camión con los bultos colocados |
| 🗺️ Vista 2D | Vista superior por capas de altura |
| 📋 Historial | Todos los planes guardados, revisables en cualquier momento |
| 🔄 Rotación | Los bultos se rotan automáticamente en las 6 orientaciones posibles |

---

## 📐 Unidades

Todas las medidas se trabajan en **metros** y el peso en **kilogramos**.
