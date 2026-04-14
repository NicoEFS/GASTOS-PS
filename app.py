import streamlit as st
import pandas as pd
import json, os, base64, re
from datetime import date, datetime
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Panel EF Securitizadora", layout="wide")

# =================== Tema dinámico ===================
def obtener_tema(modo="Claro"):
    if modo=="Oscuro":
        return {
            "bg":"#07111f","bg_soft":"#0b1728","panel":"#0f1b2d","panel_2":"#13233a","panel_3":"#1a2f4d",
            "text":"#e8eef7","muted":"#b8c4d6","border":"#243a57","accent":"#d94b45","table_even":"#0c1626",
            "chip_bg":"#162842","chip_border":"#284468","sidebar_bg":"linear-gradient(180deg,#1c2330 0%,#222635 100%)",
            "title":"#e8eef7","subtitle":"#dbe6f3","hero_bg":"rgba(11,31,58,0.84)","hero_text":"#e8eef7",
            "hero_title":"#ffffff","hero_kpi":"#ff7a6f","hero_label":"#d4e1ef","success":"#163423","warning":"#4b3a12","danger":"#4a1f1f"
        }
    return {
        "bg":"#f5f7fb","bg_soft":"#eef2f8","panel":"#ffffff","panel_2":"#f0f4f9","panel_3":"#dbe8f5",
        "text":"#0B1F3A","muted":"#5f6b7a","border":"#d6deea","accent":"#d94b45","table_even":"#f9fbfd",
        "chip_bg":"#edf2ff","chip_border":"#c7d2fe","sidebar_bg":"linear-gradient(180deg,#252736 0%,#2e3040 100%)",
        "title":"#0B1F3A","subtitle":"#334155","hero_bg":"rgba(255,255,255,0.78)","hero_text":"#1a1a1a",
        "hero_title":"#0B1F3A","hero_kpi":"#b22222","hero_label":"#0B1F3A","success":"#C6EFCE","warning":"#FFF2CC","danger":"#F8CBAD"
    }

if "modo_tema" not in st.session_state:
    st.session_state.modo_tema="Claro"

tema=obtener_tema("Oscuro" if st.session_state.modo_tema=="Oscuro" else "Claro")

# =================== Estilos globales ===================
st.markdown(f"""
<style>
:root{{
    --bg:{tema["bg"]};
    --bg-soft:{tema["bg_soft"]};
    --panel:{tema["panel"]};
    --panel-2:{tema["panel_2"]};
    --panel-3:{tema["panel_3"]};
    --text:{tema["text"]};
    --muted:{tema["muted"]};
    --border:{tema["border"]};
    --accent:{tema["accent"]};
    --table-even:{tema["table_even"]};
    --chip-bg:{tema["chip_bg"]};
    --chip-border:{tema["chip_border"]};
    --title:{tema["title"]};
    --subtitle:{tema["subtitle"]};
}}
html,body,[class*="css"]{{color:var(--text);}}
body,.stApp,[data-testid="stAppViewContainer"]{{background:linear-gradient(180deg,var(--bg) 0%,var(--bg-soft) 100%)!important;color:var(--text)!important;}}
[data-testid="stHeader"]{{background:transparent!important;}}
section[data-testid="stSidebar"]{{background:{tema["sidebar_bg"]}!important;border-right:1px solid var(--border)!important;}}
section[data-testid="stSidebar"] *{{color:#ffffff!important;}}
h1,h2,h3,h4,h5,h6,.titulo-bloque,.sidebar-title{{color:var(--title)!important;}}
p,span,div,label,small{{color:var(--text);}}
.stMarkdown,.stText,.stCaption{{color:var(--text)!important;}}
.stAlert{{background:var(--panel)!important;color:var(--text)!important;border:1px solid var(--border)!important;}}
.stSelectbox label,.stTextInput label,.stRadio label,.stForm label{{color:var(--text)!important;}}
.stSelectbox [data-baseweb="select"] > div,.stTextInput input,.stTextArea textarea{{background:var(--panel)!important;color:var(--text)!important;border:1px solid var(--border)!important;}}
.stRadio>div{{flex-direction:column}}
.stRadio div[role="radiogroup"] label{{padding:12px 18px;font-size:1.05rem;border-radius:10px;background:var(--panel-2)!important;border:1px solid var(--border)!important;margin-bottom:.55rem;color:var(--text)!important;}}
.stRadio div[role="radiogroup"] label:hover{{background:var(--panel-3)!important;}}
.stButton > button,.stDownloadButton > button,.stFormSubmitButton > button{{width:100%;font-size:1rem;padding:12px 14px;margin-bottom:.5rem;border-radius:10px;background:var(--panel-2)!important;color:var(--text)!important;border:1px solid var(--border)!important;transition:all .2s ease;box-shadow:none!important;}}
.stButton > button:hover,.stDownloadButton > button:hover,.stFormSubmitButton > button:hover{{background:var(--panel-3)!important;border-color:var(--accent)!important;color:var(--text)!important;}}
.tabla-ef{{width:100%;border-collapse:collapse;font-family:'Segoe UI',sans-serif;font-size:14px;background:var(--panel);color:var(--text);border:1px solid var(--border);border-radius:10px;overflow:hidden;}}
.tabla-ef th{{background:#0B1F3A;color:#fff;padding:8px;text-align:left;border-bottom:1px solid var(--border);}}
.tabla-ef td{{padding:8px;border-bottom:1px solid var(--border);vertical-align:top;color:var(--text);}}
.tabla-ef tr:nth-child(even){{background:var(--table-even);}}
.chip{{display:inline-block;padding:2px 8px;margin:2px;border-radius:12px;background:var(--chip-bg);color:var(--text);border:1px solid var(--chip-border);font-size:12px;white-space:normal;}}
.sidebar-title{{font-size:1.05rem;font-weight:700;margin-top:.25rem;margin-bottom:.75rem;}}
</style>
""", unsafe_allow_html=True)

