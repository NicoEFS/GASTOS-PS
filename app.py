import streamlit as st
import os
import pandas as pd
from datetime import datetime, date
import plotly.express as px

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Panel de Información - EF Securitizadora", layout="wide")

# LISTA DE USUARIOS
usuarios_modifican = [
    "nvega@efsecuritizadora.cl", "jsepulveda@efsecuritizadora.cl"
]
usuarios_visualizan = [
    "jmiranda@efsecuritizadora.cl", "pgalvez@efsecuritizadora.cl", "ssales@efsecuritizadora.cl",
    "drodriguez@efsecuritizadora.cl", "csalazar@efsecuritizadora.cl", "ppellegrini@efsecuritizadora.cl",
    "cossa@efsecuritizadora.cl", "ptoro@efsecuritizadora.cl", "mleon@efsecuritizadora.cl",
    "jcoloma@efsecuritizadora.cl", "asiri@efsecuritizadora.cl"
]

# AUTENTICACIÓN
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.usuario = ""

if not st.session_state.authenticated:
    with st.form("login"):
        st.subheader("🔐 Acceso restringido")
        correo = st.text_input("Correo electrónico institucional")
        clave = st.text_input("Clave de acceso (ef2025):", type="password")
        submit = st.form_submit_button("Ingresar")
        if submit:
            if clave == "ef2025" and (correo in usuarios_modifican or correo in usuarios_visualizan):
                st.session_state.authenticated = True
                st.session_state.usuario = correo
                st.success("Acceso concedido")
                st.rerun()
            else:
                st.error("Credenciales inválidas. Verifica tu correo o clave.")
    st.stop()

permite_editar = st.session_state.usuario in usuarios_modifican

# INICIALIZACIÓN DE ESTADO
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"
if "estado_actual" not in st.session_state:
    st.session_state.estado_actual = {}

# LOGO
if os.path.exists("EF logo@4x.png"):
    st.image("EF logo@4x.png", width=200)

# ESTILOS PERSONALIZADOS
st.markdown("""
    <style>
    .stApp { background-color: #F4F7FB; color: #000000; }
    h1 { font-size: 3em; text-align: center; color: #0B1F3A; }
    label { color: #0B1F3A; font-weight: bold; }
    .stButton > button {
        background-color: #0B1F3A;
        color: #FFFFFF;
        padding: 10px 25px;
        border-radius: 8px;
        font-size: 1em;
        font-weight: bold;
        margin: 5px;
    }
    .stButton > button:hover {
        background-color: #003366;
        color: #FFFFFF;
    }
    .button-bar { display: flex; justify-content: flex-end; margin-bottom: 20px; }
    th, td {
        padding: 8px;
        text-align: left;
        vertical-align: middle;
        font-size: 0.95em;
    }
    th { background-color: #0B1F3A; color: white; }
    td { background-color: #FFFFFF; }
    tr:nth-child(even) td { background-color: #F1F1F1; }
    tr:hover td { background-color: #D3E3FC; }
    </style>
""", unsafe_allow_html=True)

