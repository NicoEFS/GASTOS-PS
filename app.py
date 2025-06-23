import streamlit as st
import os
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import json
from pathlib import Path


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
        clave = st.text_input("Clave de acceso:", type="password")
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
    if os.path.exists("seguimiento_guardado.json"):
        with open("seguimiento_guardado.json", "r", encoding="utf-8") as f:
            st.session_state.estado_actual = json.load(f)
    else:
        st.session_state.estado_actual = {}

# LOGO
if os.path.exists("EF logo@4x.png"):
    st.image("EF logo@4x.png", width=200)

# Botón cerrar sesión alineado a la esquina superior derecha
col1, col2, col3 = st.columns([6, 0.2, 1])
with col3:
    if st.button("🔒 Cerrar sesión"):
        st.session_state.authenticated = False
        st.session_state.usuario = ""
        st.success("Sesión cerrada correctamente.")
        st.rerun()



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
   Selecciona una pestaña en la parte superior para comenzar a explorar la información relacionada con los patrimonios separados. En las distintas secciones podrás revisar los gastos y su distribución mensual, acceder a las principales definiciones contables y operativas, consultar los ítems evaluados y las herramientas de revisión utilizadas en cada reporte, así como también realizar el seguimiento detallado de las cesiones revolving de cada patrimonio.

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



