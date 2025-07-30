import streamlit as st
import pandas as pd
import mysql.connector
import hashlib

# Configuración general
st.set_page_config(page_title="Mapa del Depósito Visual", layout="wide")
st.title("📦 Plano del Depósito (por SKU)")

# Conexión MySQL
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["app_marco_new"]["host"],
        user=st.secrets["app_marco_new"]["user"],
        password=st.secrets["app_marco_new"]["password"],
        database=st.secrets["app_marco_new"]["database"],
        port=3306,
    )

# Cargar datos
@st.cache_data
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM mapa_deposito", conn)
    conn.close()
    return df

df = load_data()

# Validación de columnas
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Agrupar por sector y código
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Lista fija de sectores a mostrar
sectores_grilla = df['Sector'].dropna().unique()[:3]

# Función para color único por código
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Inicializar estado
if 'sector_seleccionado' not in st.session_state:
    st.session_state.sector_seleccionado = None

# Layout en columnas
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Detalle del Sector")
    if st.session_state.sector_seleccionado:
        detalle = df[df['Sector'] == st.session_state.sector_seleccionado]
        if not detalle.empty:
            st.markdown(f"**Sector seleccionado:** {st.session_state.sector_seleccionado}")
            st.dataframe(detalle[['codigo', 'cantidad']].groupby('codigo').sum().reset_index(), use_container_width=True)
        else:
            st.info("No hay datos para este sector.")
    else:
        st.info("Seleccioná un sector de la grilla.")

with col2:
    # CSS
    st.markdown(f"""
    <style>
    .grilla {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 25px;
        margin-top: 10px;
        justify-items: center;
    }}
    .sector {{
        width: 120px;
        aspect-ratio: 1 / 1;
        border: 2px solid black;
        border-radius: 8px;
        background-color: #ffffff;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        box-sizing: border-box;
    }}
    .sector-label {{
        position: absolute;
        top: 6px;
        font-size: 13px;
        font-weight: bold;
        background-color: white;
        padding: 0 4px;
    }}
    .sku-box {{
        width: 40px;
        height: 40px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 4px;
    }}
    </style>
    <div class="grilla">
    """, unsafe_allow_html=True)

    for sector in sectores_grilla:
        grupo = df_grouped[df_grouped['Sector'] == sector]
        html = f'<div class="sector" onclick="window.location.search = `?sector={sector}`"><div class="sector-label">{sector}</div>'
        for _, row in grupo.iterrows():
            color = color_por_codigo(str(row['codigo']))
            cantidad = int(row['cantidad'])
            html += f'<div class="sku-box" style="background-color:{color}" title="{row["codigo"]}">{cantidad}</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Capturar clic vía parámetros
params = st.query_params
if "sector" in params:
    st.session_state.sector_seleccionado = params["sector"][0]
