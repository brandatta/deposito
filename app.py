import streamlit as st
import pandas as pd
import mysql.connector
import random
import hashlib

# Configuración general
st.set_page_config(page_title="Mapa del Depósito", layout="wide")
st.title("📦 Plano del Depósito Visual")

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

# Limitar a los primeros 3 sectores
sectores = df['Sector'].unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Asignar un color único por código
def color_por_codigo(codigo):
    hash_object = hashlib.md5(codigo.encode())
    hex_color = '#' + hash_object.hexdigest()[:6]
    return hex_color

# Agrupar por sector
df_grouped = df.groupby('Sector')

# HTML y CSS para grilla
st.markdown("""
<style>
.grilla {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 20px;
}
.sector {
    border: 2px solid black;
    border-radius: 8px;
    height: 200px;
    display: flex;
    flex-wrap: wrap;
    align-content: flex-start;
    justify-content: flex-start;
    padding: 8px;
    position: relative;
    background-color: #fff;
}
.codigo {
    width: 20px;
    height: 20px;
    margin: 2px;
    border-radius: 3px;
}
.sector-label {
    position: absolute;
    top: 5px;
    left: 8px;
    font-weight: bold;
    background: white;
    padding: 2px 6px;
    font-size: 13px;
    z-index: 1;
}
</style>
<div class="grilla">
""", unsafe_allow_html=True)

# Render de cada sector como cuadrado visual
for sector, grupo in df_grouped:
    codigos = grupo['codigo'].unique()
    html = f'<div class="sector"><div class="sector-label">{sector}</div>'
    for cod in codigos:
        color = color_por_codigo(str(cod))
        html += f'<div class="codigo" style="background-color:{color};" title="{cod}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
