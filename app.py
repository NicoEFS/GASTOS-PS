import streamlit as st
import pandas as pd
import json
import os
import base64
from datetime import date, datetime
from pathlib import Path
import plotly.express as px

# --- ESTILOS DE TABLAS GLOBALES ---
st.markdown("""
<style>
.tabla-ef {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
.tabla-ef th {
    background-color: #0B1F3A;
    color: white;
    padding: 8px;
    text-align: left;
}
.tabla-ef td {
    padding: 8px;
    border-bottom: 1px solid #ddd;
}
.tabla-ef tr:nth-child(even) {
    background-color: #f9f9f9;
}
</style>
""", unsafe_allow_html=True)

def estilo_tabla(df):
    """Devuelve HTML estilizado para usar en st.markdown."""
    return df.to_html(index=False, border=0, classes='tabla-ef')

def estilo_tabla_con_totales(df_as):
    """Genera tabla contable con totales formateados y validación visual ✅/❌."""
    total_debe = df_as["DEBE"].sum()
    total_haber = df_as["HABER"].sum()
    cuadrado = "✅" if total_debe == total_haber else "❌"
    df_totales = pd.DataFrame([{
        "CUENTA": f"Totales {cuadrado}",
        "DEBE": total_debe,
        "HABER": total_haber
    }])
    df_final = pd.concat([df_as, df_totales], ignore_index=True)
    df_final["DEBE"] = df_final["DEBE"].apply(lambda x: f"$ {x:,.0f}".replace(",", ".") if x else "")
    df_final["HABER"] = df_final["HABER"].apply(lambda x: f"$ {x:,.0f}".replace(",", ".") if x else "")
    return estilo_tabla(df_final)


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
        padding: 1rem 1rem;
        font-size: 1.1rem;
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
    pagina = st.radio(
         "Ir a la sección:",
         ["Inicio", "Gastos", "Definiciones", "Reportes", "Seguimiento", "BI Recaudación"],
          index=["Inicio", "Gastos", "Definiciones", "Reportes", "Seguimiento", "BI Recaudación"].index(st.session_state.pagina)
    )
    st.session_state.pagina = pagina

    st.divider()
    st.markdown(f"**Usuario:** {st.session_state.usuario}")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.authenticated = False
        st.session_state.usuario = ""
        st.rerun()

# --- FUNCIONES ---
def _files_mtime():
    files=["GASTO-PS.xlsx","CALENDARIO-GASTOS.xlsx","PS.xlsx","TABLA AÑO.xlsx","DEFINICIONES.xlsx","TRIGGERS.xlsx","REPORTES.xlsx","HERRAMIENTAS.xlsx"]
    return tuple(os.path.getmtime(f) if os.path.exists(f) else 0 for f in files)

@st.cache_data
def cargar_datos(_mtimes):
    df_gasto_ps=pd.read_excel("GASTO-PS.xlsx")
    df_calendario=pd.read_excel("CALENDARIO-GASTOS.xlsx")
    df_ps=pd.read_excel("PS.xlsx")
    df_años=pd.read_excel("TABLA AÑO.xlsx")
    df_definiciones=pd.read_excel("DEFINICIONES.xlsx",engine="openpyxl")
    df_triggers=pd.read_excel("TRIGGERS.xlsx",engine="openpyxl")
    df_reportes=pd.read_excel("REPORTES.xlsx",engine="openpyxl")
    df_herramientas=pd.read_excel("HERRAMIENTAS.xlsx",engine="openpyxl")
    for df in [df_gasto_ps,df_calendario,df_ps,df_años,df_definiciones,df_triggers,df_reportes,df_herramientas]:
        df.columns=df.columns.astype(str).str.strip().str.upper()
    df_años["AÑO"]=df_años["AÑO"].astype(str).str.strip()
    df_reportes[["PATRIMONIO","REPORTE"]]=df_reportes[["PATRIMONIO","REPORTE"]].fillna(method="ffill")
    df_herramientas[["PATRIMONIO","REPORTE"]]=df_herramientas[["PATRIMONIO","REPORTE"]].fillna(method="ffill")
    return df_gasto_ps,df_calendario,df_ps,df_años,df_definiciones,df_triggers,df_reportes,df_herramientas


