import streamlit as st
import os
import pandas as pd
import plotly.express as px

# --- AUTENTICACIÓN ---
CLAVE_CORRECTA = "EFSECURITIZADORA"
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    clave_ingresada = st.text_input("🔒 Ingresa la clave de acceso", type="password")
    if clave_ingresada == CLAVE_CORRECTA:
        st.session_state.autenticado = True
        st.rerun()  # ← CORRECTO en versiones actuales
    else:
        st.stop()
        st.stop()
# ---------- CONFIGURACIÓN GENERAL ----------
st.set_page_config(page_title="Panel de Información - EF Securitizadora", layout="wide")

# Mostrar logo si existe
if os.path.exists("EF logo@4x.png"):
    st.image("EF logo@4x.png", width=200)

# Estilos generales
st.markdown("""
    <style>
    .stApp {
        background-color: #F0F4F8 !important;
        color: #000000 !important;
    }
    h1 {
        font-size: 3em !important;
        text-align: center !important;
        color: #002147 !important;
    }
    label {
        color: #002147 !important;
        font-weight: bold !important;
    }
    .stButton > button {
        background-color: #002147 !important;
        color: #FFFFFF !important;
        padding: 10px 24px !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 1.1em !important;
        font-weight: bold !important;
        margin: 5px 5px !important;
    }
    .stButton > button:hover {
        background-color: #34495E !important;
    }
    .button-bar {
        display: flex;
        justify-content: flex-end;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    /* SELECTBOX estilo */
    .stSelectbox > div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #002147 !important;
        border-radius: 6px !important;
        color: #002147 !important;
        font-weight: 600 !important;
    }
    .stSelectbox label {
        color: #002147 !important;
        font-weight: bold !important;
    }
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        color: #333 !important;
        font-size: 14px;
    }
    th {
        background-color: #004085 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 8px;
    }
    td {
        background-color: #FAFAFA !important;
        text-align: center !important;
        padding: 6px;
    }
    tr:nth-child(even) td {
        background-color: #EAF0F6 !important;
    }
    tr:hover td {
        background-color: #D0E3F1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Página por defecto
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

st.title("Panel de Información - EF Securitizadora")

# Botones de navegación
st.markdown('<div class="button-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
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

# Cargar datos
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

# Tabla con estilo
def estilo_tabla(df):
    html = df.to_html(index=False, escape=False, border=0)
    html = html.replace('<th', '<th style="text-align: center;"')
    html = html.replace('<td', '<td style="text-align: center;"')
    return html

# Página Inicio
if st.session_state.pagina == "Inicio":
    st.markdown("## Bienvenido al Panel de Información de EF Securitizadora.")
    st.markdown("Selecciona una pestaña en la parte superior para comenzar a explorar información sobre los patrimonios separados. Dentro de estas secciones podrás encontrar tanto los gastos y su distribución mensual, como también las principales definiciones que involucran a los patrimonios separados.")

# Página Gastos
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
        gastos_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio].drop(columns=["MONEDA"], errors="ignore")
        if frecuencia != 'Todos':
            gastos_filtrado = gastos_filtrado[gastos_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()]
        if not gastos_filtrado.empty:
            st.markdown(estilo_tabla(gastos_filtrado), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen datos para los filtros seleccionados.")
        
        cal_filtrado = df_calendario[df_calendario['PATRIMONIO'] == patrimonio].copy()
        if mes != 'Todos':
            cal_filtrado = cal_filtrado[cal_filtrado['MES'].str.upper() == mes.upper()]
        if not cal_filtrado.empty:
            st.markdown("## 📅 Calendario de Gastos")
            with st.expander("▶️ Ver tabla de Conceptos de Gastos", expanded=False):
                st.markdown(estilo_tabla(cal_filtrado[['MES', '2025']]), unsafe_allow_html=True)

            st.markdown("#### 📈 Gráfico de Área: Evolución de Gastos")

            cal_filtrado['CANTIDAD'] = pd.to_numeric(cal_filtrado['CANTIDAD'], errors='coerce').fillna(0).astype(int)
            fig = px.area(
                cal_filtrado,
                x='MES',
                y='CANTIDAD',
                title='',
                labels={'CANTIDAD': 'Cantidad de Gastos'}
            )
            fig.update_traces(line_color='black', line_width=3, fillcolor='rgba(0,123,255,0.3)')
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title='Mes',
                yaxis_title='Cantidad de Gastos',
                yaxis=dict(range=[0, cal_filtrado['CANTIDAD'].max() + 1], color='black'),
                xaxis=dict(color='black'),
                font=dict(color='black'),
                showlegend=False,
                margin=dict(t=30, b=30, l=30, r=30)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No existen datos para el mes y patrimonio seleccionados.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")

# Página Definiciones
if st.session_state.pagina == "Definiciones":
    st.markdown("### 📖 Definiciones y Triggers")
    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    patrimonio = st.selectbox("Patrimonio:", patrimonio_opciones, key="patrimonio_def")
    if patrimonio != '- Selecciona -':
        definiciones_filtrado = df_definiciones[df_definiciones['PATRIMONIO'] == patrimonio]
        if not definiciones_filtrado.empty:
            st.markdown("#### 📘 Definiciones")
            st.markdown(estilo_tabla(definiciones_filtrado), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No hay definiciones para el patrimonio seleccionado.")
        triggers_filtrado = df_triggers[df_triggers['PATRIMONIO'] == patrimonio]
        if not triggers_filtrado.empty:
            st.markdown("#### 📊 Triggers")
            st.markdown(estilo_tabla(triggers_filtrado), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen triggers para el patrimonio seleccionado.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")