# NAVEGACIÓN
st.title("Panel de Información - EF Securitizadora")
st.markdown('<div class="button-bar">', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
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
with col5:
    if st.button("📅 Seguimiento"):
        st.session_state.pagina = "Seguimiento"
st.markdown('</div>', unsafe_allow_html=True)

# FUNCIONES UTILITARIAS
@st.cache_data
def cargar_datos():
    df_gasto_ps = pd.read_excel('GASTO-PS.xlsx')
    df_calendario = pd.read_excel('CALENDARIO-GASTOS.xlsx')
    df_ps = pd.read_excel('PS.xlsx')
    df_años = pd.read_excel('TABLA AÑO.xlsx')
    df_definiciones = pd.read_excel('DEFINICIONES.xlsx', engine='openpyxl')
    df_triggers = pd.read_excel('TRIGGERS.xlsx', engine='openpyxl')
    df_reportes = pd.read_excel('REPORTES.xlsx', engine='openpyxl')
    df_herramientas = pd.read_excel('HERRAMIENTAS.xlsx', engine='openpyxl')

    for df in [df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers, df_reportes, df_herramientas]:
        df.columns = df.columns.astype(str).str.strip().str.upper()
    df_años['AÑO'] = df_años['AÑO'].astype(str).str.strip()
    df_reportes[['PATRIMONIO', 'REPORTE']] = df_reportes[['PATRIMONIO', 'REPORTE']].fillna(method='ffill')
    df_herramientas[['PATRIMONIO', 'REPORTE']] = df_herramientas[['PATRIMONIO', 'REPORTE']].fillna(method='ffill')

    return df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers, df_reportes, df_herramientas

def estilo_tabla(df):
    def resaltar_item(text):
        if isinstance(text, str) and ':' in text:
            partes = text.split(':', 1)
            return f"<b>{partes[0].strip()}</b>: {partes[1].strip()}"
        return text

    df_formateado = df.copy()
    if 'ITEM' in df_formateado.columns:
        df_formateado['ITEM'] = df_formateado['ITEM'].apply(resaltar_item)

    html = df_formateado.to_html(index=False, escape=False, border=0)
    html = html.replace('<th', '<th style="text-align: center;"')
    html = html.replace('<td', '<td style="text-align: left;"')
    return html

# CARGA DE DATOS
df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers, df_reportes, df_herramientas = cargar_datos()

# INICIO
if st.session_state.pagina == "Inicio":
    st.markdown("## Bienvenido al Panel de Información de EF Securitizadora.")
    st.markdown("""
    Selecciona una pestaña en la parte superior para comenzar a explorar información sobre los patrimonios separados.

    ### 🔗 Accesos rápidos:
    - [PS10 - HITES](https://app.powerbi.com/view?r=link1)
    - [PS11 - ADRETAIL](https://app.powerbi.com/view?r=link2)
    - [PS12 - MASISA](https://app.powerbi.com/view?r=link3)
    - [PS13 - INCOFIN](https://app.powerbi.com/view?r=link4)
    """)

# GASTOS
if st.session_state.pagina == "Gastos":
    st.markdown("### 💼 Gastos del Patrimonio")
    if st.button("🔄 Recargar archivos de gastos"):
        st.cache_data.clear()
        st.rerun()

    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    patrimonio = st.selectbox("Patrimonio:", patrimonio_opciones)
    año = st.selectbox("Año:", sorted(df_años['AÑO'].unique()))
    mes = st.selectbox("Mes:", ['Todos'] + list(df_calendario['MES'].unique()))
    frecuencia = st.selectbox("Frecuencia:", ['Todos', 'MENSUAL', 'ANUAL', 'TRIMESTRAL'])

    if patrimonio != '- Selecciona -':
        gastos_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]
        if frecuencia != 'Todos':
            gastos_filtrado = gastos_filtrado[gastos_filtrado['PERIODICIDAD'] == frecuencia]
        if not gastos_filtrado.empty:
            columnas = [c for c in gastos_filtrado.columns if c not in ['PATRIMONIO', 'MONEDA']]
            st.markdown(estilo_tabla(gastos_filtrado[columnas]), unsafe_allow_html=True)

# DEFINICIONES
if st.session_state.pagina == "Definiciones":
    st.markdown("### 📘 Definiciones y Triggers")
    if st.button("🔄 Recargar archivos"):
        st.cache_data.clear()
        st.rerun()

    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    patrimonio = st.selectbox("Patrimonio:", patrimonio_opciones)
    if patrimonio != '- Selecciona -':
        df_def = df_definiciones[df_definiciones['PATRIMONIO'] == patrimonio]
        df_trig = df_triggers[df_triggers['PATRIMONIO'] == patrimonio]
        if not df_def.empty:
            st.markdown(estilo_tabla(df_def.drop(columns='PATRIMONIO')), unsafe_allow_html=True)
        if not df_trig.empty:
            st.markdown(estilo_tabla(df_trig.drop(columns='PATRIMONIO')), unsafe_allow_html=True)

# REPORTES
if st.session_state.pagina == "Reportes":
    st.markdown("### 📋 Reportes por Patrimonio")
    if st.button("🔄 Recargar archivos de reportes"):
        st.cache_data.clear()
        st.rerun()

    patrimonio_opciones = ['- Selecciona -'] + list(df_reportes['PATRIMONIO'].dropna().unique())
    patrimonio = st.selectbox("Selecciona un patrimonio:", patrimonio_opciones)
    if patrimonio != '- Selecciona -':
        df_r = df_reportes[df_reportes['PATRIMONIO'] == patrimonio]
        reportes_disponibles = sorted(df_r['REPORTE'].dropna().unique())
        reporte = st.selectbox("Selecciona un reporte:", ['- Selecciona -'] + reportes_disponibles)
        if reporte != '- Selecciona -':
            df_items = df_r[df_r['REPORTE'] == reporte][['ITEM']].dropna()
            df_herr = df_herramientas[(df_herramientas['PATRIMONIO'] == patrimonio) & (df_herramientas['REPORTE'] == reporte)]
            if not df_items.empty:
                st.markdown(estilo_tabla(df_items), unsafe_allow_html=True)
            if not df_herr.empty:
                st.markdown(estilo_tabla(df_herr[['HERRAMIENTA', 'OBJETIVO']]), unsafe_allow_html=True)

