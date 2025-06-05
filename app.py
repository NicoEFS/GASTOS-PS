# INICIO
if st.session_state.pagina == "Inicio":
    st.markdown("## Bienvenido al Panel de Información de EF Securitizadora.")
    st.markdown("""
    Selecciona una pestaña en la parte superior para comenzar a explorar información sobre los patrimonios separados. 
    Dentro de estas secciones podrás encontrar tanto los gastos y su distribución mensual, como también las principales definiciones que involucran a los patrimonios separados.

    ### 🔗 Accesos rápidos a paneles de recaudación:
    - [RECAUDACIÓN PS10-HITES](https://app.powerbi.com/view?r=eyJrIjoiZGE0...)
    - [RECAUDACIÓN PS11-ADRETAIL](https://app.powerbi.com/view?r=eyJrIjoiMzQ4...)
    - [RECAUDACIÓN PS12-MASISA](https://app.powerbi.com/view?r=eyJrIjoiNmI4...)
    - [RECAUDACIÓN PS13-INCOFIN](https://app.powerbi.com/view?r=eyJrIjoiMTA2...)
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

            fig = px.area(
                cal_filtrado,
                x='MES',
                y='CANTIDAD',
                labels={'CANTIDAD': 'Cantidad de Gastos'},
                title='Tendencia de Gastos por Mes',
            )
            fig.add_scatter(
                x=cal_filtrado['MES'],
                y=cal_filtrado['CANTIDAD'],
                mode='lines+markers',
                name='Tendencia',
                line=dict(color='black', width=2),
                marker=dict(color='black')
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='black', size=14),
                margin=dict(t=40, b=40),
                xaxis_title='Mes',
                yaxis_title='Cantidad de Gastos',
                xaxis=dict(tickangle=-45)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No existen datos para el mes y patrimonio seleccionados.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")

# DEFINICIONES
if st.session_state.pagina == "Definiciones":
    st.markdown("### 📘 Definiciones y Triggers")
    if st.button("🔄 Recargar archivos"):
        st.cache_data.clear()
        st.success("Datos recargados exitosamente.")
        st.rerun()

    patrimonio_opciones = ['- Selecciona -'] + list(df_ps['PATRIMONIO'].unique())
    patrimonio = st.selectbox("Patrimonio:", patrimonio_opciones, key="patrimonio_def")

    if patrimonio != '- Selecciona -':
        patrimonio_upper = patrimonio.strip().upper()
        definiciones_filtrado = df_definiciones[df_definiciones['PATRIMONIO'] == patrimonio_upper]
        if not definiciones_filtrado.empty:
            st.markdown("#### 📒 Definiciones")
            if 'CONCEPTO' in definiciones_filtrado.columns:
                definiciones_filtrado = definiciones_filtrado.sort_values(by='CONCEPTO')
            columnas_visibles = [col for col in definiciones_filtrado.columns if col != 'PATRIMONIO']
            st.markdown(estilo_tabla(definiciones_filtrado[columnas_visibles]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No hay definiciones para el patrimonio seleccionado.")

        triggers_filtrado = df_triggers[df_triggers['PATRIMONIO'] == patrimonio_upper]
        if not triggers_filtrado.empty:
            st.markdown("#### 📊 Triggers")
            columnas_triggers = [col for col in triggers_filtrado.columns if col != 'PATRIMONIO']
            st.markdown(estilo_tabla(triggers_filtrado[columnas_triggers]), unsafe_allow_html=True)
        else:
            st.warning("⚠️ No existen triggers para el patrimonio seleccionado.")
    else:
        st.warning("⚠️ Por favor, selecciona un Patrimonio para ver la información.")


