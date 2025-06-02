import streamlit as st
import os
import pandas as pd
import re

st.set_page_config(page_title="Panel de Información - EF Securitizadora", layout="wide")

# Mostrar logo si existe
if os.path.exists("EF logo-blanco@4x.png"):
    st.image("EF logo-blanco@4x.png", width=300)

# Estilos generales y botones de navegación
st.markdown("""
    <style>
    .stApp { background-color: #0B1F3A !important; color: #FFFFFF !important; }
    h1 { font-size: 3em !important; text-align: center !important; color: #FFFFFF !important; }
    label { color: #FFFFFF !important; }
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        padding: 15px 30px !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 1.3em !important;
        margin: 5px !important;
    }
    .stButton > button:hover { background-color: #CCCCCC !important; }
    .button-bar { display: flex; justify-content: flex-end; margin-top: 10px; margin-bottom: 20px; }
    table { width: 100% !important; border-collapse: collapse !important; color: #333 !important; }
    th, td { border: 1px solid #004085 !important; padding: 8px !important; text-align: center !important; vertical-align: middle !important; }
    th { background-color: #E0E0E0 !important; color: #000 !important; font-weight: bold !important; }
    td { background-color: #F5F5F5 !important; }
    tr:nth-child(even) td { background-color: #E8E8E8 !important; }
    tr:hover td { background-color: #D0D0D0 !important; }
    </style>
""", unsafe_allow_html=True)

# Inicializar página
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

# Título principal
st.title("Panel de Información - EF Securitizadora")

# Botones de navegación a la derecha
st.markdown('<div class="button-bar">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("🏠 Inicio"):
        st.session_state.pagina = "Inicio"
with c2:
    if st.button("💰 Gastos"):
        st.session_state.pagina = "Gastos"
with c3:
    if st.button("📚 Definiciones"):
        st.session_state.pagina = "Definiciones"
st.markdown('</div>', unsafe_allow_html=True)

# Funciones
def estilo_tabla(df):
    html = df.to_html(index=False, escape=False, border=0)
    html = html.replace('<th', '<th style="text-align: center;"')
    html = html.replace('<td', '<td style="text-align: center;"')
    return html

@st.cache_data
def cargar_datos():
    df_gasto_ps = pd.read_excel('GASTO-PS.xlsx')
    df_calendario = pd.read_excel('CALENDARIO-GASTOS.xlsx')
    df_ps = pd.read_excel('PS.xlsx')
    df_años = pd.read_excel('TABLA AÑO.xlsx')
    df_definiciones = pd.read_excel('DEFINICIONES.xlsx', engine='openpyxl')
    df_triggers = pd.read_excel('TRIGGERS.xlsx', engine='openpyxl')

    for df in [df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers]:
        df.columns = df.columns.astype(str).str.strip().str.upper()
    df_calendario.columns = df_calendario.columns.astype(str).str.strip()
    df_años['AÑO'] = df_años['AÑO'].astype(str).str.strip()
    return df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers

df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers = cargar_datos()

# Renderizado de la página
if st.session_state.pagina == "Inicio":
    st.markdown("### Bienvenido al panel de información de EF Securitizadora.")
elif st.session_state.pagina == "Gastos":
    st.markdown("### 💼 Gastos del Patrimonio")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        patrimonio = st.selectbox("Patrimonio:", df_ps['PATRIMONIO'].unique())
    with c2:
        año = st.selectbox("Año:", sorted(df_años['AÑO'].unique()))
    with c3:
        mes = st.selectbox("Mes:", ['Todos'] + list(df_calendario['MES'].unique()))
    with c4:
        frecuencia = st.selectbox("Frecuencia:", ['Todos', 'MENSUAL', 'ANUAL', 'TRIMESTRAL'])

    gastos_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]
    if frecuencia != 'Todos':
        gastos_filtrado = gastos_filtrado[gastos_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()]
    if not gastos_filtrado.empty:
        st.markdown(estilo_tabla(gastos_filtrado), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No existen datos para los filtros seleccionados.")

    if año in df_calendario.columns:
        cal_cols = ['MES', 'PATRIMONIO', año]
        cal_filtrado = df_calendario[cal_cols][df_calendario['PATRIMONIO'] == patrimonio]
        if mes != 'Todos':
            cal_filtrado = cal_filtrado[cal_filtrado['MES'].str.upper() == mes.upper()]
        cal_filtrado = cal_filtrado.rename(columns={año: 'GASTOS'}).dropna(subset=['GASTOS'])
        st.markdown("### 📅 Calendario de Gastos")
        if not cal_filtrado.empty:
            st.markdown(estilo_tabla(cal_filtrado), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen datos para el año y filtros seleccionados.")
    else:
        st.warning("⚠️ El año seleccionado no está presente en la tabla.")
elif st.session_state.pagina == "Definiciones":
    st.markdown("### 📖 Definiciones Generales")
    if not df_definiciones.empty:
        st.markdown(estilo_tabla(df_definiciones), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No hay definiciones cargadas.")
    st.markdown("### ⚙️ Triggers por Patrimonio")
    if not df_triggers.empty:
        patrimonio = st.selectbox("Patrimonio:", df_ps['PATRIMONIO'].unique())
        triggers = df_triggers[df_triggers['PATRIMONIO'] == patrimonio]
        if not triggers.empty:
            st.markdown(estilo_tabla(triggers), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen triggers para el patrimonio seleccionado.")
    else:
        st.warning("⚠️ No hay triggers cargados.")


