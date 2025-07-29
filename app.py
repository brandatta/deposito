import streamlit as st
import pandas as pd
import mysql.connector
import hashlib

# Configuración general
st.set_page_config(page_title="Mapa del Depósito Visual", layout="wide")
st.title("📦 Plano del Depósito con SKUs y cantidades")

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

# Filtrar primeros 3 sectores únicos
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y sku, sumando cantidades
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Colores únicos por SKU
def color_por_codigo(codigo):
    hash_object = hashlib.md5(codigo.encode())
    return '#' + hash_object.hexdigest()[:6]

# CSS: sectores más chicos, SKUs se mantienen grandes
st.markdown("""
<style>
.grilla {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 20px;
    justify-items: center;
}
.sector {
    width: 120px;
    height: 120px;
    border: 2px solid black;
    border-radius: 6px;
    padding: 5px;
    background-color: white;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}
.sector-label {
    position: absolute;
    top: -16px;
    left: 5px;
    font-weight: bold;
    background-color: white;
    padding: 0 4px;
    font-size: 12px;
}
.sku-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    overflow-y: auto;
    margin-top: 5px;
}
.sku {
    width: 40px;
    height: 40px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 13px;
    color: white;
}
</style>
<div class="grilla">
""", unsafe_allow_html=True)

# Renderizar cada sector cuadrado
for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]
    html = f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">'
    for _, row in grupo.iterrows():
        color = color_por_codigo(str(row['codigo']))
        cantidad = int(row['cantidad'])
        html += f'<div class="sku" style="background-color:{color};" title="{row["codigo"]}">{cantidad}</div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