# FUNCIÓN DE FECHAS
def generar_fechas_personalizadas(anio, mes, patrimonio):
    if patrimonio in ["PS13-INCOFIN", "PS11-ADRETAIL"]:
        dias = [10, 20]
    elif patrimonio in ["PS10-HITES", "PS12-MASISA"]:
        dias = [7, 14, 21]
    else:
        dias = []
    fechas = []
    for dia in dias:
        try:
            fechas.append(date(anio, mes, dia))
        except ValueError:
            continue
    fechas.append((pd.Timestamp(anio, mes, 1) + pd.offsets.MonthEnd(1)).date())
    return fechas

# SEGUIMIENTO
if st.session_state.pagina == "Seguimiento":
    st.title("📅 Seguimiento de Cesiones Revolving")
    df_raw = pd.read_excel("SEGUIMIENTO.xlsx", sheet_name=0, header=None)
    encabezados = df_raw.iloc[0].copy()
    encabezados[:3] = ["PATRIMONIO", "RESPONSABLE", "HITOS"]
    df_seg = df_raw[1:].copy()
    df_seg.columns = encabezados

    patrimonios = sorted(df_seg["PATRIMONIO"].dropna().unique())
    patrimonio = st.selectbox("Selecciona un Patrimonio:", ["- Selecciona -"] + patrimonios)

    if patrimonio != "- Selecciona -":
        meses = {mes: idx for idx, mes in enumerate(
            ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], 1)}
        mes_nombre = st.selectbox("Selecciona un Mes:", ["- Selecciona -"] + list(meses.keys()))
        if mes_nombre != "- Selecciona -":
            mes = meses[mes_nombre]
            anio = 2025
            fechas = generar_fechas_personalizadas(anio, mes, patrimonio)
            fecha = st.selectbox("Selecciona una Fecha de Cesión:", ["- Selecciona -"] + fechas)
            if fecha != "- Selecciona -":
                fecha_str = fecha.strftime("%Y-%m-%d")
                key_estado = f"{patrimonio}|{fecha_str}"
                if key_estado not in st.session_state.estado_actual:
                    st.session_state.estado_actual[key_estado] = []

                df_filtrado = df_seg[df_seg["PATRIMONIO"] == patrimonio][["RESPONSABLE", "HITOS"]].copy()
                st.subheader("📝 Estado de cada hito:")
                nuevos_registros = []
                for i, row in df_filtrado.iterrows():
                    hito = row["HITOS"]
                    responsable = row["RESPONSABLE"]
                    estado_default = "PENDIENTE"
                    comentario_default = ""
                    for registro in st.session_state.estado_actual[key_estado]:
                        if registro["HITO"] == hito:
                            estado_default = registro["ESTADO"]
                            comentario_default = registro["COMENTARIO"]

                    col1, col2 = st.columns([2, 3])
                    with col1:
                        estado = st.selectbox("Estado:", ["PENDIENTE", "REALIZADO", "ATRASADO"],
                                              key=f"estado_{i}", index=["PENDIENTE", "REALIZADO", "ATRASADO"].index(estado_default))
                    with col2:
                        comentario = st.text_input("Comentario:", value=comentario_default, key=f"comentario_{i}")

                    nuevos_registros.append({
                        "HITO": hito, "RESPONSABLE": responsable, "ESTADO": estado,
                        "COMENTARIO": comentario, "FECHA": fecha_str,
                        "MODIFICADO_POR": st.session_state.usuario,
                        "TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                if permite_editar and st.button("💾 Guardar Cambios"):
                    st.session_state.estado_actual[key_estado] = nuevos_registros
                    st.success("Cambios guardados correctamente.")

                if st.session_state.estado_actual.get(key_estado):
                    st.markdown("### 📊 Estado guardado")
                    df_mostrar = pd.DataFrame(st.session_state.estado_actual[key_estado])
                    st.dataframe(df_mostrar[["HITO", "ESTADO", "COMENTARIO", "MODIFICADO_POR", "TIMESTAMP"]])




