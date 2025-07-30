import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
from pathlib import Path
import plotly.express as px

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Panel EF Securitizadora", layout="wide")

# --- USUARIOS AUTORIZADOS ---
usuarios_modifican = [
    "nvega@efsecuritizadora.cl", "jsepulveda@efsecuritizadora.cl"
]
usuarios_visualizan = [
    "jmiranda@efsecuritizadora.cl", "pgalvez@efsecuritizadora.cl", "ssales@efsecuritizadora.cl",
    "drodriguez@efsecuritizadora.cl", "csalazar@efsecuritizadora.cl", "ppellegrini@efsecuritizadora.cl",
    "cossa@efsecuritizadora.cl", "ptoro@efsecuritizadora.cl", "mleon@efsecuritizadora.cl",
    "jcoloma@efsecuritizadora.cl", "asiri@efsecuritizadora.cl"
]

# --- AUTENTICACIÓN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.usuario = ""

if not st.session_state.authenticated:
    st.image("EF logo@4x.png", width=180)
    with st.form("login"):
        st.subheader("🔐 Acceso restringido")
        correo = st.text_input("Correo institucional")
        clave = st.text_input("Clave de acceso", type="password")
        submit = st.form_submit_button("Ingresar")
        if submit:
            if clave == "ef2025" and (correo in usuarios_modifican or correo in usuarios_visualizan):
                st.session_state.authenticated = True
                st.session_state.usuario = correo
                st.success("Acceso concedido")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

# --- ESTADO GLOBAL ---
permite_editar = st.session_state.usuario in usuarios_modifican
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"
if "estado_actual" not in st.session_state:
    if os.path.exists("seguimiento_guardado.json"):
        with open("seguimiento_guardado.json", "r", encoding="utf-8") as f:
            st.session_state.estado_actual = json.load(f)
    else:
        st.session_state.estado_actual = {}

