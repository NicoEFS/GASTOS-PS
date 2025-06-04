import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Panel de Información - EF Securitizadora", layout="wide")

# CLAVE DE ACCESO
PASSWORD = "ef2025"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("login"):
        clave = st.text_input("🔒 Ingrese la clave para acceder:", type="password")
        submit = st.form_submit_button("Ingresar")
        if submit:
            if clave == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Clave incorrecta. Intente nuevamente.")
    st.stop()

# MOSTRAR LOGO
if os.path.exists("EF logo@4x.png"):
    st.image("EF logo@4x.png", width=200)

# ESTILOS
st.markdown("""
    <style>
    .stApp { background-color: #F4F7FB !important; color: #000000 !important; }
    h1 { font-size: 3em !important; text-align: center !important; color: #0B1F3A !important; }
    label { color: #0B1F3A !important; font-weight: bold; }
    .stButton > button {
        background-color: #0B1F3A !important;
        color: #FFFFFF !important;
        padding: 10px 25px !important;
        border-radius: 8px !important;
        font-size: 1em !important;
        font-weight: bold !important;
        margin: 5px !important;
    }
    .stButton > button:hover {
        background-color: #003366 !important;
        color: #FFFFFF !important;
    }
    .button-bar { display: flex; justify-content: flex-end; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# PÁGINA POR DEFECTO
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

st.title("Panel de Información - EF Securitizadora")

# NAVEGACIÓN
st.markdown('<div class="button-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Inicio"):
        st.session_state.pagina = "Inicio"
with col2:
    if st.button("💰 Gastos"):
        st.session_state.pagina = "Gastos"
with col3:
    if st.button("📈 Definiciones"):
        st.session_state.pagina = "Definiciones"
st.markdown('</div>', unsafe_allow_html=True)

# CARGA DE DATOS
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
    df_años['AÑO'] = df_años['AÑO'].astype(str).str.strip()
    df_calendario['MES'] = df_calendario['MES'].str.strip().str.upper()  # limpieza aquí
    return df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers

df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers = cargar_datos()

# FUNCIONES
def estilo_tabla(df):
    html = df.to_html(index=False, escape=False, border=0)
    html = html.replace('<th', '<th style="text-align: center;"')
    html = html.replace('<td', '<td style="text-align: center;"')
    return html

# INICIO
if st.session_state.pagina == "Inicio":
    st.markdown("## Bienvenido al Panel de Información de EF Securitizadora.")
    st.markdown("""
    Selecciona una pestaña en la parte superior para comenzar a explorar información sobre los patrimonios separados.

    ### 🔗 Accesos rápidos a paneles de recaudación:
    - [RECAUDACIÓN PS10-HITES](https://app.powerbi.com/view?r=eyJrIjoiZGE0MzNiODYtZGQwOC00NTYwLTk2OWEtZWUwMjlhYzFjNWU2IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9)
    - [RECAUDACIÓN PS11-ADRETAIL](https://app.powerbi.com/view?r=eyJrIjoiMzQ4OGRhMTQtMThiYi00YjE2LWJlNjUtYTEzNGIyM2FiODA3IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9)
    - [RECAUDACIÓN PS12-MASISA](https://app.powerbi.com/view?r=eyJrIjoiNmI4NjE3NDktNzY4Yy00OWEwLWE0M2EtN2EzNjQ1NjRhNWQzIiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9)
    - [RECAUDACIÓN PS13-INCOFIN](https://app.powerbi.com/view?r=eyJrIjoiMTA2OTMyYjYtZDBjNS00YTIyLWFjNmYtMGE0OGQ5YjRmZDMxIiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9)
    """)

# ... [CÓDIGO ANTERIOR IGUAL HASTA LA SECCIÓN GASTOS]

# GASTOS
if st.session_state.pagina == "Gastos":
    st.markdown("### 💼 Gastos del Patrimonio")
    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        patrimonio = st.selectbox("Patrimonio:", patrimonio_opciones)
    with c2:
        año = st.selectbox("Año:", sorted(df_años['AÑO'].unique()))
    with c3:
        mes = st.selectbox("Mes:", ['Todos'] + list(df_calendario['MES'].unique()))
    with c4:
        frecuencia = st.selectbox("Frecuencia:", ['Todos', 'MENSUAL', 'ANUAL', 'TRIMESTRAL'])

    if patrimonio != '- Selecciona -':
        gastos_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]
        if frecuencia != 'Todos':
            gastos_filtrado = gastos_filtrado[gastos_filtrado['PERIODICIDAD'] == frecuencia]
        if not gastos_filtrado.empty:
            columnas_gastos = [col for col in gastos_filtrado.columns if col not in ['PATRIMONIO', 'MONEDA']]
            st.markdown(estilo_tabla(gastos_filtrado[columnas_gastos]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen datos para los filtros seleccionados.")
        
        cal_filtrado = df_calendario[df_calendario['PATRIMONIO'] == patrimonio].copy()
        if mes != 'Todos':
            cal_filtrado = cal_filtrado[cal_filtrado['MES'] == mes]

        if not cal_filtrado.empty:
            cal_filtrado.columns = cal_filtrado.columns.astype(str)  # Asegura que '2025' sea string
            cal_filtrado['CANTIDAD'] = pd.to_numeric(cal_filtrado['CANTIDAD'], errors='coerce').fillna(0).astype(int)
            orden_meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
                           'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
            cal_filtrado['MES'] = pd.Categorical(cal_filtrado['MES'], categories=orden_meses, ordered=True)
            cal_filtrado = cal_filtrado.sort_values('MES')

            st.markdown("### 📅 Calendario de Gastos")
            with st.expander("▶️ Ver tabla de calendario", expanded=False):
                columnas_tabla = ['MES', '2025'] if '2025' in cal_filtrado.columns else ['MES']
                st.dataframe(cal_filtrado[columnas_tabla], use_container_width=True, hide_index=True)

            st.markdown("### 📈 Gráfico de Gastos por Mes")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=cal_filtrado['MES'],
                y=cal_filtrado['CANTIDAD'],
                name='Cantidad de Gastos',
                marker=dict(color='lightsalmon')
            ))
            fig.add_trace(go.Scatter(
                x=cal_filtrado['MES'],
                y=cal_filtrado['CANTIDAD'],
                mode='lines+markers',
                name='Tendencia',
                line=dict(color='firebrick', width=2),
                marker=dict(size=6)
            ))
            fig.update_layout(
                xaxis_title='Mes',
                yaxis_title='Cantidad de Gastos',
                template='simple_white',
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No existen datos para el mes y patrimonio seleccionados.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")

# DEFINICIONES
if st.session_state.pagina == "Definiciones":
    st.markdown("### 📖 Definiciones y Triggers")
    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    patrimonio = st.selectbox("Patrimonio:", patrimonio_opciones, key="patrimonio_def")
    if patrimonio != '- Selecciona -':
        definiciones_filtrado = df_definiciones[df_definiciones['PATRIMONIO'] == patrimonio]
        if not definiciones_filtrado.empty:
            st.markdown("#### 📘 Definiciones")
            if 'CONCEPTO' in definiciones_filtrado.columns:
                definiciones_filtrado = definiciones_filtrado.sort_values(by='CONCEPTO')
            columnas_visibles = [col for col in definiciones_filtrado.columns if col != 'PATRIMONIO']
            st.markdown(estilo_tabla(definiciones_filtrado[columnas_visibles]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No hay definiciones para el patrimonio seleccionado.")

        triggers_filtrado = df_triggers[df_triggers['PATRIMONIO'] == patrimonio]
        if not triggers_filtrado.empty:
            st.markdown("#### 📊 Triggers")
            columnas_triggers = [col for col in triggers_filtrado.columns if col != 'PATRIMONIO']
            st.markdown(estilo_tabla(triggers_filtrado[columnas_triggers]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen triggers para el patrimonio seleccionado.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")





