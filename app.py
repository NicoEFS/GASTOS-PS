import streamlit as st
import os
import pandas as pd
from datetime import datetime, date
import plotly.express as px

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Panel de Información - EF Securitizadora", layout="wide")

# LISTA DE USUARIOS
usuarios_modifican = [
    "nvega@efsecuritizadora.cl",
    "jsepulveda@efsecuritizadora.cl"
]
usuarios_visualizan = [
    "jmiranda@efsecuritizadora.cl", "pgalvez@efsecuritizadora.cl", "ssales@efsecuritizadora.cl",
    "drodriguez@efsecuritizadora.cl", "csalazar@efsecuritizadora.cl", "ppellegrini@efsecuritizadora.cl",
    "cossa@efsecuritizadora.cl", "ptoro@efsecuritizadora.cl", "mleon@efsecuritizadora.cl",
    "jcoloma@efsecuritizadora.cl", "asiri@efsecuritizadora.cl"
]

# AUTENTICACIÓN POR CORREO Y CLAVE
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
        text-align: left !important;
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


# CARGA DE DATOS
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

df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers, df_reportes, df_herramientas = cargar_datos()

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

df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers, df_reportes, df_herramientas = cargar_datos()

# INICIO
if st.session_state.pagina == "Inicio":
    st.markdown("## Bienvenido al Panel de Información de EF Securitizadora.")
    st.markdown("""
    Selecciona una pestaña en la parte superior para comenzar a explorar información sobre los patrimonios separados. 
    Dentro de estas secciones podrás encontrar tanto los gastos y su distribución mensual, como también las principales definiciones que involucran a los patrimonios separados.

    ### 🔗 Accesos rápidos a paneles de recaudación:
    - [POWER BI-RECAUDACIÓN PS10 - HITES](https://app.powerbi.com/view?r=eyJrIjoiZGE0MzNiODYtZGQwOC00NTYwLTk2OWEtZWUwMjlhYzFjNWU2IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9)
    - [POWER BI-RECAUDACIÓN PS11 - ADRETAIL](https://app.powerbi.com/view?r=eyJrIjoiMzQ4OGRhMTQtMThiYi00YjE2LWJlNjUtYTEzNGIyM2FiODA3IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9)
    - [POWER BI-RECAUDACIÓN PS12 - MASISA](https://app.powerbi.com/view?r=eyJrIjoiNmI4NjE3NDktNzY4Yy00OWEwLWE0M2EtN2EzNjQ1NjRhNWQzIiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9)
    - [POWER BI-RECAUDACIÓN PS13 - INCOFIN](https://app.powerbi.com/view?r=eyJrIjoiMTA2OTMyYjYtZDBjNS00YTIyLWFjNmYtMGE0OGQ5YjRmZDMxIiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9)
    """)


# GASTOS
if st.session_state.pagina == "Gastos":
    st.markdown("### 💼 Gastos del Patrimonio")
    if st.button("🔄 Recargar archivos de gastos"):
        st.cache_data.clear()
        st.success("Datos recargados exitosamente.")
        st.rerun()

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
        cal_filtrado['MES'] = cal_filtrado['MES'].astype(str).str.strip().str.upper()

        if mes != 'Todos':
            mes = str(mes).strip().upper()
            cal_filtrado = cal_filtrado[cal_filtrado['MES'] == mes]

        if not cal_filtrado.empty:
            st.markdown("#### 🗓️ Calendario de Gastos")
            cal_filtrado['CANTIDAD'] = pd.to_numeric(cal_filtrado['CANTIDAD'], errors='coerce').fillna(0).astype(int)
            orden_meses = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
            cal_filtrado['MES'] = pd.Categorical(cal_filtrado['MES'], categories=orden_meses, ordered=True)
            cal_filtrado = cal_filtrado.sort_values('MES')

            with st.expander("▶️ Ver tabla de conceptos", expanded=False):
                if '2025' in cal_filtrado.columns:
                    st.markdown(estilo_tabla(cal_filtrado[['MES', '2025']]), unsafe_allow_html=True)
                else:
                    st.warning("⚠️ La columna '2025' no existe en el calendario.")

            fig = px.area(cal_filtrado, x='MES', y='CANTIDAD', labels={'CANTIDAD': 'Cantidad de Gastos'}, title='Tendencia de Gastos por Mes')
            fig.add_scatter(x=cal_filtrado['MES'], y=cal_filtrado['CANTIDAD'], mode='lines+markers', name='Tendencia', line=dict(color='black', width=2), marker=dict(color='black'))
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(color='black', size=14), margin=dict(t=40, b=40), xaxis_title='Mes', yaxis_title='Cantidad de Gastos', xaxis=dict(tickangle=-45))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No existen datos para el mes y patrimonio seleccionados.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")