# --- SECCIÓN DEFINICIONES ---
def mostrar_definiciones():
    st.markdown("### 📚 Definiciones Patrimonios Separados")

    def estilo_tabla(df, header_bg="#0d1b2a", header_color="white", max_width="100%"):
        html = f"""
        <style>
        .styled-table {{
            width: {max_width};
            max-width: 100%;
            border-collapse: collapse;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            margin-left: 0;
        }}
        .styled-table thead th {{
            background-color: {header_bg};
            color: {header_color};
            padding: 8px;
            text-align: left;
        }}
        .styled-table td {{
            padding: 8px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        .styled-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        </style>
        <table class="styled-table">
            <thead>
                <tr>""" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr></thead><tbody>"

        for _, row in df.iterrows():
            html += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in df.columns) + "</tr>"
        html += "</tbody></table>"
        return html

    try:
        df_def = pd.read_excel("DEFINICIONES.xlsx", engine="openpyxl")
        df_def.columns = df_def.columns.str.upper().str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("utf-8").str.strip()

        col_patrimonio = next((c for c in df_def.columns if "PATRIMONIO" in c), None)
        col_concepto = next((c for c in df_def.columns if "CONCEPTO" in c), None)
        col_definicion = next((c for c in df_def.columns if "DEFIN" in c), None)

        if not all([col_patrimonio, col_concepto, col_definicion]):
            st.error("❌ Columnas necesarias no encontradas en DEFINICIONES.xlsx.")
            st.stop()

        opciones_def = ["Generales", "Contables"]
        opcion = st.radio("Selecciona el tipo de definición:", opciones_def, horizontal=True)

        if opcion == "Generales":
            st.markdown("### 🧠 **Definiciones Generales**")
            patrimonios_disponibles = df_def[df_def[col_patrimonio] != "PS-CONTABLE"][col_patrimonio].dropna().unique()
            patrimonios_ordenados = ["- Selecciona -"] + sorted(patrimonios_disponibles)
            selected_patrimonio = st.selectbox("Selecciona un patrimonio:", patrimonios_ordenados)

            if selected_patrimonio == "- Selecciona -":
                st.warning("⚠️ Por favor, selecciona un Patrimonio para visualizar sus definiciones.")
            else:
                df_filtrado = (
                    df_def[df_def[col_patrimonio] == selected_patrimonio]
                    [[col_concepto, col_definicion]]
                    .rename(columns={col_concepto: "CONCEPTO", col_definicion: "DEFINICIÓN"})
                    .sort_values("CONCEPTO")
                    .reset_index(drop=True)
                )
                st.markdown(estilo_tabla(df_filtrado), unsafe_allow_html=True)

        elif opcion == "Contables":
            st.markdown("### 🧾 **Definiciones Contables**")
            df_filtrado = (
                df_def[df_def[col_patrimonio] == "PS-CONTABLE"]
                [[col_concepto, col_definicion]]
                .rename(columns={col_concepto: "CONCEPTO", col_definicion: "DEFINICIÓN"})
                .sort_values("CONCEPTO")
                .reset_index(drop=True)
            )
            st.markdown(estilo_tabla(df_filtrado, max_width="900px"), unsafe_allow_html=True)

            st.markdown("### 📒 **Asientos Contables**")

            try:
                df_asientos = pd.read_excel("ASIENTOS.xlsx", engine="openpyxl")
                df_asientos.columns = df_asientos.columns.str.upper().str.strip()

                if not {"GLOSA", "CUENTA", "DEBE", "HABER"}.issubset(df_asientos.columns):
                    st.warning("❗ El archivo ASIENTOS.xlsx no tiene las columnas necesarias.")
                else:
                    df_asientos = df_asientos.fillna({"DEBE": 0, "HABER": 0})
                    for glosa, grupo in df_asientos.groupby("GLOSA"):
                        st.markdown(f"#### 📄 Asiento: {glosa}")
                        df_as = grupo[["CUENTA", "DEBE", "HABER"]].copy()
                        df_as["DEBE"] = df_as["DEBE"].astype(float)
                        df_as["HABER"] = df_as["HABER"].astype(float)

                        total_debe = df_as["DEBE"].sum()
                        total_haber = df_as["HABER"].sum()

                        df_totales = pd.DataFrame([{
                            "CUENTA": f"Totales {'✅' if total_debe == total_haber else '❌'}",
                            "DEBE": total_debe,
                            "HABER": total_haber
                        }])

                        df_final = pd.concat([df_as, df_totales], ignore_index=True)
                        df_final["DEBE"] = df_final["DEBE"].apply(lambda x: f"$ {x:,.0f}".replace(",", ".") if x else "")
                        df_final["HABER"] = df_final["HABER"].apply(lambda x: f"$ {x:,.0f}".replace(",", ".") if x else "")

                        st.markdown(estilo_tabla(df_final, max_width="900px"), unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error al procesar los asientos contables: {e}")

    except Exception as e:
        st.error(f"❌ Error general al cargar definiciones: {e}")


# --- LLAMADO CONTROLADO ---
if "pagina" in st.session_state and st.session_state.pagina == "Definiciones":
    mostrar_definiciones()



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


# --- SECCIÓN SEGUIMIENTO ---
if st.session_state.pagina == "Seguimiento":
    st.title("📅 Seguimiento de Cesiones Revolving")

    df_raw = pd.read_excel("SEGUIMIENTO.xlsx", sheet_name=0, header=None)
    encabezados = df_raw.iloc[0].copy()
    encabezados[:3] = ["PATRIMONIO", "RESPONSABLE", "HITOS"]
    df_seg = df_raw[1:].copy()
    df_seg.columns = encabezados

    if "estado_actual" not in st.session_state:
        if os.path.exists("seguimiento_guardado.json"):
            with open("seguimiento_guardado.json", "r", encoding="utf-8") as f:
                st.session_state.estado_actual = json.load(f)
        else:
            st.session_state.estado_actual = {}

    puede_modificar = st.session_state.email in [
        "nvega@efsecuritizadora.cl", "jsepulveda@efsecuritizadora.cl"
    ]

    patrimonios = sorted(df_seg["PATRIMONIO"].dropna().unique())
    patrimonio = st.selectbox("Selecciona un Patrimonio:", ["- Selecciona -"] + patrimonios)

    if patrimonio != "- Selecciona -":
        meses = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
            "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
            "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }
        mes_nombre = st.selectbox("Selecciona un Mes:", ["- Selecciona -"] + list(meses.keys()))

        if mes_nombre != "- Selecciona -":
            mes = meses[mes_nombre]
            anio = 2025

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

            fechas = generar_fechas_personalizadas(anio, mes, patrimonio)
            opciones_fechas = ["- Selecciona -"] + fechas
            fecha = st.selectbox("Selecciona una Fecha de Cesión:", opciones_fechas)

            if fecha != "- Selecciona -":
                fecha_str = fecha.strftime("%Y-%m-%d")
                key_estado = f"{patrimonio}|{fecha_str}"

                if key_estado not in st.session_state.estado_actual:
                    df_filtro = df_seg[df_seg["PATRIMONIO"] == patrimonio]
                    registros = []
                    for _, fila in df_filtro.iterrows():
                        registros.append({
                            "HITO": fila["HITOS"],
                            "RESPONSABLE": fila["RESPONSABLE"],
                            "ESTADO": "PENDIENTE",
                            "COMENTARIO": ""
                        })
                    st.session_state.estado_actual[key_estado] = registros

                registros = st.session_state.estado_actual[key_estado]

                color_estado = {
                    "REALIZADO": "#C6EFCE",
                    "PENDIENTE": "#FFF2CC",
                    "ATRASADO": "#F8CBAD"
                }

                for i, reg in enumerate(registros):
                    with st.container():
                        fondo = color_estado.get(reg["ESTADO"], "#FFF2CC")
                        st.markdown(
                            f"<div style='background-color:{fondo};padding:15px;border-radius:10px;margin-bottom:10px;'>",
                            unsafe_allow_html=True
                        )
                        st.markdown(f"**🧩 Hito {i+1}: {reg['HITO']}**")
                        st.markdown(f"**Responsable:** {reg['RESPONSABLE']}")

                        if puede_modificar:
                            estado = st.selectbox(
                                f"Estado del Hito {i+1}",
                                ["PENDIENTE", "REALIZADO", "ATRASADO"],
                                index=["PENDIENTE", "REALIZADO", "ATRASADO"].index(reg["ESTADO"]),
                                key=f"estado_{i}"
                            )
                            comentario = st.text_input(
                                f"Comentario del Hito {i+1}",
                                value=reg["COMENTARIO"],
                                key=f"comentario_{i}"
                            )
                            reg["ESTADO"] = estado
                            reg["COMENTARIO"] = comentario
                        else:
                            st.markdown(f"**Estado:** {reg['ESTADO']}")
                            st.markdown(f"**Comentario:** *{reg['COMENTARIO'] or '(Sin comentario)'}*")

                        st.markdown("</div>", unsafe_allow_html=True)

                if puede_modificar:
                    with open("seguimiento_guardado.json", "w", encoding="utf-8") as f:
                        json.dump(st.session_state.estado_actual, f, ensure_ascii=False, indent=2)
                    st.success("✅ Cambios guardados automáticamente.")














