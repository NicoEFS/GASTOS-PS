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
# 📁 Cargar datos (una sola vez)
# =====================================
@st.cache_data
def cargar_datos():
    df_gasto_ps = pd.read_excel(os.path.join(ruta, 'GASTO-PS.xlsx'))
    df_calendario = pd.read_excel(os.path.join(ruta, 'CALENDARIO-GASTOS.xlsx'))
    df_ps = pd.read_excel(os.path.join(ruta, 'PS.xlsx'))

    # Normalizar nombres
    df_gasto_ps.columns = df_gasto_ps.columns.str.strip().str.upper()
    df_calendario.columns = df_calendario.columns.str.strip().str.upper()
    df_ps.columns = df_ps.columns.str.strip().str.upper()

    return df_gasto_ps, df_calendario, df_ps

df_gasto_ps, df_calendario, df_ps = cargar_datos()

# =====================================
# 🎛️ Filtros interactivos
# =====================================
st.title("📊 Explorador de Gastos Patrimoniales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    patrimonio = st.selectbox("Selecciona un Patrimonio:", df_ps['PATRIMONIO'].unique())

with col2:
    año = st.selectbox("Selecciona un Año:", sorted(df_calendario['AÑO'].unique()))

with col3:
    meses_opciones = ['Todos'] + list(df_calendario['MES'].unique())
    mes = st.selectbox("Selecciona un Mes:", meses_opciones)

with col4:
    frecuencia_opciones = ['Todos', 'MENSUAL', 'ANUAL', 'TRIMESTRAL']
    frecuencia = st.selectbox("Frecuencia:", frecuencia_opciones)

# =====================================
# 🎨 Estilo CSS para centrar encabezados y ajustar celdas
# =====================================
st.markdown("""
    <style>
    table {
        table-layout: fixed;
        width: 100%;
    }
    th {
        text-align: center;
    }
    td {
        word-wrap: break-word;
        white-space: normal;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================
# 📊 Mostrar tablas filtradas
# =====================================
st.markdown("### 💼 Gastos del Patrimonio (GASTO-PS)")
gastos_ps_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]

if frecuencia != 'Todos':
    gastos_ps_filtrado = gastos_ps_filtrado[
        gastos_ps_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()
    ]

# Mostrar tabla como HTML con CSS aplicado
st.markdown(gastos_ps_filtrado.to_html(index=False, escape=False), unsafe_allow_html=True)

st.markdown("### 📅 Calendario de Gastos (CALENDARIO-GASTOS)")
calendario_filtrado = df_calendario[
    (df_calendario['PATRIMONIO'] == patrimonio) &
    (df_calendario['AÑO'] == año)
]

if mes != 'Todos':
    calendario_filtrado = calendario_filtrado[
        calendario_filtrado['MES'].str.upper() == mes.upper()
    ]

# Mostrar tabla como HTML con CSS aplicado
st.markdown(calendario_filtrado.to_html(index=False, escape=False), unsafe_allow_html=True)

