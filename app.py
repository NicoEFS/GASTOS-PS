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
# 📊 Mostrar tabla de Gastos del Patrimonio
# =====================================
st.markdown("### 💼 Gastos del Patrimonio (GASTO-PS)")
gastos_ps_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]
if frecuencia != 'Todos':
    gastos_ps_filtrado = gastos_ps_filtrado[
        gastos_ps_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()
    ]
st.dataframe(gastos_ps_filtrado, use_container_width=True)

# =====================================
# 📊 Mostrar tabla de Calendario de Gastos (sin melt)
# =====================================
st.markdown("### 📅 Calendario de Gastos (CALENDARIO-GASTOS)")

# ⚠️ Chequeamos si el año existe como columna en la tabla original
if año in df_calendario.columns:
    calendario_filtrado = df_calendario[['MES', 'PATRIMONIO', año]].copy()
    calendario_filtrado = calendario_filtrado[calendario_filtrado['PATRIMONIO'] == patrimonio]
    if mes != 'Todos':
        calendario_filtrado = calendario_filtrado[calendario_filtrado['MES'].str.upper() == mes.upper()]

    # Renombrar la columna del año a "GASTOS" para mostrarla de forma uniforme
    calendario_filtrado = calendario_filtrado.rename(columns={año: 'GASTOS'})

    # Eliminar filas vacías (opcional)
    calendario_filtrado = calendario_filtrado.dropna(subset=['GASTOS'])

    if calendario_filtrado.empty:
        st.warning("⚠️ No existen datos para el año seleccionado.")
    else:
        st.dataframe(calendario_filtrado, use_container_width=True)
else:
    st.warning("⚠️ El año seleccionado no está en la tabla de calendario.")





