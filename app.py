import pandas as pd
import os
import streamlit as st

# =====================================
# 📁 Configuración de la página
# =====================================
st.set_page_config(page_title="Explorador de Gastos Patrimoniales", layout="wide")

# =====================================
# ⚠️ Definir la ruta donde están los archivos Excel
ruta = "."

# =====================================
# 📁 Cargar datos
# =====================================
@st.cache_data
def cargar_datos():
    df_gasto_ps = pd.read_excel(os.path.join(ruta, 'GASTO-PS.xlsx'))
    df_calendario = pd.read_excel(os.path.join(ruta, 'CALENDARIO-GASTOS.xlsx'))
    df_ps = pd.read_excel(os.path.join(ruta, 'PS.xlsx'))
    df_años = pd.read_excel(os.path.join(ruta, 'TABLA AÑO.xlsx'))

    # Normalizar nombres
    for df in [df_gasto_ps, df_calendario, df_ps, df_años]:
        df.columns = df.columns.str.strip().str.upper()

    df_años['AÑO'] = df_años['AÑO'].astype(str)
    return df_gasto_ps, df_calendario, df_ps, df_años

df_gasto_ps, df_calendario, df_ps, df_años = cargar_datos()

# =====================================
# 🎛️ Filtros
# =====================================
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

# =====================================
# 🎨 Estilo de tablas para HTML
# =====================================
def estilo_tabla(df):
    return df.style.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center')]},
        {'selector': 'td', 'props': [('text-align', 'center'), ('white-space', 'normal'), ('word-wrap', 'break-word')]}
    ])

# =====================================
# 📊 Mostrar tabla de Gastos del Patrimonio con estilo
# =====================================
st.markdown("### 💼 Gastos del Patrimonio (GASTO-PS)")
gastos_ps_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]
if frecuencia != 'Todos':
    gastos_ps_filtrado = gastos_ps_filtrado[
        gastos_ps_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()
    ]

if gastos_ps_filtrado.empty:
    st.warning("⚠️ No existen datos para el patrimonio y frecuencia seleccionados.")
else:
    st.markdown(estilo_tabla(gastos_ps_filtrado).to_html(), unsafe_allow_html=True)

# =====================================
# 📊 Mostrar tabla de Calendario de Gastos (SI lógico + estilo)
# =====================================
st.markdown("### 📅 Calendario de Gastos (CALENDARIO-GASTOS)")

# ⚠️ Chequeamos si el año existe como columna
if año in df_calendario.columns:
    calendario_filtrado = df_calendario[['MES', 'PATRIMONIO', año]].copy()
    calendario_filtrado = calendario_filtrado[calendario_filtrado['PATRIMONIO'] == patrimonio]
    if mes != 'Todos':
        calendario_filtrado = calendario_filtrado[calendario_filtrado['MES'].str.upper() == mes.upper()]

    # Renombrar la columna del año a "GASTOS"
    calendario_filtrado = calendario_filtrado.rename(columns={año: 'GASTOS'})

    # Eliminar filas vacías
    calendario_filtrado = calendario_filtrado.dropna(subset=['GASTOS'])

    if calendario_filtrado.empty:
        st.warning("⚠️ No existen datos para el año seleccionado.")
    else:
        st.markdown(estilo_tabla(calendario_filtrado).to_html(), unsafe_allow_html=True)
else:
    st.warning("⚠️ El año seleccionado no está en la tabla de calendario.")





