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

# Dropdown de código
codigos_disponibles = df['codigo'].dropna().unique()
codigo_seleccionado = st.selectbox("Seleccioná un código:", codigos_disponibles)

# Filtrar y agrupar cantidades por sector
df_filtrado = df[df['codigo'] == codigo_seleccionado]
df_sector = df_filtrado.groupby('Sector', as_index=False)['cantidad'].sum()

# Tomar 3 sectores fijos
sectores_grilla = df['Sector'].dropna().unique()[:3]
cantidades_por_sector = {row['Sector']: int(row['cantidad']) for _, row in df_sector.iterrows()}

# Función para color único por código
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# CSS ajustado
st.markdown(f"""
<style>
.grilla {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px 20px;
    margin-top: 40px;
    justify-items: center;
    align-items: start;
}}
.sector {{
    aspect-ratio: 1 / 1;
    width: 120px;
    border: 2px solid black;
    border-radius: 8px;
    background-color: #fefefe;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
}}
.sector-label {{
    position: absolute;
    top: -22px;
    left: 8px;
    background-color: white;
    font-size: 13px;
    font-weight: bold;
    padding: 0 6px;
}}
.cantidad-box {{
    width: 40px;
    height: 40px;
    border-radius: 6px;
    background-color: {color_por_codigo(codigo_seleccionado)};
    color: white;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
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
        {"<div class='cantidad-box'>" + str(cantidad) + "</div>" if cantidad > 0 else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
