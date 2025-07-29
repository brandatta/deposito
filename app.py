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

# Dropdown para seleccionar SKU
codigos_disponibles = df['codigo'].dropna().unique()
codigo_seleccionado = st.selectbox("Seleccioná un código:", codigos_disponibles)

# Agrupar cantidad por sector
df_filtrado = df[df['codigo'] == codigo_seleccionado]
df_sector = df_filtrado.groupby('Sector', as_index=False)['cantidad'].sum()

# Tomar los primeros 3 sectores para la grilla
sectores_grilla = df['Sector'].dropna().unique()[:3]
cantidades_por_sector = {row['Sector']: int(row['cantidad']) for _, row in df_sector.iterrows()}

# Función para color único por código
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# CSS ajustado con títulos dentro de las celdas
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
    justify-content: space-between;
    padding: 8px;
    box-sizing: border-box;
}}

.sector-label {{
    font-size: 13px;
    font-weight: bold;
    text-align: center;
    width: 100%;
    margin-bottom: 6px;
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

# Dibujar grilla
for sector in sectores_grilla:
    cantidad = cantidades_por_sector.get(sector, 0)
    html = f"""
    <div class="sector">
        <div class="sector-label">{sector}</div>
        <div class="cantidad-box">{cantidad if cantidad > 0 else "-"}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