import streamlit as st
import base64
from pathlib import Path

def mostrar_fondo_con_titulo(imagen_path):
    if not Path(imagen_path).is_file():
        st.warning(f"No se encuentra la imagen '{imagen_path}'.")
        return

    with open(imagen_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{img_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            .bloque-titulo {{
                position: absolute;
                top: 60px;
                left: 60px;
                max-width: 950px;
                padding: 2rem 2.5rem;
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 15px;
                color: #1a1a1a;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
                animation: fadein 1.5s ease-in-out;
                font-family: 'Segoe UI', sans-serif;
                z-index: 999;
            }}
            .bloque-titulo h1 {{
                font-size: 2.8rem;
                font-weight: 800;
                margin-bottom: 1rem;
                border-bottom: 2px solid #444;
                padding-bottom: 0.4rem;
            }}
            .bloque-titulo p {{
                font-size: 1.1rem;
                line-height: 1.7;
                text-align: justify;
                margin: 0 0 1.5rem 0;
            }}
            .kpis {{
                display: flex;
                justify-content: space-between;
                margin-top: 1rem;
            }}
            .kpi {{
                text-align: center;
                flex: 1;
            }}
            .kpi .valor {{
                font-size: 2.5rem;
                font-weight: 700;
                color: #b30000;
                margin: 0;
            }}
            .kpi .etiqueta {{
                font-size: 1rem;
                color: #333;
                margin-top: 0.3rem;
            }}
            @keyframes fadein {{
                0% {{ opacity: 0; transform: translateY(-20px); }}
                100% {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>

        <div class="bloque-titulo">
            <h1>EF SECURITIZADORA</h1>
            <p>
                Somos una empresa con más de 20 años de experiencia en la securitización de activos.
                Contamos con equipos de más de 40 años de experiencia acumulada y más de 90 colocaciones de bonos corporativos en Chile desde el año 2003,
                por un monto acumulado superior a UF 200 millones. EF Securitizadora administra actualmente más de 10.000.000 UF en activos,
                con colocaciones de más de 15.000.000 UF.
            </p>

            <!-- KPIs -->
            <div class="kpis">
                <div class="kpi">
                    <p class="valor">20</p>
                    <p class="etiqueta">Años de Experiencia</p>
                </div>
                <div class="kpi">
                    <p class="valor">11</p>
                    <p class="etiqueta">Emisiones de Bonos Securitizados</p>
                </div>
                <div class="kpi">
                    <p class="valor">10&nbsp;mill</p>
                    <p class="etiqueta">UF en Activos Administrados</p>
                </div>
                <div class="kpi">
                    <p class="valor">15&nbsp;mill</p>
                    <p class="etiqueta">UF en Colocaciones Emitidas</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# --- CARGA DE DATOS ---
df_gasto_ps,df_calendario,df_ps,df_años,df_definiciones,df_triggers,df_reportes,df_herramientas=cargar_datos(_files_mtime())


# --- PÁGINAS ---
if st.session_state.pagina == "Inicio":
    mostrar_fondo_con_titulo("Las_Condes_Santiago_Chile.jpeg")

elif st.session_state.pagina == "BI Recaudación":
    st.markdown("""
        <style>
        .titulo-bloque {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 2rem;
            color: #0B1F3A;
            font-weight: bold;
        }
        .stButton > button {
            width: 100%;
            font-size: 1rem;
            padding: 12px;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            background-color: #f0f4f9;
        }
        .stButton > button:hover {
            background-color: #dbe8f5;
            color: #0B1F3A;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="titulo-bloque">Panel de Recaudación</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Recaudación PS10 - HITES"):
            st.session_state.bi_url = "https://app.powerbi.com/view?r=eyJrIjoiZGE0MzNiODYtZGQwOC00NTYwLTk2OWEtZWUwMjlhYzFjNWU2IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"
    with col2:
        if st.button("Recaudación PS11 - ADRETAIL"):
            st.session_state.bi_url = "https://app.powerbi.com/view?r=eyJrIjoiMzQ4OGRhMTQtMThiYi00YjE2LWJlNjUtYTEzNGIyM2FiODA3IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"
    with col3:
        if st.button("Recaudación PS12 - MASISA"):
            st.session_state.bi_url = "https://app.powerbi.com/view?r=eyJrIjoiNmI4NjE3NDktNzY4Yy00OWEwLWE0M2EtN2EzNjQ1NjRhNWQzIiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"
    with col4:
        if st.button("Recaudación PS13 - INCOFIN"):
            st.session_state.bi_url = "https://app.powerbi.com/view?r=eyJrIjoiMTA2OTMyYjYtZDBjNS00YTIyLWFjNmYtMGE0OGQ5YjRmZDMxIiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"

    if "bi_url" in st.session_state:
        st.markdown(f"""
            <iframe title="Power BI"
                    width="100%"
                    height="850"
                    src="{st.session_state.bi_url}"
                    frameborder="0"
                    allowFullScreen="true">
            </iframe>
        """, unsafe_allow_html=True)



# ----- GASTOS -----------

elif st.session_state.pagina == "Gastos":
    st.title("💰 Gastos del Patrimonio")

    # 👉 refresco local
    def _reload():
        return cargar_datos(_files_mtime())

    if st.button("🔄 Recargar archivos de gastos"):
        st.cache_data.clear()
        # recarga inmediata de los dfs que usa esta sección
        df_gasto_ps, df_calendario, df_ps, df_años, df_definiciones, df_triggers, df_reportes, df_herramientas = _reload()
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

#-----DEFINICIONES-----------------------

def mostrar_definiciones():
    st.title("📘 Definiciones Patrimonios Separados")

    def estilo_tabla(df, header_bg="#0d1b2a", header_color="white", max_width="100%"):
        html = (
            f"<style>"
            f".styled-table{{width:{max_width};border-collapse:collapse;font-family:'Segoe UI',sans-serif;font-size:14px;}}"
            f".styled-table thead th{{background-color:{header_bg};color:{header_color};padding:8px;text-align:left;}}"
            f".styled-table td{{padding:8px;border-bottom:1px solid #ddd;text-align:left;}}"
            f".styled-table tr:nth-child(even){{background-color:#f9f9f9;}}"
            f"</style>"
            f"<table class='styled-table'><thead><tr>"
            + "".join(f"<th>{c}</th>" for c in df.columns)
            + "</tr></thead><tbody>"
        )
        for _, row in df.iterrows():
            html += "<tr>" + "".join(f"<td>{row[c]}</td>" for c in df.columns) + "</tr>"
        html += "</tbody></table>"
        return html

    try:
        df_def = pd.read_excel("DEFINICIONES.xlsx", engine="openpyxl")
        df_def.columns = (
            df_def.columns.str.upper().str.normalize("NFKD")
            .str.encode("ascii","ignore").str.decode("utf-8").str.strip()
        )

        col_patrimonio = next((c for c in df_def.columns if "PATRIMONIO" in c), None)
        col_concepto   = next((c for c in df_def.columns if "CONCEPTO"   in c), None)
        col_definicion = next((c for c in df_def.columns if "DEFIN"      in c), None)
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
                # 🚫 sin ordenar, se muestra como viene en el Excel
                df_filtrado = (
                    df_def[df_def[col_patrimonio] == selected][[col_concepto, col_definicion]]
                    .rename(columns={col_concepto: "CONCEPTO", col_definicion: "DEFINICIÓN"})
                    .reset_index(drop=True)
                )
                st.markdown(estilo_tabla(df_filtrado), unsafe_allow_html=True)

                # 📎 Anexos
                with st.expander("📎 Anexos", expanded=False):
                    # --- ANEXOS CRITERIOS ---
                    try:
                        df_criterios = pd.read_excel("ANEXOS CRITERIOS.xlsx", engine="openpyxl")
                        df_criterios.columns = (
                            df_criterios.columns.astype(str).str.upper().str.normalize("NFKD")
                            .str.encode("ascii","ignore").str.decode("utf-8").str.strip()
                        )
                        col_pat_crit = next((c for c in df_criterios.columns if "PATRIMONIO" in c), None)
                        st.markdown("**📄 Criterios por Patrimonio**")
                        if col_pat_crit:
                            dfc = df_criterios[df_criterios[col_pat_crit].astype(str).str.strip().eq(selected)].copy()
                            if dfc.empty:
                                st.info("No hay criterios específicos para este patrimonio. Se muestran criterios generales.")
                                st.markdown(estilo_tabla(df_criterios), unsafe_allow_html=True)
                            else:
                                st.markdown(estilo_tabla(dfc), unsafe_allow_html=True)
                        else:
                            st.markdown(estilo_tabla(df_criterios), unsafe_allow_html=True)
                    except FileNotFoundError:
                        st.warning("No se encontró **ANEXOS CRITERIOS.xlsx**.")
                    except Exception as e:
                        st.error(f"Error al cargar ANEXOS CRITERIOS.xlsx: {e}")

                    st.divider()

                    # --- ANEXO VALORIZACIÓN (solo PS11-ADRETAIL) ---
                    st.markdown("**📄 Anexo Valorización**")
                    if selected != "PS11-ADRETAIL":
                        st.info("Disponible solo para **PS11-ADRETAIL**.")
                    else:
                        try:
                            df_val = pd.read_excel("ANEXO VALORIZACION.xlsx", engine="openpyxl")
                            df_val.columns = (
                                df_val.columns.astype(str).str.upper().str.normalize("NFKD")
                                .str.encode("ascii","ignore").str.decode("utf-8").str.strip()
                            )
                            df_val_show = df_val.copy()

                            # 🎯 Formato %VALORIZACION
                            col_val = next((c for c in df_val_show.columns if "VALORIZACION" in c), None)
                            if col_val:
                                df_val_show[col_val] = pd.to_numeric(df_val_show[col_val], errors="coerce").fillna(0)
                                df_val_show[col_val] = df_val_show[col_val].apply(lambda x: f"{x:.2%}")

                            # 🔎 filtro por CREDITO
                            col_credito = next((c for c in df_val.columns if "CREDITO" in c), None)
                            if col_credito:
                                opciones = ["Todos"] + df_val[col_credito].dropna().astype(str).unique().tolist()
                                elegido = st.selectbox("Filtrar por Crédito:", opciones, key="fil_credito_val")
                                if elegido != "Todos":
                                    df_val_show = df_val_show[df_val[col_credito].astype(str).eq(elegido)].copy()

                            st.markdown(estilo_tabla(df_val_show), unsafe_allow_html=True)
                        except FileNotFoundError:
                            st.warning("No se encontró **ANEXO VALORIZACION.xlsx**.")
                        except Exception as e:
                            st.error(f"Error al cargar ANEXO VALORIZACION.xlsx: {e}")
            else:
                st.warning("⚠️ Por favor, selecciona un Patrimonio para visualizar las definiciones.")

        else:  # Contables
            st.markdown("### 🧾 Definiciones Contables")
            df_filtrado = (
                df_def[df_def[col_patrimonio] == "PS-CONTABLE"][[col_concepto, col_definicion]]
                .rename(columns={col_concepto: "CONCEPTO", col_definicion: "DEFINICIÓN"})
                .reset_index(drop=True)  # 🚫 sin ordenar
            )
            st.markdown(estilo_tabla(df_filtrado, max_width="900px"), unsafe_allow_html=True)

            st.markdown("### 📒 Asientos Contables")
            try:
                df_asientos = pd.read_excel("ASIENTOS.xlsx", engine="openpyxl")
                df_asientos.columns = df_asientos.columns.str.upper().str.strip()
                if not {"GLOSA","CUENTA","DEBE","HABER"}.issubset(df_asientos.columns):
                    st.warning("❗ El archivo ASIENTOS.xlsx no contiene las columnas necesarias.")
                else:
                    df_asientos = df_asientos.fillna({"DEBE":0,"HABER":0})
                    glosas = list(df_asientos["GLOSA"].unique())
                    for i in range(0, len(glosas), 2):
                        cols = st.columns(2)
                        for j in range(2):
                            if i + j < len(glosas):
                                glosa = glosas[i + j]
                                grupo = df_asientos[df_asientos["GLOSA"] == glosa]
                                with cols[j]:
                                    st.markdown(f"#### 📄 {glosa}")
                                    df_as = grupo[["CUENTA","DEBE","HABER"]].copy()
                                    df_as[["DEBE","HABER"]] = df_as[["DEBE","HABER"]].astype(float)
                                    total_debe = df_as["DEBE"].sum()
                                    total_haber = df_as["HABER"].sum()
                                    df_totales = pd.DataFrame([{
                                        "CUENTA": f"Totales {'✅' if total_debe == total_haber else '❌'}",
                                        "DEBE": total_debe, "HABER": total_haber
                                    }])
                                    df_final = pd.concat([df_as, df_totales], ignore_index=True)
                                    df_final["DEBE"]  = df_final["DEBE"].apply(lambda x: f"$ {x:,.0f}".replace(",", ".") if x else "")
                                    df_final["HABER"] = df_final["HABER"].apply(lambda x: f"$ {x:,.0f}".replace(",", ".") if x else "")
                                    st.markdown(estilo_tabla(df_final, max_width="100%"), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error al procesar los asientos contables: {e}")
    except Exception as e:
        st.error(f"❌ Error general al cargar definiciones: {e}")



# llamado desde navegación (fuera de la función)
if st.session_state.pagina=="Definiciones": mostrar_definiciones()


# ----- REPORTES-----------

elif st.session_state.pagina == "Reportes":
    st.title("📋 Reportes por Patrimonio Separado")

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

# --- SECCIÓN SEGUIMIENTO MEJORADA ---
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

    st.markdown("### 1️⃣ Selecciona el Patrimonio")
    patrimonios = sorted(df_seg["PATRIMONIO"].dropna().unique())
    patrimonio = st.selectbox("Patrimonio:", ["- Selecciona -"] + patrimonios)
    if patrimonio == "- Selecciona -":
        st.warning("⚠️ Por favor, selecciona un patrimonio para continuar.")
        st.stop()

    st.markdown("### 2️⃣ Selecciona el Mes")
    meses = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
        "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
        "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }
    mes_nombre = st.selectbox("Mes:", ["- Selecciona -"] + list(meses.keys()))
    if mes_nombre == "- Selecciona -":
        st.warning("⚠️ Selecciona un mes válido para continuar.")
        st.stop()

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

    st.markdown("### 3️⃣ Selecciona la Fecha de Cesión")
    fecha = st.selectbox("Fecha de Cesión:", opciones_fechas)
    if fecha == "- Selecciona -":
        st.warning("⚠️ Selecciona una fecha válida para continuar.")
        st.stop()

    if fecha == "📂 Todas las Cesiones del Mes":
        registros_mes = []
        for clave, lista in st.session_state.estado_actual.items():
            try:
                clave_pat, clave_fecha = clave.split("|")
                fecha_obj = datetime.strptime(clave_fecha, "%Y-%m-%d")
                if clave_pat == patrimonio and fecha_obj.month == mes:
                    registros_mes.extend([{**reg, "FECHA": clave_fecha, "ORDEN": idx} for idx, reg in enumerate(lista)])
            except Exception:
                continue

        if registros_mes:
            st.markdown("### 📂 Vista consolidada del mes")
            registros_ordenados = sorted(registros_mes, key=lambda r: (r["FECHA"], r["ORDEN"]))
            fechas_unicas = sorted(set(r["FECHA"] for r in registros_ordenados))

            for cesion_fecha in fechas_unicas:
                st.markdown(f"#### 📂 Cesión del {cesion_fecha}")
                for idx, reg in enumerate([r for r in registros_ordenados if r["FECHA"] == cesion_fecha], 1):
                    color_fondo = {
                        "REALIZADO": "#C6EFCE",
                        "PENDIENTE": "#FFF2CC",
                        "ATRASADO": "#F8CBAD"
                    }.get(reg["ESTADO"], "#FFF2CC")
                    st.markdown(f"""
                        <div style='background-color: {color_fondo}; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;'>
                            <p style='font-weight: bold;'>🧹 #{idx} - {reg['HITO']}</p>
                            <p><strong>Responsable:</strong> {reg['RESPONSABLE']}</p>
                            <p><strong>Estado:</strong> {reg['ESTADO']}</p>
                            <p><strong>Comentario:</strong> <em>{reg['COMENTARIO'] or '(Sin comentario)'}</em></p>
                        </div>
                    """, unsafe_allow_html=True)

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

    fecha_str = fecha.strftime("%Y-%m-%d")
    key_estado = f"{patrimonio}|{fecha_str}"
    if key_estado not in st.session_state.estado_actual:
        df_base = df_seg[df_seg["PATRIMONIO"] == patrimonio][["HITOS", "RESPONSABLE"]].copy()
        registros_base = []
        for _, row in df_base.iterrows():
            registros_base.append({"HITO": row["HITOS"], "RESPONSABLE": row["RESPONSABLE"], "ESTADO": "PENDIENTE", "COMENTARIO": ""})
        st.session_state.estado_actual[key_estado] = registros_base

    registros = st.session_state.estado_actual[key_estado]
    st.markdown("### Estado actual de la cesión")
    for idx, reg in enumerate(registros, 1):
        color_fondo = {
            "REALIZADO": "#C6EFCE",
            "PENDIENTE": "#FFF2CC",
            "ATRASADO": "#F8CBAD"
        }.get(reg["ESTADO"], "#FFF2CC")
        st.markdown(f"""
            <div style='background-color: {color_fondo}; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;'>
                <p style='font-weight: bold;'>🧩 #{idx} - {reg['HITO']}</p>
                <p><strong>Responsable:</strong> {reg['RESPONSABLE']}</p>
                <p><strong>Estado:</strong> {reg['ESTADO']}</p>
                <p><strong>Comentario:</strong> <em>{reg['COMENTARIO'] or '(Sin comentario)'}</em></p>
            </div>
        """, unsafe_allow_html=True)

    usuario_actual = st.session_state.get("usuario", "").lower()
    if usuario_actual in ["nvega@efsecuritizadora.cl", "jsepulveda@efsecuritizadora.cl"]:
        st.markdown("### ✏️ Modificar Estado de Cesión")
        nuevos_registros = []
        for i, reg in enumerate(registros):
            st.markdown(f"<div style='margin-top:1.2rem;'><strong>🧩 {reg['HITO']}</strong></div>", unsafe_allow_html=True)
            cols = st.columns([1, 3])
            with cols[0]:
                nuevo_estado = st.selectbox("Estado", ["PENDIENTE", "REALIZADO", "ATRASADO"], index=["PENDIENTE", "REALIZADO", "ATRASADO"].index(reg["ESTADO"]), key=f"estado_{i}")
            with cols[1]:
                nuevo_comentario = st.text_input("Comentario", value=reg["COMENTARIO"], key=f"comentario_{i}")
            nuevos_registros.append({"HITO": reg["HITO"], "RESPONSABLE": reg["RESPONSABLE"], "ESTADO": nuevo_estado, "COMENTARIO": nuevo_comentario})

        if st.button("💾 Guardar cambios"):
            st.session_state.estado_actual[key_estado] = nuevos_registros
            with open("seguimiento_guardado.json", "w", encoding="utf-8") as f:
               json.dump(st.session_state.estado_actual, f, ensure_ascii=False, indent=2)
            st.success("✅ Cambios guardados correctamente.")
            st.stop()


        df_actualizado = pd.DataFrame(nuevos_registros)[["HITO", "RESPONSABLE", "ESTADO", "COMENTARIO"]]
        df_actualizado.insert(0, "FECHA", fecha_str)
        df_actualizado.insert(1, "PATRIMONIO", patrimonio)
        nombre_excel_actual = f"seguimiento_excel/SEGUIMIENTO_EDITABLE_{patrimonio.replace('-', '')}_{fecha_str}.xlsx"
        Path("seguimiento_excel").mkdir(exist_ok=True)
        df_actualizado.to_excel(nombre_excel_actual, index=False)
        with open(nombre_excel_actual, "rb") as f:
            st.download_button(
                label="📥 Descargar Excel editable actualizado",
                data=f,
                file_name=os.path.basename(nombre_excel_actual),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

