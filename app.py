import pandas as pd
import os
import streamlit as st
import re

# =====================================
# 📁 Configuración de la página
# =====================================
st.set_page_config(page_title="EF Securitizadora - Gastos de los Patrimonios Separados", layout="wide")

# =====================================
# ⚙️ Función para limpiar títulos (quitar texto entre paréntesis)
# =====================================
def limpiar_titulo(texto):
    return re.sub(r'\s*\(.*?\)', '', texto).strip()

# =====================================
# 🎨 Estilos generales de la página y tablas
# =====================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1a2a3a;
        color: #ffffff;
    }
    h1, h2, h3 {
        color: #ffffff;
        text-align: center;  /* Centramos los títulos */
    }
    .css-10trblm {
        color: #ffffff;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        color: #333333;
    }
    th, td {
        border: 1px solid #004085;
        padding: 8px;
        text-align: center;  /* Centramos los encabezados y datos */
    }
    th {
        background-color: #e0e0e0;
        color: #000000;
    }
    td {
        background-color: #f5f5f5;
    }
    tr:nth-child(even) td {
        background-color: #e8e8e8;
    }
    tr:hover td {
        background-color: #d0d0d0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# ⚠️ Definir la ruta donde están los archivos Excel
ruta = "."

# =====================================
# 📁 Cargar datos
# =====================================
@st.cache_data
def cargar_datos():
    df_gasto_ps = pd.read_excel(os.path.join(ruta, 'GASTO-PS.xlsx'))
    df_calendario = pd.read_excel(os.path.join(ruta, 'CALENDARIO-GASTOS.xlsx'))
    df_ps = pd.read_excel(os.path.join(ruta, 'PS.xlsx'))
    df_años = pd.read_excel(os.path.join(ruta, 'TABLA AÑO.xlsx'))

    for df in [df_gasto_ps, df_calendario, df_ps, df_años]:
        df.columns = df.columns.astype(str).str.strip().str.upper()

    df_calendario.columns = df_calendario.columns.astype(str).str.strip()
    df_años['AÑO'] = df_años['AÑO'].astype(str).str.strip()

    return df_gasto_ps, df_calendario, df_ps, df_años

df_gasto_ps, df_calendario, df_ps, df_años = cargar_datos()

# =====================================
# 🎛️ Filtros
# =====================================
st.title("EF Securitizadora - Gastos de los Patrimonios Separados")

col1, col2, col3, col4 = st.columns(4)
with col1:
    patrimonio = st.selectbox("Selecciona un Patrimonio:", df_ps['PATRIMONIO'].unique())
with col2:
    año = st.selectbox("Selecciona un Año:", sorted(df_años['AÑO'].unique()))
with col3:
    meses_opciones = ['Todos'] + list(df_calendario['MES'].unique())
    mes = st.selectbox("Selecciona un Mes:", meses_opciones)
with col4:
    frecuencia_opciones = ['Todos', 'MENSUAL', 'ANUAL', 'TRIMESTRAL']
    frecuencia = st.selectbox("Frecuencia:", frecuencia_opciones)

# =====================================
# 🎨 Función para convertir tabla a HTML con estilo
# =====================================
def estilo_tabla(df):
    return df.to_html(index=False, escape=False, border=0)

# =====================================
# 📊 Mostrar tabla de Gastos del Patrimonio
# =====================================
titulo_gastos = "### 💼 Gastos del Patrimonio (GASTO-PS)"
st.markdown(limpiar_titulo(titulo_gastos))

gastos_ps_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]
if frecuencia != 'Todos':
    gastos_ps_filtrado = gastos_ps_filtrado[
        gastos_ps_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()
    ]

if gastos_ps_filtrado.empty:
    st.warning("⚠️ No existen datos para el patrimonio y frecuencia seleccionados.")
else:
    st.markdown(estilo_tabla(gastos_ps_filtrado), unsafe_allow_html=True)

# =====================================
# 📊 Mostrar tabla de Calendario de Gastos
# =====================================
titulo_calendario = "### 📅 Calendario de Gastos (CALENDARIO-GASTOS)"
st.markdown(limpiar_titulo(titulo_calendario))

año = str(año).strip()
if año in df_calendario.columns:
    columnas_a_mostrar = ['MES', 'PATRIMONIO', año]
    calendario_filtrado = df_calendario[columnas_a_mostrar].copy()
    calendario_filtrado = calendario_filtrado[calendario_filtrado['PATRIMONIO'] == patrimonio]
    if mes != 'Todos':
        calendario_filtrado = calendario_filtrado[calendario_filtrado['MES'].str.upper() == mes.upper()]
    calendario_filtrado = calendario_filtrado.rename(columns={año: 'GASTOS'})
    calendario_filtrado = calendario_filtrado.dropna(subset=['GASTOS'])
    if calendario_filtrado.empty:
        st.warning("⚠️ No existen datos para el año y filtros seleccionados.")
    else:
        st.markdown(estilo_tabla(calendario_filtrado), unsafe_allow_html=True)
else:
    st.warning("⚠️ El año seleccionado no está presente como columna en la tabla de calendario.")




