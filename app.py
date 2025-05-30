import pandas as pd
import os
import streamlit as st

st.set_page_config(page_title="Explorador de Gastos Patrimoniales", layout="wide")
ruta = "."

@st.cache_data
def cargar_datos():
    df_gasto_ps = pd.read_excel(os.path.join(ruta, 'GASTO-PS.xlsx'))
    df_calendario = pd.read_excel(os.path.join(ruta, 'CALENDARIO-GASTOS.xlsx'))
    df_ps = pd.read_excel(os.path.join(ruta, 'PS.xlsx'))
    df_años = pd.read_excel(os.path.join(ruta, 'TABLA AÑO.xlsx'))

    for df in [df_gasto_ps, df_calendario, df_ps, df_años]:
        df.columns = df.columns.astype(str).str.strip().str.upper()

    # ⚠️ Normaliza las columnas de año para asegurar coincidencias
    df_calendario.columns = df_calendario.columns.astype(str).str.strip()
    df_años['AÑO'] = df_años['AÑO'].astype(str).str.strip()

    return df_gasto_ps, df_calendario, df_ps, df_años

df_gasto_ps, df_calendario, df_ps, df_años = cargar_datos()

st.title("📊 Explorador de Gastos Patrimoniales")
col1, col2, col3, col4 = st.columns(4)
with col1:
    patrimonio = st.selectbox("Selecciona un Patrimonio:", df_ps['PATRIMONIO'].unique())
with col2:
    año = st.selectbox("Selecciona un Año:", sorted(df_años['AÑO'].unique()))
with col3:
    meses_opciones = ['Todos'] + list(df_calendario['MES'].unique())
    mes = st.selectbox("Selecciona un Mes:", meses_opciones)
with col4:
    frecuencia_opciones = ['Todos', 'MENSUAL', 'ANUAL', 'TRIMESTRAL']
    frecuencia = st.selectbox("Frecuencia:", frecuencia_opciones)

def estilo_tabla(df):
    return df.style.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center')]},
        {'selector': 'td', 'props': [('text-align', 'center'), ('white-space', 'normal'), ('word-wrap', 'break-word')]}
    ])

st.markdown("### 💼 Gastos del Patrimonio")
gastos_ps_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]
if frecuencia != 'Todos':
    gastos_ps_filtrado = gastos_ps_filtrado[
        gastos_ps_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()
    ]
if gastos_ps_filtrado.empty:
    st.warning("⚠️ No existen datos para el patrimonio y frecuencia seleccionados.")
else:
    st.markdown(estilo_tabla(gastos_ps_filtrado).to_html(), unsafe_allow_html=True)

st.markdown("### 📅 Calendario de Gastos")

# 🔥 Convertir año a string y quitar espacios
año = str(año).strip()
if año in df_calendario.columns:
    columnas_a_mostrar = ['MES', 'PATRIMONIO', año]
    calendario_filtrado = df_calendario[columnas_a_mostrar].copy()
    calendario_filtrado = calendario_filtrado[calendario_filtrado['PATRIMONIO'] == patrimonio]
    if mes != 'Todos':
        calendario_filtrado = calendario_filtrado[calendario_filtrado['MES'].str.upper() == mes.upper()]
    calendario_filtrado = calendario_filtrado.rename(columns={año: 'GASTOS'})
    calendario_filtrado = calendario_filtrado.dropna(subset=['GASTOS'])
    if calendario_filtrado.empty:
        st.warning("⚠️ No existen datos para el año y filtros seleccionados.")
    else:
        st.markdown(estilo_tabla(calendario_filtrado).to_html(), unsafe_allow_html=True)
else:
    st.warning("⚠️ El año seleccionado no está presente como columna en la tabla de calendario.")






