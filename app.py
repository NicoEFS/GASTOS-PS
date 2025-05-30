import pandas as pd
import os
import streamlit as st
import re

# =====================================
# 📁 Configuración de la página
# =====================================
st.set_page_config(
    page_title="EF Securitizadora - Gastos de los Patrimonios Separados",
    layout="wide"
)

# =====================================
# 🖼️ Mostrar el logo en la parte superior
# =====================================
logo_path = "EF logo-blanco@4x.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=300)
else:
    st.warning("⚠️ El logo no se encuentra en la carpeta actual.")

# =====================================
# ⚙️ Utilidades
# =====================================
@st.cache_data
def cargar_datos(ruta):
    archivos = {
        "GASTO-PS": "GASTO-PS.xlsx",
        "CALENDARIO-GASTOS": "CALENDARIO-GASTOS.xlsx",
        "PS": "PS.xlsx",
        "AÑOS": "TABLA AÑO.xlsx",
    }
    # Cargar todos los dataframes en un solo paso y limpiar columnas
    dfs = {}
    for k, v in archivos.items():
        df = pd.read_excel(os.path.join(ruta, v))
        df.columns = df.columns.map(str).str.strip().str.upper()
        dfs[k] = df
    # Ajustes específicos
    dfs["CALENDARIO-GASTOS"].columns = dfs["CALENDARIO-GASTOS"].columns.map(str).str.strip()
    dfs["AÑOS"]["AÑO"] = dfs["AÑOS"]["AÑO"].astype(str).str.strip()
    return dfs

def limpiar_titulo(texto):
    return re.sub(r'\s*\(.*?\)', '', texto).strip()

def estilo_tabla(df):
    if df.empty:
        return ""
    html = df.to_html(index=False, escape=False, border=0, classes="dataframe")
    html = html.replace("<th", '<th style="text-align: center;"')
    html = html.replace("<td", '<td style="text-align: center;"')
    return html

# =====================================
# 🎨 Estilos de la página y tablas
# =====================================
st.markdown(
    """
    <style>
    .stApp { background-color: #0B1F3A !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #FFFFFF !important; text-align: center !important; }
    label { color: #FFFFFF !important; }
    table { width: 100% !important; border-collapse: collapse !important; color: #333333 !important; }
    th, td { border: 1px solid #004085 !important; padding: 8px !important; text-align: center !important; vertical-align: middle !important; }
    th { background-color: #E0E0E0 !important; color: #000000 !important; font-weight: bold !important; }
    td { background-color: #F5F5F5 !important; }
    tr:nth-child(even) td { background-color: #E8E8E8 !important; }
    tr:hover td { background-color: #D0D0D0 !important; }
    .stButton > button { background-color: #007BFF !important; color: #FFFFFF !important; border: none !important; padding: 0.5em 1em !important; border-radius: 4px !important; }
    .stButton > button:hover { background-color: #0056b3 !important; color: #FFFFFF !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# 📁 Cargar datos
# =====================================
RUTA_DATOS = "."
dfs = cargar_datos(RUTA_DATOS)
df_gasto_ps = dfs["GASTO-PS"]
df_calendario = dfs["CALENDARIO-GASTOS"]
df_ps = dfs["PS"]
df_años = dfs["AÑOS"]

# =====================================
# 🎛️ Filtros
# =====================================
st.title("EF Securitizadora - Gastos de los Patrimonios Separados")

col1, col2, col3, col4 = st.columns(4)
with col1:
    patrimonio = st.selectbox("Selecciona un Patrimonio:", df_ps["PATRIMONIO"].unique())
with col2:
    año = st.selectbox("Selecciona un Año:", sorted(df_años["AÑO"].unique()))
with col3:
    meses_opciones = ["Todos"] + sorted(df_calendario["MES"].dropna().unique())
    mes = st.selectbox("Selecciona un Mes:", meses_opciones)
with col4:
    frecuencia_opciones = ["Todos", "MENSUAL", "ANUAL", "TRIMESTRAL"]
    frecuencia = st.selectbox("Frecuencia:", frecuencia_opciones)

# =====================================
# 📊 Mostrar tabla de Gastos del Patrimonio
# =====================================
st.markdown(limpiar_titulo("### 💼 Gastos del Patrimonio (GASTO-PS)"))
gastos_ps_filtrado = df_gasto_ps[df_gasto_ps["PATRIMONIO"] == patrimonio]
if frecuencia != "Todos":
    gastos_ps_filtrado = gastos_ps_filtrado[gastos_ps_filtrado["PERIODICIDAD"].str.upper() == frecuencia.upper()]

if gastos_ps_filtrado.empty:
    st.warning("⚠️ No existen datos para el patrimonio y frecuencia seleccionados.")
else:
    st.markdown(estilo_tabla(gastos_ps_filtrado), unsafe_allow_html=True)

# =====================================
# 📊 Mostrar tabla de Calendario de Gastos
# =====================================
st.markdown(limpiar_titulo("### 📅 Calendario de Gastos (CALENDARIO-GASTOS)"))
año = str(año).strip()
if año in df_calendario.columns:
    columnas = ["MES", "PATRIMONIO", año]
    calendario_filtrado = df_calendario[df_calendario["PATRIMONIO"] == patrimonio][columnas].copy()
    if mes != "Todos":
        calendario_filtrado = calendario_filtrado[calendario_filtrado["MES"].str.upper() == mes.upper()]
    calendario_filtrado = calendario_filtrado.rename(columns={año: "GASTOS"}).dropna(subset=["GASTOS"])
    if calendario_filtrado.empty:
        st.warning("⚠️ No existen datos para el año y filtros seleccionados.")
    else:
        st.markdown(estilo_tabla(calendario_filtrado), unsafe_allow_html=True)
else:
    st.warning("⚠️ El año seleccionado no está presente como columna en la tabla de calendario.")

