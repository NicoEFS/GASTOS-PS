import pandas as pd
import os
import streamlit as st
import re

# Configuración general
st.set_page_config(page_title="EF Securitizadora - Dashboard", layout="wide")

# =====================================
# ⚙️ Funciones generales
# =====================================
def limpiar_titulo(texto):
    return re.sub(r'\s*\(.*?\)', '', texto).strip()

def estilo_tabla(df):
    html = df.to_html(index=False, escape=False, border=0, classes='dataframe')
    html = html.replace('<th', '<th style="text-align: center;"')
    html = html.replace('<td', '<td style="text-align: center;"')
    return html

# =====================================
# 🎨 Estilos CSS
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
# 📁 Cargar datos una sola vez
# =====================================
@st.cache_data
def cargar_datos():
    df_gasto_ps = pd.read_excel('GASTO-PS.xlsx')
    df_calendario = pd.read_excel('CALENDARIO-GASTOS.xlsx')
    df_ps = pd.read_excel('PS.xlsx')
    df_años = pd.read_excel('TABLA AÑO.xlsx')
    df_definiciones = pd.read_excel('DEFINICIONES.xlsx')
    df_triggers = pd.read_excel('TRIGGERS.xlsx')

    for df in [df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers]:
        df.columns = df.columns.astype(str).str.strip().str.upper()

    df_calendario.columns = df_calendario.columns.astype(str).str.strip()
    df_años['AÑO'] = df_años['AÑO'].astype(str).str.strip()

    return df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers

df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers = cargar_datos()

# =====================================
# 🟢 Navegación inicial
# =====================================
opcion = st.radio("Selecciona una opción:", ["Inicio", "Gastos", "Definiciones"])

# =====================================
# 🏠 Pantalla de inicio
# =====================================
if opcion == "Inicio":
    st.image("EF logo-blanco@4x.png", width=300)
    st.title("EF Securitizadora - Dashboard")
    st.write("Bienvenido al dashboard de gestión de Gastos y Definiciones.")
    if st.button("Ir a Gastos"):
        st.experimental_set_query_params(pagina="Gastos")
    if st.button("Ir a Definiciones"):
        st.experimental_set_query_params(pagina="Definiciones")

# =====================================
# 💰 Sección de Gastos (tu código actual)
# =====================================
elif opcion == "Gastos":
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

    st.markdown(limpiar_titulo("### 💼 Gastos del Patrimonio"))
    gastos_ps_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]
    if frecuencia != 'Todos':
        gastos_ps_filtrado = gastos_ps_filtrado[gastos_ps_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()]
    if gastos_ps_filtrado.empty:
        st.warning("⚠️ No existen datos para el patrimonio y frecuencia seleccionados.")
    else:
        st.markdown(estilo_tabla(gastos_ps_filtrado), unsafe_allow_html=True)

    st.markdown(limpiar_titulo("### 📅 Calendario de Gastos"))
    año = str(año).strip()
    if año in df_calendario.columns:
        columnas = ['MES', 'PATRIMONIO', año]
        calendario_filtrado = df_calendario[columnas].copy()
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

# =====================================
# 📚 Sección de Definiciones
# =====================================
elif opcion == "Definiciones":
    st.title("EF Securitizadora - Definiciones y Triggers")

    st.markdown("### 📖 Definiciones Generales")
    st.markdown(estilo_tabla(df_definiciones), unsafe_allow_html=True)

    st.markdown("### ⚙️ Triggers por Patrimonio")
    patrimonio = st.selectbox("Selecciona un Patrimonio:", df_ps['PATRIMONIO'].unique())
    triggers_filtrado = df_triggers[df_triggers['PATRIMONIO'] == patrimonio]
    if triggers_filtrado.empty:
        st.warning("⚠️ No existen triggers para el patrimonio seleccionado.")
    else:
        st.markdown(estilo_tabla(triggers_filtrado), unsafe_allow_html=True)