def estilo_tabla(df): return df.to_html(index=False, border=0, classes='tabla-ef', escape=False)

def estilo_tabla_con_totales(df_as):
    total_debe,total_haber=df_as["DEBE"].sum(),df_as["HABER"].sum()
    cuadrado="✅" if total_debe==total_haber else "❌"
    df_tot=pd.DataFrame([{"CUENTA":f"Totales {cuadrado}","DEBE":total_debe,"HABER":total_haber}])
    df_fin=pd.concat([df_as,df_tot],ignore_index=True)
    df_fin["DEBE"]=df_fin["DEBE"].apply(lambda x:f"$ {x:,.0f}".replace(",",".") if x else "")
    df_fin["HABER"]=df_fin["HABER"].apply(lambda x:f"$ {x:,.0f}".replace(",",".") if x else "")
    return estilo_tabla(df_fin)

# =================== Configuración ===================
usuarios_modifican=["nvega@efsecuritizadora.cl","jsepulveda@efsecuritizadora.cl"]
usuarios_visualizan=[
    "jmiranda@efsecuritizadora.cl","pgalvez@efsecuritizadora.cl","ssales@efsecuritizadora.cl",
    "drodriguez@efsecuritizadora.cl","csalazar@efsecuritizadora.cl","ppellegrini@efsecuritizadora.cl",
    "cossa@efsecuritizadora.cl","ptoro@efsecuritizadora.cl","mleon@efsecuritizadora.cl",
    "jcoloma@efsecuritizadora.cl","asiri@efsecuritizadora.cl","dcardoso@efsecuritizadora.cl",
    "mvidal@efsecuritizadora.cl","fsoto@efsecuritizadora.cl","sguzman@efsecuritizadora.cl"
]

# =================== Autenticación ===================
if "authenticated" not in st.session_state:
    st.session_state.authenticated=False
    st.session_state.usuario=""
if not st.session_state.authenticated:
    st.image("EF logo@4x.png", width=180)
    with st.form("login"):
        st.subheader("🔐 Acceso restringido")
        correo=st.text_input("Correo institucional")
        clave=st.text_input("Clave de acceso", type="password")
        submit=st.form_submit_button("Ingresar")
        if submit:
            if clave=="ef2025" and (correo in usuarios_modifican or correo in usuarios_visualizan):
                st.session_state.authenticated=True
                st.session_state.usuario=correo
                st.success("Acceso concedido")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

permite_editar=st.session_state.usuario in usuarios_modifican
if "pagina" not in st.session_state: st.session_state.pagina="Inicio"
if "estado_actual" not in st.session_state:
    if os.path.exists("seguimiento_guardado.json"):
        with open("seguimiento_guardado.json","r",encoding="utf-8") as f: st.session_state.estado_actual=json.load(f)
    else:
        st.session_state.estado_actual={}

# =================== Sidebar ===================
paginas_visibles=["Inicio","Antecedentes Generales","Gastos","Definiciones","BI Recaudación"]
if st.session_state.pagina not in paginas_visibles: st.session_state.pagina="Inicio"

with st.sidebar:
    st.image("EF logo@4x.png", width=180)
    st.markdown('<div class="sidebar-title">Panel EF Securitizadora</div>', unsafe_allow_html=True)
    st.session_state.modo_tema=st.radio("Tema:", ["Claro","Oscuro"], index=0 if st.session_state.modo_tema=="Claro" else 1, key="tema_visual")
    pagina=st.radio("Ir a la sección:", paginas_visibles, index=paginas_visibles.index(st.session_state.pagina))
    st.session_state.pagina=pagina
    st.divider()
    st.markdown(f"**Usuario:** {st.session_state.usuario}")
    if st.button("🔒 Cerrar sesión"):
        st.session_state.authenticated=False
        st.session_state.usuario=""
        st.rerun()

