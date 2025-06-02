import streamlit as st

# Inicializar la página
st.set_page_config(page_title="Panel de Información - EF Securitizadora", layout="wide")

# Mostrar logo si existe
if os.path.exists("EF logo-blanco@4x.png"):
    st.image("EF logo-blanco@4x.png", width=300)

# Estilos generales y para los botones de navegación
st.markdown("""
    <style>
    .stApp { background-color: #0B1F3A !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #FFFFFF !important; text-align: center !important; }
    h1 { font-size: 3em !important; }  /* Título principal más grande */
    .nav-button {
        background-color: #007BFF;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
        font-size: 1.2em;
        cursor: pointer;
        margin: 5px;
    }
    .nav-button:hover {
        background-color: #0056b3;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar el estado de la página
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

# Barra de navegación personalizada
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Inicio", key="inicio"):
        st.session_state.pagina = "Inicio"
with col2:
    if st.button("💰 Gastos", key="gastos"):
        st.session_state.pagina = "Gastos"
with col3:
    if st.button("📚 Definiciones", key="definiciones"):
        st.session_state.pagina = "Definiciones"

# Renderizar el contenido según la opción elegida
if st.session_state.pagina == "Inicio":
    st.title("Panel de Información - EF Securitizadora")
    # Contenido de la página de inicio
elif st.session_state.pagina == "Gastos":
    st.title("EF Securitizadora - Gastos")
    # Contenido de la página de gastos
elif st.session_state.pagina == "Definiciones":
    st.title("EF Securitizadora - Definiciones y Triggers")
    # Contenido de la página de definiciones




