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

# Validación
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Dropdown de código
codigos_disponibles = df['codigo'].dropna().unique()
codigo_seleccionado = st.selectbox("Seleccioná un código:", codigos_disponibles)

# Cantidades por sector para ese código
df_filtrado = df[df['codigo'] == codigo_seleccionado]
df_sector = df_filtrado.groupby('Sector', as_index=False)['cantidad'].sum()
cantidades_por_sector = {row['Sector']: int(row['cantidad']) for _, row in df_sector.iterrows()}
sectores_grilla = df['Sector'].dropna().unique()[:3]

# Color único por SKU
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Estado seleccionado
if "sector_seleccionado" not in st.session_state:
    st.session_state["sector_seleccionado"] = None

# Columnas
col1, col2 = st.columns([1, 2])

# Columna izquierda: detalle
with col1:
    st.subheader("📋 Detalle del Sector")
    if st.session_state["sector_seleccionado"]:
        df_detalle = df[df["Sector"] == st.session_state["sector_seleccionado"]]
        st.markdown(f"**Sector seleccionado:** {st.session_state['sector_seleccionado']}")
        st.dataframe(
            df_detalle[['codigo', 'cantidad']].groupby('codigo').sum().reset_index(),
            use_container_width=True
        )
    else:
        st.info("Seleccioná un sector para ver su contenido.")

# Columna derecha: grilla
with col2:
    st.markdown(f"""
    <style>
    .grilla {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 25px;
        margin-top: 30px;
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
        z-index: 1;
    }}
    .cantidad-box {{
        width: 40px;
        height: 40px;
        border-radius: 6px;
        background-color: {color_por_codigo(codigo_seleccionado)};
        color: white;
        font-weight: bold;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    </style>
    <div class="grilla">
    """, unsafe_allow_html=True)

    for sector in sectores_grilla:
        cantidad = cantidades_por_sector.get(sector, 0)
        button_clicked = st.button(f"Seleccionar {sector}", key=f"btn_{sector}")
        if button_clicked:
            st.session_state["sector_seleccionado"] = sector

        html = f"""<div class="sector">
                    <div class="sector-label">{sector}</div>"""
        if cantidad > 0:
            html += f"""<div class="cantidad-box">{cantidad}</div>"""
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