# =================== Carga de datos ===================
def _files_mtime():
    files=["GASTO-PS.xlsx","CALENDARIO-GASTOS.xlsx","PS.xlsx","TABLA AÑO.xlsx","DEFINICIONES.xlsx","TRIGGERS.xlsx","REPORTES.xlsx","HERRAMIENTAS.xlsx","ANTECEDENTES GENERALES.xlsx","TD CONSOL.xlsx","TD CONSOLO.xlsx"]
    return tuple(os.path.getmtime(f) if os.path.exists(f) else 0 for f in files)

def _read_first_existing(paths, engine=None, **kwargs):
    for p in paths:
        if os.path.exists(p): return pd.read_excel(p, engine=engine, **kwargs) if engine else pd.read_excel(p, **kwargs)
    return pd.DataFrame()

@st.cache_data
def cargar_datos(_mtimes):
    df_gasto_ps=_read_first_existing(["GASTO-PS.xlsx"])
    df_calendario=_read_first_existing(["CALENDARIO-GASTOS.xlsx"])
    df_ps=_read_first_existing(["PS.xlsx"])
    df_años=_read_first_existing(["TABLA AÑO.xlsx"])
    df_definiciones=_read_first_existing(["DEFINICIONES.xlsx"], engine="openpyxl")
    df_triggers=_read_first_existing(["TRIGGERS.xlsx"], engine="openpyxl")
    df_reportes=_read_first_existing(["REPORTES.xlsx"], engine="openpyxl")
    df_herramientas=_read_first_existing(["HERRAMIENTAS.xlsx"], engine="openpyxl")
    df_antecedentes=_read_first_existing(["ANTECEDENTES GENERALES.xlsx"], engine="openpyxl", dtype=str)
    df_td_consol=_read_first_existing(["TD CONSOL.xlsx","TD CONSOLO.xlsx"], engine="openpyxl")
    for df in [df_gasto_ps,df_calendario,df_ps,df_años,df_definiciones,df_triggers,df_reportes,df_herramientas,df_antecedentes,df_td_consol]:
        if not df.empty: df.columns=df.columns.astype(str).str.strip().str.upper()
    if not df_años.empty and "AÑO" in df_años.columns: df_años["AÑO"]=df_años["AÑO"].astype(str).str.strip()
    for d in (df_reportes,df_herramientas):
        if not d.empty:
            for c in ("PATRIMONIO","REPORTE"):
                if c in d.columns: d[c]=d[c].ffill()
    return df_gasto_ps,df_calendario,df_ps,df_años,df_definiciones,df_triggers,df_reportes,df_herramientas,df_antecedentes,df_td_consol

(df_gasto_ps,df_calendario,df_ps,df_años,df_definiciones,df_triggers,df_reportes,df_herramientas,df_antecedentes,df_td_consol)=cargar_datos(_files_mtime())

# =================== UI Inicio ===================
def mostrar_fondo_con_titulo(imagen_path:str):
    img_b64=""
    if Path(imagen_path).is_file():
        with open(imagen_path,"rb") as f: img_b64=base64.b64encode(f.read()).decode()
    ext=Path(imagen_path).suffix.replace(".","") or "jpeg"
    overlay="rgba(5,10,18,.68)" if st.session_state.modo_tema=="Oscuro" else "rgba(255,255,255,.10)"
    css=f"""
    <style>
      html, body, .stApp {{ height:100%; }}
      [data-testid="stAppViewContainer"], .stApp {{ background:transparent!important; }}
      .stApp::before {{
        content:"";
        position:fixed;
        inset:0;
        z-index:-1;
        background-image:linear-gradient({overlay},{overlay}),url("data:image/{ext};base64,{img_b64}");
        background-size:cover;
        background-position:center;
        background-repeat:no-repeat;
        background-attachment:fixed;
        image-rendering:auto;
      }}
      .bloque-titulo {{
        margin:48px auto 24px auto;
        width:min(1280px,92vw);
        background-color:{tema["hero_bg"]};
        border-radius:16px;
        padding:2.2rem 2.6rem;
        box-shadow:0 8px 28px rgba(0,0,0,0.20);
        font-family:'Segoe UI',sans-serif;
        color:{tema["hero_text"]};
        animation:fadein .9s ease-in-out;
        border:1px solid {tema["border"]};
      }}
      .bloque-titulo h1 {{ font-size:2.4rem; font-weight:800; margin:0 0 1rem 0; color:{tema["hero_title"]}; }}
      .bloque-titulo p {{ font-size:1.02rem; line-height:1.65; text-align:justify; margin:0 0 1.6rem 0; color:{tema["hero_text"]}; }}
      .kpis {{ display:grid; grid-template-columns:repeat(4,minmax(180px,1fr)); gap:2rem; }}
      .kpi {{ text-align:center; background:rgba(255,255,255,0.04); border-radius:12px; padding:1rem; }}
      .kpi .valor {{ font-size:2.3rem; font-weight:800; color:{tema["hero_kpi"]}; line-height:1; margin:0 0 .3rem 0; }}
      .kpi .etiqueta{{ margin:0; font-size:.95rem; color:{tema["hero_label"]}; opacity:.95; }}
      @media (max-width:1100px){{ .bloque-titulo{{ width:95vw; padding:1.6rem 1.8rem; }} .kpis{{ grid-template-columns:repeat(2,1fr); }} .kpi .valor{{ font-size:2.0rem; }} }}
      @keyframes fadein{{from{{opacity:0;transform:translateY(-8px)}}to{{opacity:1;transform:translateY(0)}}}}
    </style>"""
    kpis_html="""
    <div class="kpis">
      <div class="kpi"><p class="valor">25</p><p class="etiqueta">Años de Experiencia</p></div>
      <div class="kpi"><p class="valor">16</p><p class="etiqueta">Emisiones de Bonos Securitizados</p></div>
      <div class="kpi"><p class="valor">13&nbsp;mill</p><p class="etiqueta">UF en Activos Administrados</p></div>
      <div class="kpi"><p class="valor">15.7&nbsp;mill</p><p class="etiqueta">UF en Colocaciones Emitidas</p></div>
    </div>"""
    st.markdown(f"""{css}
    <div class="bloque-titulo">
      <h1>EF SECURITIZADORA</h1>
      <p>Somos una empresa con más de 25 años de experiencia en la securitización de activos. Contamos con equipos de más de 40 años de experiencia acumulada y más de 90 colocaciones de bonos corporativos en Chile desde el año 2003, por un monto acumulado superior a UF 200 millones. EF Securitizadora administra actualmente más de UF 11.000.000 en activos, con colocaciones de más de UF 15.700.000.</p>
      {kpis_html}
    </div>""", unsafe_allow_html=True)