# --- ESTILO GLOBAL ---
st.markdown("""
    <style>
    .sidebar-nav .sidebar-item {
        padding: 1rem 1rem;          /* Aumenta el alto */
        font-size: 1.1rem;           /* Texto más grande */
        font-weight: 600;
        color: #0B1F3A;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .sidebar-nav .sidebar-item:hover {
        background-color: #e0e7f0;
        cursor: pointer;
    }
    .stRadio > div {
        flex-direction: column;
    }
    .stRadio div[role=radiogroup] label {
        padding: 12px 18px;
        font-size: 1.1rem;
        border-radius: 8px;
        background-color: #f0f4f9;
        margin-bottom: 0.6rem;
    }
    .stRadio div[role=radiogroup] label:hover {
        background-color: #e2ebf5;
    }
    .stRadio div[role=radiogroup] input:checked + div {
        background-color: #d0e2f2 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# --- SIDEBAR NAVEGACIÓN ---
with st.sidebar:
    st.image("EF logo@4x.png", width=180)
    st.markdown('<div class="sidebar-title">Panel EF Securitizadora</div>', unsafe_allow_html=True)

    pagina = st.radio("Ir a la sección:", ["Inicio", "Gastos", "Definiciones", "Reportes", "Seguimiento"], index=["Inicio", "Gastos", "Definiciones", "Reportes", "Seguimiento"].index(st.session_state.pagina))
    st.session_state.pagina = pagina

    st.divider()
    st.markdown(f"**Usuario:** {st.session_state.usuario}")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.authenticated = False
        st.session_state.usuario = ""
        st.rerun()

# --- FUNCIONES GENERALES ---
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

def estilo_tabla(df, max_width="100%"):
    html = f"""
    <style>
    .styled-table {{
        width: {max_width};
        border-collapse: collapse;
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        margin-top: 10px;
    }}
    .styled-table th {{
        background-color: #0b1f3a;
        color: white;
        text-align: left;
        padding: 10px;
        border-bottom: 2px solid #ddd;
    }}
    .styled-table td {{
        padding: 8px;
        border-bottom: 1px solid #ddd;
        text-align: left;
    }}
    .styled-table tr:nth-child(even) {{
        background-color: #f4f7fb;
    }}
    .styled-table tr:hover {{
        background-color: #e6f0ff;
    }}
    </style>
    <table class="styled-table">
        <thead>
            <tr>""" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in df.columns) + "</tr>"
    html += "</tbody></table>"
    return html


# --- CARGA DE DATOS UNA VEZ ---
df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers, df_reportes, df_herramientas = cargar_datos()

# --- RUTEO DE PÁGINAS ---
if st.session_state.pagina == "Inicio":
    st.title("🏠 Bienvenido al Panel de Información de EF Securitizadora")
    st.markdown("""
    Este panel permite consultar información relevante de los Patrimonios Separados, incluyendo gastos, reportes, definiciones contables y seguimiento de cesiones revolving.
    
    ### Accesos rápidos a Power BI:
    - [Recaudación PS10 - HITES](https://app.powerbi.com/view?r=eyJrIjoiZGE0...)
    - [Recaudación PS11 - ADRETAIL](https://app.powerbi.com/view?r=eyJrIjoiMzQ4...)
    - [Recaudación PS12 - MASISA](https://app.powerbi.com/view?r=eyJrIjoiNmI4...)
    - [Recaudación PS13 - INCOFIN](https://app.powerbi.com/view?r=eyJrIjoiMTA2...)
    """)

# secccion gastos

elif st.session_state.pagina == "Gastos":
    st.title("💰 Gastos del Patrimonio")

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

            fig = px.area(
                cal_filtrado, x='MES', y='CANTIDAD',
                labels={'CANTIDAD': 'Cantidad de Gastos'},
                title='Tendencia de Gastos por Mes'
            )
            fig.add_scatter(
                x=cal_filtrado['MES'], y=cal_filtrado['CANTIDAD'],
                mode='lines+markers', name='Tendencia',
                line=dict(color='black', width=2), marker=dict(color='black')
            )
            fig.update_layout(
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color='black', size=14), margin=dict(t=40, b=40),
                xaxis_title='Mes', yaxis_title='Cantidad de Gastos', xaxis=dict(tickangle=-45)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No existen datos para el mes y patrimonio seleccionados.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")

# --- SECCIÓN DEFINICIONES ---
def mostrar_definiciones():
    st.title("📘 Definiciones Patrimonios Separados")

    def estilo_tabla(df, header_bg="#0d1b2a", header_color="white", max_width="100%"):
        html = f"""
        <style>
        .styled-table {{
            width: {max_width};
            border-collapse: collapse;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
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
        .styled-table tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
        <table class="styled-table">
            <thead><tr>""" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr></thead><tbody>"

        for _, row in df.iterrows():
            html += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in df.columns) + "</tr>"
        html += "</tbody></table>"
        return html

    try:
        df_def = pd.read_excel("DEFINICIONES.xlsx", engine="openpyxl")
        df_def.columns = (
            df_def.columns
            .str.upper()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
            .str.strip()
        )

        col_patrimonio = next((c for c in df_def.columns if "PATRIMONIO" in c), None)
        col_concepto = next((c for c in df_def.columns if "CONCEPTO" in c), None)
        col_definicion = next((c for c in df_def.columns if "DEFIN" in c), None)

        if not all([col_patrimonio, col_concepto, col_definicion]):
            st.error("❌ No se encontraron las columnas 'PATRIMONIO', 'CONCEPTO' o 'DEFINICIÓN'.")
            return

        opcion = st.radio("Selecciona el tipo de definición:", ["Generales", "Contables"], horizontal=True)

        if opcion == "Generales":
            st.markdown("### 🧠 Definiciones Generales")
            patrimonios_disponibles = df_def[df_def[col_patrimonio] != "PS-CONTABLE"][col_patrimonio].dropna().unique()
            patrimonios_ordenados = ["- Selecciona -"] + sorted(patrimonios_disponibles)
            selected = st.selectbox("Selecciona un patrimonio:", patrimonios_ordenados)

            if selected != "- Selecciona -":
                df_filtrado = (
                    df_def[df_def[col_patrimonio] == selected]
                    [[col_concepto, col_definicion]]
                    .rename(columns={col_concepto: "CONCEPTO", col_definicion: "DEFINICIÓN"})
                    .sort_values("CONCEPTO")
                    .reset_index(drop=True)
                )
                st.markdown(estilo_tabla(df_filtrado), unsafe_allow_html=True)
            else:
                st.warning("⚠️ Por favor, selecciona un Patrimonio para visualizar las definiciones.")

        else:  # Contables
            st.markdown("### 🧾 Definiciones Contables")
            df_filtrado = (
                df_def[df_def[col_patrimonio] == "PS-CONTABLE"]
                [[col_concepto, col_definicion]]
                .rename(columns={col_concepto: "CONCEPTO", col_definicion: "DEFINICIÓN"})
                .sort_values("CONCEPTO")
                .reset_index(drop=True)
            )
            st.markdown(estilo_tabla(df_filtrado, max_width="900px"), unsafe_allow_html=True)

            st.markdown("### 📒 Asientos Contables")

            try:
                df_asientos = pd.read_excel("ASIENTOS.xlsx", engine="openpyxl")
                df_asientos.columns = df_asientos.columns.str.upper().str.strip()

                if not {"GLOSA", "CUENTA", "DEBE", "HABER"}.issubset(df_asientos.columns):
                    st.warning("❗ El archivo ASIENTOS.xlsx no contiene las columnas necesarias.")
                else:
                    df_asientos = df_asientos.fillna({"DEBE": 0, "HABER": 0})
                    glosas = list(df_asientos['GLOSA'].unique())

                    for i in range(0, len(glosas), 2):
                        cols = st.columns(2)
                        for j in range(2):
                            if i + j < len(glosas):
                                glosa = glosas[i + j]
                                grupo = df_asientos[df_asientos["GLOSA"] == glosa]
                                with cols[j]:
                                    st.markdown(f"#### 📄 {glosa}")
                                    df_as = grupo[["CUENTA", "DEBE", "HABER"]].copy()
                                    df_as[["DEBE", "HABER"]] = df_as[["DEBE", "HABER"]].astype(float)

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

                                    st.markdown(estilo_tabla(df_final, max_width="100%"), unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error al procesar los asientos contables: {e}")

    except Exception as e:
        st.error(f"❌ Error general al cargar definiciones: {e}")


# llamado desde navegación (fuera de la función)
if st.session_state.pagina == "Definiciones":
    mostrar_definiciones()


#REPORTES
elif st.session_state.pagina == "Reportes":
    st.title("📋 Reportes por Patrimonio")

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
            herramientas = df_herramientas[
                (df_herramientas['PATRIMONIO'] == patrimonio) & 
                (df_herramientas['REPORTE'] == reporte)
            ][['HERRAMIENTA', 'OBJETIVO']].dropna()
            if not herramientas.empty:
                st.markdown(estilo_tabla(herramientas), unsafe_allow_html=True)
            else:
                st.warning("⚠️ No hay herramientas registradas para el reporte seleccionado.")
        else:
            st.warning("⚠️ Por favor, selecciona un reporte para ver la información.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver los reportes disponibles.")



# --- ESTILOS DE TARJETAS ---
st.markdown("""
    <style>
    .tarjeta-hito {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 18px;
        border: 1px solid #ccc;
        font-family: Arial, sans-serif;
        font-size: 14px;
    }
    .separador-cesion {
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 10px;
        font-size: 16px;
        color: #0B1F3A;
    }
    </style>
""", unsafe_allow_html=True)

# --- SECCIÓN SEGUIMIENTO ---
if st.session_state.pagina == "Seguimiento":
    st.title("🗕️ Seguimiento de Cesiones Revolving")

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
            opciones_fechas = ["- Selecciona -", "📂 Todas las Cesiones del Mes"] + fechas
            fecha = st.selectbox("Selecciona una Fecha de Cesión:", opciones_fechas)

            if fecha == "📂 Todas las Cesiones del Mes":
                registros_mes = []
                for clave, lista in st.session_state.estado_actual.items():
                    clave_pat, clave_fecha = clave.split("|")
                    fecha_obj = datetime.strptime(clave_fecha, "%Y-%m-%d")
                    if clave_pat == patrimonio and fecha_obj.month == mes:
                        registros_mes.extend([
                            {**reg, "FECHA": clave_fecha} for reg in lista
                        ])

                if registros_mes:
                    st.markdown("### 📂 Vista consolidada de todas las cesiones del mes")
                    registros_ordenados = sorted(registros_mes, key=lambda r: (r["FECHA"], r["HITO"]))
                    fechas_unicas = sorted(set(r["FECHA"] for r in registros_ordenados))

                    for cesion_fecha in fechas_unicas:
                        st.markdown(f"#### 📂 Cesión del {cesion_fecha}")
                        for idx, reg in enumerate([r for r in registros_ordenados if r["FECHA"] == cesion_fecha], 1):
                            color_fondo = {
                                "REALIZADO": "#C6EFCE",
                                "PENDIENTE": "#FFF2CC",
                                "ATRASADO": "#F8CBAD"
                            }.get(reg["ESTADO"], "#FFF2CC")

                            html_card = f"""
                            <div style="background-color: {color_fondo}; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;">
                                <p style="font-weight: bold;">🧹 #{idx} - {reg['HITO']}</p>
                                <p><strong>Responsable:</strong> {reg['RESPONSABLE']}</p>
                                <p><strong>Estado:</strong> {reg['ESTADO']}</p>
                                <p><strong>Comentario:</strong> <em>{reg['COMENTARIO'] or '(Sin comentario)'}</em></p>
                            </div>
                            """
                            st.markdown(html_card, unsafe_allow_html=True)

                    df_export = pd.DataFrame(registros_ordenados)[["FECHA", "HITO", "RESPONSABLE", "ESTADO", "COMENTARIO"]]
                    df_export.insert(1, "PATRIMONIO", patrimonio)
                    Path("seguimiento_excel").mkdir(exist_ok=True)
                    nombre_archivo = f"seguimiento_excel/SEGUIMIENTO_{patrimonio.replace('-', '')}_{mes_nombre.upper()}_{anio}.xlsx"
                    df_export.to_excel(nombre_archivo, index=False)

                    with open(nombre_archivo, "rb") as f:
                        st.download_button(
                            label="📅 Descargar seguimiento consolidado del mes",
                            data=f,
                            file_name=os.path.basename(nombre_archivo),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("No hay registros guardados para este mes.")
                st.stop()

            elif fecha != "- Selecciona -":
                fecha_str = fecha.strftime("%Y-%m-%d")
                key_estado = f"{patrimonio}|{fecha_str}"

                if key_estado not in st.session_state.estado_actual:
                    df_base = df_seg[df_seg["PATRIMONIO"] == patrimonio][["HITOS", "RESPONSABLE"]].copy()
                    registros_base = []
                    for _, row in df_base.iterrows():
                        registros_base.append({
                            "HITO": row["HITOS"],
                            "RESPONSABLE": row["RESPONSABLE"],
                            "ESTADO": "PENDIENTE",
                            "COMENTARIO": ""
                        })
                    st.session_state.estado_actual[key_estado] = registros_base

                registros = st.session_state.estado_actual[key_estado]

                st.markdown("### Estado actual de la cesión")
                for idx, reg in enumerate(registros, 1):
                    color_fondo = {
                        "REALIZADO": "#C6EFCE",
                        "PENDIENTE": "#FFF2CC",
                        "ATRASADO": "#F8CBAD"
                    }.get(reg["ESTADO"], "#FFF2CC")

                    html_card = f"""
                    <div style="background-color: {color_fondo}; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;">
                        <p style="font-weight: bold;">🧩 #{idx} - {reg['HITO']}</p>
                        <p><strong>Responsable:</strong> {reg['RESPONSABLE']}</p>
                        <p><strong>Estado:</strong> {reg['ESTADO']}</p>
                        <p><strong>Comentario:</strong> <em>{reg['COMENTARIO'] or '(Sin comentario)'}</em></p>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)

                df_export = pd.DataFrame(registros)[["HITO", "RESPONSABLE", "ESTADO", "COMENTARIO"]]
                df_export.insert(0, "FECHA", fecha_str)
                df_export.insert(1, "PATRIMONIO", patrimonio)
                nombre_archivo = f"seguimiento_excel/SEGUIMIENTO_{patrimonio.replace('-', '')}_{fecha_str}.xlsx"
                Path("seguimiento_excel").mkdir(exist_ok=True)
                df_export.to_excel(nombre_archivo, index=False)

                with open(nombre_archivo, "rb") as f:
                    st.download_button(
                        label="📅 Descargar seguimiento de la cesión",
                        data=f,
                        file_name=os.path.basename(nombre_archivo),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                # --- Edición solo para usuarios autorizados ---
                usuario_actual = st.session_state.get("usuario", "").lower()
                usuarios_modifican = [
                    "nvega@efsecuritizadora.cl", "jsepulveda@efsecuritizadora.cl"
                ]

                if usuario_actual in usuarios_modifican:
                    st.markdown("### ✏️ Modificar Estado de Cesión")
                    nuevos_registros = []
                    for i, reg in enumerate(registros):
                        st.markdown(f"<div style='margin-top:1.2rem;'><strong>🧩 {reg['HITO']}</strong></div>", unsafe_allow_html=True)
                        cols = st.columns([1, 3])
                        with cols[0]:
                            nuevo_estado = st.selectbox(
                                "Estado", ["PENDIENTE", "REALIZADO", "ATRASADO"],
                                index=["PENDIENTE", "REALIZADO", "ATRASADO"].index(reg["ESTADO"]),
                                key=f"estado_{i}"
                            )
                        with cols[1]:
                            nuevo_comentario = st.text_input(
                                "Comentario", value=reg["COMENTARIO"], key=f"comentario_{i}"
                            )
                        nuevos_registros.append({
                            "HITO": reg["HITO"],
                            "RESPONSABLE": reg["RESPONSABLE"],
                            "ESTADO": nuevo_estado,
                            "COMENTARIO": nuevo_comentario
                        })

                    if st.button("💾 Guardar cambios"):
                        st.session_state.estado_actual[key_estado] = nuevos_registros
                        with open("seguimiento_guardado.json", "w", encoding="utf-8") as f:
                            json.dump(st.session_state.estado_actual, f, ensure_ascii=False, indent=2)
                        st.success("Cambios guardados exitosamente.")
                        st.experimental_rerun()

                    df_actualizado = pd.DataFrame(nuevos_registros)[["HITO", "RESPONSABLE", "ESTADO", "COMENTARIO"]]
                    df_actualizado.insert(0, "FECHA", fecha_str)
                    df_actualizado.insert(1, "PATRIMONIO", patrimonio)
                    nombre_excel_actual = f"seguimiento_excel/SEGUIMIENTO_EDITABLE_{patrimonio.replace('-', '')}_{fecha_str}.xlsx"
                    df_actualizado.to_excel(nombre_excel_actual, index=False)

                    with open(nombre_excel_actual, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Excel editable actualizado",
                            data=f,
                            file_name=os.path.basename(nombre_excel_actual),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