# DEFINICIONES
if st.session_state.pagina == "Definiciones":
    st.markdown("### 📘 Definiciones y Triggers")
    if st.button("🔄 Recargar archivos"):
        st.cache_data.clear()
        st.success("Datos recargados exitosamente.")
        st.rerun()

    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    patrimonio = st.selectbox("Patrimonio:", patrimonio_opciones, key="patrimonio_def")

    if patrimonio != '- Selecciona -':
        patrimonio_upper = patrimonio.strip().upper()
        definiciones_filtrado = df_definiciones[df_definiciones['PATRIMONIO'] == patrimonio_upper]
        if not definiciones_filtrado.empty:
            st.markdown("#### 📒 Definiciones")
            if 'CONCEPTO' in definiciones_filtrado.columns:
                definiciones_filtrado = definiciones_filtrado.sort_values(by='CONCEPTO')
            columnas_visibles = [col for col in definiciones_filtrado.columns if col != 'PATRIMONIO']
            st.markdown(estilo_tabla(definiciones_filtrado[columnas_visibles]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No hay definiciones para el patrimonio seleccionado.")

        triggers_filtrado = df_triggers[df_triggers['PATRIMONIO'] == patrimonio_upper]
        if not triggers_filtrado.empty:
            st.markdown("#### 📊 Triggers")
            columnas_triggers = [col for col in triggers_filtrado.columns if col != 'PATRIMONIO']
            st.markdown(estilo_tabla(triggers_filtrado[columnas_triggers]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen triggers para el patrimonio seleccionado.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")



# REPORTES
if st.session_state.pagina == "Reportes":
    st.markdown("### 📋 Reportes por Patrimonio")

    # Botón para recargar archivos
    if st.button("🔄 Recargar archivos de reportes"):
        st.cache_data.clear()
        st.success("Archivos de reportes actualizados exitosamente.")
        st.rerun()

    patrimonio_opciones = ['- Selecciona -'] + sorted(df_reportes['PATRIMONIO'].dropna().unique())
    patrimonio = st.selectbox("Selecciona un patrimonio:", patrimonio_opciones, key="reporte_patrimonio")

    if patrimonio != '- Selecciona -':
        df_filtrado = df_reportes[df_reportes['PATRIMONIO'] == patrimonio]
        reportes_disponibles = sorted(df_filtrado['REPORTE'].dropna().unique())
        reporte = st.selectbox("Selecciona un reporte:", ['- Selecciona -'] + reportes_disponibles, key="reporte_tipo")

        if reporte != '- Selecciona -':
            st.markdown("#### 📄 Ítems a Revisar")
            items = df_filtrado[df_filtrado['REPORTE'] == reporte][['ITEM']].dropna()
            if not items.empty:
                st.markdown(estilo_tabla(items), unsafe_allow_html=True)
            else:
                st.warning("⚠️ No hay ítems a revisar para el reporte seleccionado.")

            st.markdown("#### 🛠 Herramientas y Objetivos")
            herramientas = df_herramientas[(df_herramientas['PATRIMONIO'] == patrimonio) & (df_herramientas['REPORTE'] == reporte)][['HERRAMIENTA', 'OBJETIVO']].dropna()
            if not herramientas.empty:
                st.markdown(estilo_tabla(herramientas), unsafe_allow_html=True)
            else:
                st.warning("⚠️ No hay herramientas registradas para el reporte seleccionado.")
        else:
            st.warning("⚠️ Por favor, selecciona un reporte para ver la información.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver los reportes disponibles.")

# SEGUIMIENTO
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

    fin_mes = pd.Timestamp(anio, mes, 1) + pd.offsets.MonthEnd(1)
    fechas.append(fin_mes.date())
    return fechas

if st.session_state.pagina == "Seguimiento":
    st.markdown("### 📅 Seguimiento de Cesiones Revolving")

    if st.button("🔄 Recargar archivo de seguimiento"):
        st.cache_data.clear()
        st.success("Archivo recargado exitosamente.")
        st.rerun()

    # Cargar archivo base
    df_raw = pd.read_excel("SEGUIMIENTO.xlsx", sheet_name=0, header=None)
    encabezados = df_raw.iloc[0].copy()
    encabezados[:3] = ["PATRIMONIO", "RESPONSABLE", "HITOS"]
    df_seg = df_raw[1:].copy()
    df_seg.columns = encabezados
    df_seg.columns = df_seg.columns.str.upper()

    patrimonios = ['- Selecciona -'] + sorted(df_seg["PATRIMONIO"].dropna().unique())
    patrimonio = st.selectbox("Selecciona un Patrimonio:", patrimonios, key="filtro_patrimonio")

    if patrimonio != '- Selecciona -':
        meses = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
            "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
            "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }

        mes_nombre = st.selectbox("Selecciona un Mes:", ["- Selecciona -"] + list(meses.keys()), key="mes_filtro")

        if mes_nombre != '- Selecciona -':
            mes = meses[mes_nombre]
            anio = 2025
            fechas_generadas = generar_fechas_personalizadas(anio, mes, patrimonio)
            fecha = st.selectbox("Selecciona una Fecha de Cesión:", ['- Selecciona -'] + fechas_generadas, key="fecha_filtro")

            if fecha != '- Selecciona -':
                df_filtrado = df_seg[df_seg["PATRIMONIO"] == patrimonio][["RESPONSABLE", "HITOS"]].copy()

                st.markdown("#### 📝 Actualiza el estado de cada hito:")
                nuevos_estados = []
                nuevos_comentarios = []

                for i, row in df_filtrado.iterrows():
                    st.markdown(
                        f"""
                        <div style='padding:18px; background-color:#E3ECF8; border-radius:12px; margin-bottom:25px;'>
                            <div style='font-size:1.2rem; font-weight:700; color:#0B1F3A; margin-bottom:10px;'>🧩 {row['HITOS']}</div>
                        """,
                        unsafe_allow_html=True
                    )

                    col1, col2 = st.columns([2, 3])
                    with col1:
                        estado = st.selectbox(
                            "Estado:",
                            options=["PENDIENTE", "REALIZADO", "ATRASADO"],
                            key=f"estado_{i}",
                            disabled=not permite_editar
                        )
                    with col2:
                        comentario = st.text_input(
                            "Comentario:",
                            key=f"comentario_{i}",
                            disabled=not permite_editar
                        )

                    icono_estado = {
                        "PENDIENTE": "🟡",
                        "REALIZADO": "🟢",
                        "ATRASADO": "🔴"
                    }.get(estado, "")

                    st.markdown(
                        f"<div style='margin-top:10px;'>{icono_estado} <b>Estado actual:</b> {estado.title()}</div>",
                        unsafe_allow_html=True
                    )

                    nuevos_estados.append(estado)
                    nuevos_comentarios.append(comentario)

                    st.markdown("</div>", unsafe_allow_html=True)

                if permite_editar and st.button("💾 Guardar Cambios"):
                    df_final = df_filtrado.copy()
                    df_final["PATRIMONIO"] = patrimonio
                    df_final["FECHA"] = fecha
                    df_final["ESTADO"] = nuevos_estados
                    df_final["COMENTARIO"] = nuevos_comentarios
                    df_final["ULTIMA_MODIFICACION"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    output_path = "estado_cesiones.xlsx"
                    if os.path.exists(output_path):
                        df_existente = pd.read_excel(output_path)
                        if "PATRIMONIO" in df_existente.columns and "FECHA" in df_existente.columns:
                            df_existente = df_existente[
                                ~((df_existente["PATRIMONIO"] == patrimonio) & (df_existente["FECHA"] == str(fecha)))
                            ]
                        df_resultado = pd.concat([df_existente, df_final], ignore_index=True)
                    else:
                        df_resultado = df_final

                    df_resultado.to_excel(output_path, index=False)
                    st.success("✅ Cambios guardados correctamente en estado_cesiones.xlsx")

                if os.path.exists("estado_cesiones.xlsx"):
                    with open("estado_cesiones.xlsx", "rb") as f:
                        st.download_button(
                            label="📥 Descargar archivo de estado",
                            data=f,
                            file_name="estado_cesiones.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.warning("⚠️ Por favor, selecciona una fecha de cesión.")
        else:
            st.warning("⚠️ Por favor, selecciona un mes.")
    else:
        st.warning("⚠️ Por favor, selecciona un patrimonio.")


