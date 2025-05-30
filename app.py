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

    # Transformar df_calendario: pasar años de columnas a filas (formato largo)
    df_calendario = df_calendario.melt(
        id_vars=['MES', 'PATRIMONIO'],
        var_name='AÑO',
        value_name='GASTOS'
    )

    # Eliminar filas donde 'GASTOS' está vacío
    df_calendario = df_calendario.dropna(subset=['GASTOS'])

    # Asegurar que AÑO sea string
    df_calendario['AÑO'] = df_calendario['AÑO'].astype(str)

    return df_gasto_ps, df_calendario, df_ps

df_gasto_ps, df_calendario, df_ps = cargar_datos()

# =====================================
# 🎛️ Filtros interactivos (usando solo valores reales)
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
# 🎨 Estilo de las tablas
# =====================================
def estilo_tabla(df):
    return df.style.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center')]},
        {'selector': 'td', 'props': [('text-align', 'center'), ('white-space', 'normal'), ('word-wrap', 'break-word')]}
    ])

# =====================================
# 📊 Mostrar tabla de Gastos del Patrimonio
# =====================================
st.markdown("### 💼 Gastos del Patrimonio (GASTO-PS)")
gastos_ps_filtrado = df_gasto_ps[df_gasto_ps['PATRIMONIO'] == patrimonio]

if frecuencia != 'Todos':
    gastos_ps_filtrado = gastos_ps_filtrado[
        gastos_ps_filtrado['PERIODICIDAD'].str.upper() == frecuencia.upper()
    ]

st.markdown(estilo_tabla(gastos_ps_filtrado).to_html(), unsafe_allow_html=True)

# =====================================
# 📊 Mostrar tabla de Calendario de Gastos
# =====================================
st.markdown("### 📅 Calendario de Gastos (CALENDARIO-GASTOS)")
calendario_filtrado = df_calendario[
    (df_calendario['PATRIMONIO'] == patrimonio) &
    (df_calendario['AÑO'] == año)
]

if mes != 'Todos':
    calendario_filtrado = calendario_filtrado[
        calendario_filtrado['MES'].str.upper() == mes.upper()
    ]

# Eliminar la columna AÑO antes de mostrar (opcional)
calendario_filtrado = calendario_filtrado.drop(columns=['AÑO'])

st.markdown(estilo_tabla(calendario_filtrado).to_html(), unsafe_allow_html=True)


