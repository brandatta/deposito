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

# Estado inicial
if 'sector_seleccionado' not in st.session_state:
    st.session_state.sector_seleccionado = None

# Dropdown para seleccionar SKU
codigos_disponibles = df['codigo'].dropna().unique()
codigo_seleccionado = st.selectbox("Seleccioná un código:", codigos_disponibles)

# Agrupar cantidad por sector para el código seleccionado
df_filtrado = df[df['codigo'] == codigo_seleccionado]
df_sector = df_filtrado.groupby('Sector', as_index=False)['cantidad'].sum()

# Tomar los primeros 3 sectores únicos para la grilla
sectores_grilla = df['Sector'].dropna().unique()[:3]
cantidades_por_sector = {row['Sector']: int(row['cantidad']) for _, row in df_sector.iterrows()}

# Función para color único por código
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# CSS
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
    text-align: center;
    background-color: white;
    padding: 0 4px;
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
    cursor: pointer;
}}
</style>
""", unsafe_allow_html=True)

# Layout: tabla de detalle (izquierda) y grilla (derecha)
col1, col2 = st.columns([2, 3])

with col1:
    if st.session_state.sector_seleccionado:
        st.markdown("### 🧾 Detalle del sector")
        if st.button("❌ Cerrar"):
            st.session_state.sector_seleccionado = None
        else:
            detalle = df[df['Sector'] == st.session_state.sector_seleccionado]
            resumen = detalle.groupby('codigo', as_index=False)['cantidad'].sum()
            st.dataframe(resumen, use_container_width=True)

with col2:
    st.markdown('<div class="grilla">', unsafe_allow_html=True)
    for sector in sectores_grilla:
        cantidad = cantidades_por_sector.get(sector, 0)

        if st.button(f"📍 {sector}", key=f"btn_{sector}"):
            st.session_state.sector_seleccionado = sector

        html = f"""
        <div class="sector">
            <div class="sector-label">{sector}</div>"""
        if cantidad > 0:
            html += f"""<div class="cantidad-box">{cantidad}</div>"""
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
