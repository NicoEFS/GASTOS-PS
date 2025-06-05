import streamlit as st
import os
import pandas as pd
import plotly.express as px

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Panel de Información - EF Securitizadora", layout="wide")

# CLAVE DE ACCESO
PASSWORD = "ef2025"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("login"):
        clave = st.text_input("\U0001F512 Ingrese la clave para acceder:", type="password")
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
    th, td {
        padding: 8px !important;
        text-align: center !important;
        vertical-align: middle !important;
        font-size: 0.95em;
    }
    th { background-color: #0B1F3A !important; color: white !important; }
    td { background-color: #FFFFFF !important; }
    tr:nth-child(even) td { background-color: #F1F1F1 !important; }
    tr:hover td { background-color: #D3E3FC !important; }
    </style>
""", unsafe_allow_html=True)

# PÁGINA POR DEFECTO
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

st.title("Panel de Información - EF Securitizadora")

# NAVEGACIÓN
st.markdown('<div class="button-bar">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🏠 Inicio"):
        st.session_state.pagina = "Inicio"
with col2:
    if st.button("💰 Gastos"):
        st.session_state.pagina = "Gastos"
with col3:
    if st.button("📈 Definiciones"):
        st.session_state.pagina = "Definiciones"
with col4:
    if st.button("📋 Reportes"):
        st.session_state.pagina = "Reportes"
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
    return df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers

df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers = cargar_datos()

def estilo_tabla(df):
    html = df.to_html(index=False, escape=False, border=0)
    html = html.replace('<th', '<th style="text-align: left;"')
    html = html.replace('<td', '<td style="text-align: left;"')
    return html

# INICIO
if st.session_state.pagina == "Inicio":
    st.markdown("## Bienvenido al Panel de Información de EF Securitizadora.")
    st.markdown("""
    Selecciona una pestaña en la parte superior para comenzar a explorar información sobre los patrimonios separados. 
    Dentro de estas secciones podrás encontrar tanto los gastos y su distribución mensual, como también las principales definiciones que involucran a los patrimonios separados.

    ### \U0001F517 Accesos rápidos a paneles de recaudación:
    - [RECAUDACIÓN PS10-HITES](https://app.powerbi.com/view?r=eyJrIjoiZGE0...)
    - [RECAUDACIÓN PS11-ADRETAIL](https://app.powerbi.com/view?r=eyJrIjoiMzQ4...)
    - [RECAUDACIÓN PS12-MASISA](https://app.powerbi.com/view?r=eyJrIjoiNmI4...)
    - [RECAUDACIÓN PS13-INCOFIN](https://app.powerbi.com/view?r=eyJrIjoiMTA2...)
    """)

# GASTOS
if st.session_state.pagina == "Gastos":
    st.markdown("### \U0001F4BC Gastos del Patrimonio")
    
    # Botón para recargar datos
    if st.button("🔄 Recargar archivos de gastos"):
        st.cache_data.clear()
        st.success("Datos recargados exitosamente.")
        st.rerun()
    
    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    c1, c2, c3, c4 = st.columns(4)
    
if st.session_state.pagina == "Gastos":
    st.markdown("### \U0001F4BC Gastos del Patrimonio")
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

        # Limpieza robusta de la columna MES
        cal_filtrado['MES'] = cal_filtrado['MES'].astype(str).str.strip().str.upper()

        if mes != 'Todos':
            mes = str(mes).strip().upper()
            cal_filtrado = cal_filtrado[cal_filtrado['MES'] == mes]

        if not cal_filtrado.empty:
            st.markdown("#### \U0001F4C5 Calendario de Gastos")
            cal_filtrado['CANTIDAD'] = pd.to_numeric(cal_filtrado['CANTIDAD'], errors='coerce').fillna(0).astype(int)
            orden_meses = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
            cal_filtrado['MES'] = pd.Categorical(cal_filtrado['MES'], categories=orden_meses, ordered=True)
            cal_filtrado = cal_filtrado.sort_values('MES')

            with st.expander("▶️ Ver tabla de conceptos", expanded=False):
                if '2025' in cal_filtrado.columns:
                    st.markdown(estilo_tabla(cal_filtrado[['MES', '2025']]), unsafe_allow_html=True)
                else:
                    st.warning("⚠️ La columna '2025' no existe en el calendario.")

            fig = px.area(
                cal_filtrado,
                x='MES',
                y='CANTIDAD',
                labels={'CANTIDAD': 'Cantidad de Gastos'},
                title='Tendencia de Gastos por Mes',
            )
            fig.add_scatter(
                x=cal_filtrado['MES'],
                y=cal_filtrado['CANTIDAD'],
                mode='lines+markers',
                name='Tendencia',
                line=dict(color='black', width=2),
                marker=dict(color='black')
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='black', size=14),
                margin=dict(t=40, b=40),
                xaxis_title='Mes',
                yaxis_title='Cantidad de Gastos',
                xaxis=dict(tickangle=-45)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No existen datos para el mes y patrimonio seleccionados.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")


# DEFINICIONES

def obtener_definiciones_y_triggers():
    df_def = pd.read_excel('DEFINICIONES.xlsx', engine='openpyxl')
    df_trig = pd.read_excel('TRIGGERS.xlsx', engine='openpyxl')
    df_def.columns = df_def.columns.astype(str).str.strip().str.upper()
    df_trig.columns = df_trig.columns.astype(str).str.strip().str.upper()
    df_def['PATRIMONIO'] = df_def['PATRIMONIO'].astype(str).str.strip().str.upper()
    df_trig['PATRIMONIO'] = df_trig['PATRIMONIO'].astype(str).str.strip().str.upper()
    return df_def, df_trig

def mostrar_definiciones():
    st.markdown("### \U0001F4D6 Definiciones y Triggers")
    
    # Botón para recargar los datos si el Excel fue actualizado
    if st.button("🔄 Recargar archivos"):
        st.cache_data.clear()
        st.success("Datos recargados exitosamente.")
        st.rerun()

    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    patrimonio = st.selectbox("Patrimonio:", patrimonio_opciones, key="patrimonio_def")

    df_def, df_trig = obtener_definiciones_y_triggers()

    if patrimonio != '- Selecciona -':
        patrimonio_upper = patrimonio.strip().upper()
        
        definiciones_filtrado = df_def[df_def['PATRIMONIO'] == patrimonio_upper]
        if not definiciones_filtrado.empty:
            st.markdown("#### \U0001F4D8 Definiciones")
            if 'CONCEPTO' in definiciones_filtrado.columns:
                definiciones_filtrado = definiciones_filtrado.sort_values(by='CONCEPTO')
            columnas_visibles = [col for col in definiciones_filtrado.columns if col != 'PATRIMONIO']
            st.markdown(estilo_tabla(definiciones_filtrado[columnas_visibles]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No hay definiciones para el patrimonio seleccionado.")

        triggers_filtrado = df_trig[df_trig['PATRIMONIO'] == patrimonio_upper]
        if not triggers_filtrado.empty:
            st.markdown("#### \U0001F4CA Triggers")
            columnas_triggers = [col for col in triggers_filtrado.columns if col != 'PATRIMONIO']
            st.markdown(estilo_tabla(triggers_filtrado[columnas_triggers]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen triggers para el patrimonio seleccionado.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")

# Mostrar definiciones si corresponde
if st.session_state.pagina == "Definiciones":
    mostrar_definiciones()

# SECCIÓN REPORTES NUEVA VERSIÓN CON DOS ARCHIVOS
if st.session_state.pagina == "Reportes":
    st.markdown("### 📋 Reportes por Patrimonio")

    # Cargar archivos y preparar
    df_reportes = pd.read_excel("REPORTES.xlsx", engine="openpyxl")
    df_herramientas = pd.read_excel("HERRAMIENTAS.xlsx", engine="openpyxl")

    for df in [df_reportes, df_herramientas]:
        df.columns = df.columns.str.strip().str.upper()
        df[['PATRIMONIO', 'REPORTE']] = df[['PATRIMONIO', 'REPORTE']].fillna(method='ffill')

    # Filtros
    patrimonios = ['- Selecciona -'] + sorted(df_reportes['PATRIMONIO'].unique())
    patrimonio = st.selectbox("Selecciona un patrimonio:", patrimonios, key="reporte_patrimonio")

    if patrimonio != '- Selecciona -':
        reportes_disponibles = sorted(df_reportes[df_reportes['PATRIMONIO'] == patrimonio]['REPORTE'].unique())
        reporte = st.selectbox("Selecciona un reporte:", ['- Selecciona -'] + reportes_disponibles, key="reporte_tipo")

        if reporte != '- Selecciona -':
            st.markdown("#### 📄 Ítems a Revisar")
            items = df_reportes[
                (df_reportes['PATRIMONIO'] == patrimonio) &
                (df_reportes['REPORTE'] == reporte)
            ][['ITEM']].dropna()

            if not items.empty:
                st.markdown(estilo_tabla(items), unsafe_allow_html=True)
            else:
                st.info("No hay ítems a revisar para este reporte.")

            st.markdown("#### 🛠 Herramientas y Objetivos")
            herramientas = df_herramientas[
                (df_herramientas['PATRIMONIO'] == patrimonio) &
                (df_herramientas['REPORTE'] == reporte)
            ][['HERRAMIENTA', 'OBJETIVO']].dropna()

            if not herramientas.empty:
                st.markdown(estilo_tabla(herramientas), unsafe_allow_html=True)
            else:
                st.info("No hay herramientas registradas para este reporte.")
        else:
            st.info("Selecciona un reporte para ver la información.")
    else:
        st.info("Selecciona un patrimonio para comenzar.")