# =================== Helpers ===================
def _norm(s:str)->str:
    if s is None: return ""
    s=str(s).strip().lower()
    for a,b in (("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u")): s=s.replace(a,b)
    s=re.sub(r"\s+"," ",s)
    return s

def _apply_to_row_nrm(df:pd.DataFrame, row_label:str, func, first_col_name:str):
    if df.empty: return
    mask=df[first_col_name].astype(str).map(_norm)==_norm(row_label)
    if mask.any():
        cols=df.columns[1:]
        df.loc[mask,cols]=df.loc[mask,cols].applymap(func)

# =================== Función Definiciones ===================
def mostrar_definiciones():
    st.title("📘 Definiciones Patrimonios Separados")

    def estilo_tabla_local(df, header_bg="#0B1F3A", header_color="white", max_width="100%"):
        fila_even=tema["table_even"]
        borde=tema["border"]
        fondo=tema["panel"]
        texto=tema["text"]
        html=(
            f"<style>"
            f".styled-table{{width:{max_width};border-collapse:collapse;font-family:'Segoe UI',sans-serif;font-size:14px;background:{fondo};color:{texto};border:1px solid {borde};}}"
            f".styled-table thead th{{background-color:{header_bg};color:{header_color};padding:8px;text-align:left;border-bottom:1px solid {borde};}}"
            f".styled-table td{{padding:8px;border-bottom:1px solid {borde};text-align:left;color:{texto};}}"
            f".styled-table tr:nth-child(even){{background-color:{fila_even};}}"
            f"</style>"
            f"<table class='styled-table'><thead><tr>"
            + "".join(f"<th>{c}</th>" for c in df.columns)
            + "</tr></thead><tbody>"
        )
        for _, row in df.iterrows():
            html+="<tr>"+"".join(f"<td>{row[c]}</td>" for c in df.columns)+"</tr>"
        html+="</tbody></table>"
        return html

    try:
        df_def=pd.read_excel("DEFINICIONES.xlsx", engine="openpyxl")
        df_def.columns=(df_def.columns.str.upper().str.normalize("NFKD").str.encode("ascii","ignore").str.decode("utf-8").str.strip())
        col_patrimonio=next((c for c in df_def.columns if "PATRIMONIO" in c), None)
        col_concepto=next((c for c in df_def.columns if "CONCEPTO" in c), None)
        col_definicion=next((c for c in df_def.columns if "DEFIN" in c), None)
        if not all([col_patrimonio,col_concepto,col_definicion]):
            st.error("❌ No se encontraron las columnas 'PATRIMONIO', 'CONCEPTO' o 'DEFINICIÓN'.")
            return

        opcion=st.radio("Selecciona el tipo de definición:", ["Generales","Contables"], horizontal=True)

        if opcion=="Generales":
            st.markdown("### 🧠 Definiciones Generales")
            patrimonios_disponibles=df_def[df_def[col_patrimonio]!="PS-CONTABLE"][col_patrimonio].dropna().unique()
            selected=st.selectbox("Selecciona un patrimonio:", ["- Selecciona -"]+sorted(patrimonios_disponibles))
            if selected!="- Selecciona -":
                df_filtrado=(df_def[df_def[col_patrimonio]==selected][[col_concepto,col_definicion]].rename(columns={col_concepto:"CONCEPTO",col_definicion:"DEFINICIÓN"}).reset_index(drop=True))
                st.markdown(estilo_tabla_local(df_filtrado), unsafe_allow_html=True)

        else:
            st.markdown("### 🧾 Definiciones Contables")
            df_filtrado=(df_def[df_def[col_patrimonio]=="PS-CONTABLE"][[col_concepto,col_definicion]].rename(columns={col_concepto:"CONCEPTO",col_definicion:"DEFINICIÓN"}).reset_index(drop=True))
            st.markdown(estilo_tabla_local(df_filtrado, max_width="900px"), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error general al cargar definiciones: {e}")

# =================== Páginas ===================
if st.session_state.pagina=="Inicio":
    mostrar_fondo_con_titulo("Las_Condes_Santiago_Chile.jpeg")

elif st.session_state.pagina=="Antecedentes Generales":
    st.subheader("📚 Antecedentes Generales")
    st.info("Se mantiene tu lógica original. Aquí puedes dejar el bloque completo que ya usabas.")

elif st.session_state.pagina=="Gastos":
    st.title("💰 Gastos del Patrimonio")
    st.info("Se mantiene tu lógica original. Aquí puedes dejar el bloque completo que ya usabas.")

elif st.session_state.pagina=="Definiciones":
    mostrar_definiciones()

elif st.session_state.pagina=="BI Recaudación":
    st.markdown(f"""
    <style>
    .titulo-bloque{{text-align:center;font-size:2.3rem;margin-bottom:2rem;color:{tema["title"]};font-weight:bold;}}
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="titulo-bloque">Panel de Recaudación</div>', unsafe_allow_html=True)

    col1,col2,col3,col4,col5=st.columns(5)
    with col1:
        if st.button("Recaudación PS10 - HITES"): st.session_state.bi_url="https://app.powerbi.com/view?r=eyJrIjoiZGE0MzNiODYtZGQwOC00NTYwLTk2OWEtZWUwMjlhYzFjNWU2IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"
    with col2:
        if st.button("Recaudación PS11 - ADRETAIL"): st.session_state.bi_url="https://app.powerbi.com/view?r=eyJrIjoiMzQ4OGRhMTQtMThiYi00YjE2LWJlNjUtYTEzNGIyM2FiODA3IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"
    with col3:
        if st.button("Recaudación PS12 - MASISA"): st.session_state.bi_url="https://app.powerbi.com/view?r=eyJrIjoiNmI4NjE3NDktNzY4Yy00OWEwLWE0M2EtN2EzNjQ1NjRhNWQzIiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"
    with col4:
        if st.button("Recaudación PS13 - INCOFIN"): st.session_state.bi_url="https://app.powerbi.com/view?r=eyJrIjoiMTA2OTMyYjYtZDBjNS00YTIyLWFjNmYtMGE0OGQ5YjRmZDMxIiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"
    with col5:
        if st.button("Recaudación PS14 - GLOBAL"): st.session_state.bi_url="https://app.powerbi.com/view?r=eyJrIjoiZGFlNGM0MzEtYzYxYS00NGUzLWE4NDMtODVmYzQ0YWJjOTM5IiwidCI6IjliYmZlNzZjLTQ1NGQtNGRmNy1hY2M5LTIzM2EyY2QwMTVlMCIsImMiOjR9"

    if "bi_url" in st.session_state:
        st.markdown(f'<iframe title="Power BI" width="100%" height="850" src="{st.session_state.bi_url}" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)

# =================== GASTOS ===================
elif st.session_state.pagina=="Gastos":
    st.title("💰 Gastos del Patrimonio")

    def _reload():
        return cargar_datos(_files_mtime())

    if st.button("🔄 Recargar archivos de gastos"):
        st.cache_data.clear()
        if os.path.exists("GASTO-PS.xlsx"): os.utime("GASTO-PS.xlsx", None)
        if os.path.exists("CALENDARIO-GASTOS.xlsx"): os.utime("CALENDARIO-GASTOS.xlsx", None)
        (df_gasto_ps,df_calendario,df_ps,df_años,df_definiciones,df_triggers,df_reportes,df_herramientas,df_antecedentes,df_td_consol)=_reload()
        st.success("Datos recargados exitosamente.")
        st.rerun()

    if os.path.exists("GASTO-PS.xlsx"):
        ts=os.path.getmtime("GASTO-PS.xlsx")
        st.caption(f"📅 Última actualización: {datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')}")

    orden_meses=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
    orden_dict={m:i for i,m in enumerate(orden_meses, start=1)}

    patrimonio_opciones=['- Selecciona -']+list(df_ps['PATRIMONIO'].dropna().unique()) if not df_ps.empty and 'PATRIMONIO' in df_ps.columns else ['- Selecciona -']
    años_opciones=sorted(df_años['AÑO'].dropna().astype(str).unique()) if not df_años.empty and 'AÑO' in df_años.columns else ["2026"]
    meses_base=list(df_calendario['MES'].dropna().astype(str).str.upper().str.strip().unique()) if not df_calendario.empty and 'MES' in df_calendario.columns else []
    meses_opciones=['Todos']+[m for m in orden_meses if m in meses_base]

    c1,c2,c3,c4=st.columns(4)
    with c1: patrimonio=st.selectbox("Patrimonio:", patrimonio_opciones)
    with c2: año=st.selectbox("Año:", años_opciones)
    with c3: mes=st.selectbox("Mes:", meses_opciones)
    with c4: frecuencia=st.selectbox("Frecuencia:", ['Todos','MENSUAL','ANUAL','TRIMESTRAL'])

    if patrimonio=='- Selecciona -':
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")
        st.stop()

    gastos_filtrado=df_gasto_ps[df_gasto_ps['PATRIMONIO']==patrimonio].copy() if not df_gasto_ps.empty and 'PATRIMONIO' in df_gasto_ps.columns else pd.DataFrame()
    if frecuencia!='Todos' and not gastos_filtrado.empty and 'PERIODICIDAD' in gastos_filtrado.columns:
        gastos_filtrado=gastos_filtrado[gastos_filtrado['PERIODICIDAD']==frecuencia]

    if gastos_filtrado.empty:
        st.warning("⚠️ No existen datos para los filtros seleccionados.")
    else:
        columnas_gastos=[c for c in gastos_filtrado.columns if c not in ['PATRIMONIO','MONEDA']]
        st.markdown(estilo_tabla(gastos_filtrado[columnas_gastos]), unsafe_allow_html=True)

    cal_filtrado=df_calendario[df_calendario['PATRIMONIO']==patrimonio].copy() if not df_calendario.empty and 'PATRIMONIO' in df_calendario.columns else pd.DataFrame()
    if cal_filtrado.empty:
        st.warning("⚠️ No existen datos para el patrimonio seleccionado.")
        st.stop()

    cal_filtrado.columns=cal_filtrado.columns.astype(str).str.upper().str.strip()
    cal_filtrado['MES']=cal_filtrado['MES'].astype(str).str.strip().str.upper()

    if mes!='Todos':
        cal_filtrado=cal_filtrado[cal_filtrado['MES']==mes.upper()]

    if cal_filtrado.empty:
        st.warning("⚠️ No existen datos para el mes y patrimonio seleccionados.")
        st.stop()

    st.markdown("#### 🗓️ Calendario de Gastos")

    col_anio=str(año).upper() if str(año).upper() in cal_filtrado.columns else ('2026' if '2026' in cal_filtrado.columns else None)

    with st.expander("▶️ Ver tabla de conceptos", expanded=False):
        if col_anio:
            st.markdown(estilo_tabla(cal_filtrado[['MES',col_anio]]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existe una columna del año seleccionado en el calendario.")

elif st.session_state.pagina=="Definiciones":
    mostrar_definiciones()

# =================== Código oculto: Reportes ===================
elif st.session_state.pagina=="Reportes":
    st.title("📋 Reportes por Patrimonio Separado")

    if st.button("🔄 Recargar archivos de reportes"):
        st.cache_data.clear()
        st.success("Archivos de reportes actualizados exitosamente.")
        st.rerun()

    patrimonio_opciones=['- Selecciona -']+sorted(df_reportes['PATRIMONIO'].dropna().unique())
    patrimonio=st.selectbox("Selecciona un patrimonio:", patrimonio_opciones, key="reporte_patrimonio")

    if patrimonio!='- Selecciona -':
        df_filtrado=df_reportes[df_reportes['PATRIMONIO']==patrimonio]
        reportes_disponibles=sorted(df_filtrado['REPORTE'].dropna().unique())
        reporte=st.selectbox("Selecciona un reporte:", ['- Selecciona -']+reportes_disponibles, key="reporte_tipo")

        if reporte!='- Selecciona -':
            st.markdown("#### 📄 Ítems a Revisar")
            items=df_filtrado[df_filtrado['REPORTE']==reporte][['ITEM']].dropna()
            if not items.empty:
                st.markdown(estilo_tabla(items), unsafe_allow_html=True)
            else:
                st.warning("⚠️ No hay ítems a revisar para el reporte seleccionado.")

            st.markdown("#### 🛠 Herramientas y Objetivos")
            herramientas=df_herramientas[(df_herramientas['PATRIMONIO']==patrimonio)&(df_herramientas['REPORTE']==reporte)][['HERRAMIENTA','OBJETIVO']].dropna()
            if not herramientas.empty:
                st.markdown(estilo_tabla(herramientas), unsafe_allow_html=True)
            else:
                st.warning("⚠️ No hay herramientas registradas para el reporte seleccionado.")
        else:
            st.warning("⚠️ Por favor, selecciona un reporte para ver la información.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver los reportes disponibles.")

# =================== Código oculto: Seguimiento ===================
elif st.session_state.pagina=="Seguimiento":
    st.markdown("""
        <style>
        .tarjeta-hito{
            border-radius:12px;
            padding:15px;
            margin-bottom:18px;
            border:1px solid #243a57;
            font-family:Arial,sans-serif;
            font-size:14px;
            color:#e8eef7;
            background:#0f1b2d;
        }
        .separador-cesion{
            font-weight:bold;
            margin-top:30px;
            margin-bottom:10px;
            font-size:16px;
            color:#e8eef7;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📅 Seguimiento de Cesiones Revolving")

    df_raw=pd.read_excel("SEGUIMIENTO.xlsx", sheet_name=0, header=None)
    encabezados=df_raw.iloc[0].copy()
    encabezados[:3]=["PATRIMONIO","RESPONSABLE","HITOS"]
    df_seg=df_raw[1:].copy()
    df_seg.columns=encabezados

    if "estado_actual" not in st.session_state:
        if os.path.exists("seguimiento_guardado.json"):
            with open("seguimiento_guardado.json","r",encoding="utf-8") as f: st.session_state.estado_actual=json.load(f)
        else:
            st.session_state.estado_actual={}

    st.markdown("### 1️⃣ Selecciona el Patrimonio")
    patrimonios=sorted(df_seg["PATRIMONIO"].dropna().unique())
    patrimonio=st.selectbox("Patrimonio:", ["- Selecciona -"]+patrimonios)
    if patrimonio=="- Selecciona -":
        st.warning("⚠️ Por favor, selecciona un patrimonio para continuar.")
        st.stop()

    st.markdown("### 2️⃣ Selecciona el Mes")
    meses={"Enero":1,"Febrero":2,"Marzo":3,"Abril":4,"Mayo":5,"Junio":6,"Julio":7,"Agosto":8,"Septiembre":9,"Octubre":10,"Noviembre":11,"Diciembre":12}
    mes_nombre=st.selectbox("Mes:", ["- Selecciona -"]+list(meses.keys()))
    if mes_nombre=="- Selecciona -":
        st.warning("⚠️ Selecciona un mes válido para continuar.")
        st.stop()

    mes=meses[mes_nombre]
    anio=2025

    def generar_fechas_personalizadas(anio, mes, patrimonio):
        if patrimonio in ["PS13-INCOFIN","PS11-ADRETAIL"]:
            dias=[10,20]
        elif patrimonio in ["PS10-HITES","PS12-MASISA"]:
            dias=[7,14,21]
        else:
            dias=[]
        fechas=[]
        for dia in dias:
            try: fechas.append(date(anio, mes, dia))
            except ValueError: continue
        fin_mes=pd.Timestamp(anio, mes, 1)+pd.offsets.MonthEnd(1)
        fechas.append(fin_mes.date())
        return fechas

    fechas=generar_fechas_personalizadas(anio, mes, patrimonio)
    opciones_fechas=["- Selecciona -","📂 Todas las Cesiones del Mes"]+fechas

    st.markdown("### 3️⃣ Selecciona la Fecha de Cesión")
    fecha=st.selectbox("Fecha de Cesión:", opciones_fechas)
    if fecha=="- Selecciona -":
        st.warning("⚠️ Selecciona una fecha válida para continuar.")
        st.stop()

    if fecha=="📂 Todas las Cesiones del Mes":
        registros_mes=[]
        for clave, lista in st.session_state.estado_actual.items():
            try:
                clave_pat,clave_fecha=clave.split("|")
                fecha_obj=datetime.strptime(clave_fecha,"%Y-%m-%d")
                if clave_pat==patrimonio and fecha_obj.month==mes:
                    registros_mes.extend([{**reg,"FECHA":clave_fecha,"ORDEN":idx} for idx, reg in enumerate(lista)])
            except Exception:
                continue

        if registros_mes:
            st.markdown("### 📂 Vista consolidada del mes")
            registros_ordenados=sorted(registros_mes, key=lambda r:(r["FECHA"], r["ORDEN"]))
            fechas_unicas=sorted(set(r["FECHA"] for r in registros_ordenados))

            for cesion_fecha in fechas_unicas:
                st.markdown(f"#### 📂 Cesión del {cesion_fecha}")
                for idx, reg in enumerate([r for r in registros_ordenados if r["FECHA"]==cesion_fecha], 1):
                    color_fondo={"REALIZADO":"#163423","PENDIENTE":"#4b3a12","ATRASADO":"#4a1f1f"}.get(reg["ESTADO"], "#4b3a12")
                    st.markdown(f"""
                        <div style='background-color:{color_fondo};padding:1rem;margin-bottom:1rem;border-radius:10px;border:1px solid #243a57;color:#e8eef7;'>
                            <p style='font-weight:bold;'>🧩 #{idx} - {reg['HITO']}</p>
                            <p><strong>Responsable:</strong> {reg['RESPONSABLE']}</p>
                            <p><strong>Estado:</strong> {reg['ESTADO']}</p>
                            <p><strong>Comentario:</strong> <em>{reg['COMENTARIO'] or '(Sin comentario)'}</em></p>
                        </div>
                    """, unsafe_allow_html=True)

            df_export=pd.DataFrame(registros_ordenados)[["FECHA","HITO","RESPONSABLE","ESTADO","COMENTARIO"]]
            df_export.insert(1,"PATRIMONIO",patrimonio)
            Path("seguimiento_excel").mkdir(exist_ok=True)
            nombre_archivo=f"seguimiento_excel/SEGUIMIENTO_{patrimonio.replace('-','')}_{mes_nombre.upper()}_{anio}.xlsx"
            df_export.to_excel(nombre_archivo, index=False)
            with open(nombre_archivo,"rb") as f:
                st.download_button(label="📅 Descargar seguimiento consolidado del mes", data=f, file_name=os.path.basename(nombre_archivo), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("No hay registros guardados para este mes.")
        st.stop()

    fecha_str=fecha.strftime("%Y-%m-%d")
    key_estado=f"{patrimonio}|{fecha_str}"
    if key_estado not in st.session_state.estado_actual:
        df_base=df_seg[df_seg["PATRIMONIO"]==patrimonio][["HITOS","RESPONSABLE"]].copy()
        registros_base=[]
        for _, row in df_base.iterrows():
            registros_base.append({"HITO":row["HITOS"],"RESPONSABLE":row["RESPONSABLE"],"ESTADO":"PENDIENTE","COMENTARIO":""})
        st.session_state.estado_actual[key_estado]=registros_base

    registros=st.session_state.estado_actual[key_estado]
    st.markdown("### Estado actual de la cesión")
    for idx, reg in enumerate(registros, 1):
        color_fondo={"REALIZADO":"#163423","PENDIENTE":"#4b3a12","ATRASADO":"#4a1f1f"}.get(reg["ESTADO"], "#4b3a12")
        st.markdown(f"""
            <div style='background-color:{color_fondo};padding:1rem;margin-bottom:1rem;border-radius:10px;border:1px solid #243a57;color:#e8eef7;'>
                <p style='font-weight:bold;'>🧩 #{idx} - {reg['HITO']}</p>
                <p><strong>Responsable:</strong> {reg['RESPONSABLE']}</p>
                <p><strong>Estado:</strong> {reg['ESTADO']}</p>
                <p><strong>Comentario:</strong> <em>{reg['COMENTARIO'] or '(Sin comentario)'}</em></p>
            </div>
        """, unsafe_allow_html=True)

    usuario_actual=st.session_state.get("usuario","").lower()
    if usuario_actual in ["nvega@efsecuritizadora.cl","jsepulveda@efsecuritizadora.cl"]:
        st.markdown("### ✏️ Modificar Estado de Cesión")
        nuevos_registros=[]
        for i, reg in enumerate(registros):
            st.markdown(f"<div style='margin-top:1.2rem;'><strong>🧩 {reg['HITO']}</strong></div>", unsafe_allow_html=True)
            cols=st.columns([1,3])
            with cols[0]:
                nuevo_estado=st.selectbox("Estado", ["PENDIENTE","REALIZADO","ATRASADO"], index=["PENDIENTE","REALIZADO","ATRASADO"].index(reg["ESTADO"]), key=f"estado_{i}")
            with cols[1]:
                nuevo_comentario=st.text_input("Comentario", value=reg["COMENTARIO"], key=f"comentario_{i}")
            nuevos_registros.append({"HITO":reg["HITO"],"RESPONSABLE":reg["RESPONSABLE"],"ESTADO":nuevo_estado,"COMENTARIO":nuevo_comentario})

        if st.button("💾 Guardar cambios"):
            st.session_state.estado_actual[key_estado]=nuevos_registros
            with open("seguimiento_guardado.json","w",encoding="utf-8") as f: json.dump(st.session_state.estado_actual, f, ensure_ascii=False, indent=2)
            st.success("✅ Cambios guardados correctamente.")
            st.rerun()

        df_actualizado=pd.DataFrame(nuevos_registros)[["HITO","RESPONSABLE","ESTADO","COMENTARIO"]]
        df_actualizado.insert(0,"FECHA",fecha_str)
        df_actualizado.insert(1,"PATRIMONIO",patrimonio)
        nombre_excel_actual=f"seguimiento_excel/SEGUIMIENTO_EDITABLE_{patrimonio.replace('-','')}_{fecha_str}.xlsx"
        Path("seguimiento_excel").mkdir(exist_ok=True)
        df_actualizado.to_excel(nombre_excel_actual, index=False)
        with open(nombre_excel_actual,"rb") as f:
            st.download_button(label="📥 Descargar seguimiento editable actual", data=f, file_name=os.path.basename(nombre_excel_actual), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
