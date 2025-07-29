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

# Validar columnas
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Tomar primeros 3 sectores únicos para demo
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y código
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Función para color único por SKU
def color_por_codigo(codigo):
    return "#" + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Leer parámetros de selección desde URL
params = st.query_params
sku_sel = params.get("sku", [None])[0]
sector_sel = params.get("sector", [None])[0]

# CSS + JavaScript
st.markdown("""
<style>
.grilla {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 20px;
}
.sector {
    border: 2px solid black;
    border-radius: 6px;
    background-color: white;
    padding: 8px;
    height: 160px;
    position: relative;
}
.sector-label {
    position: absolute;
    top: -14px;
    left: 8px;
    background-color: white;
    padding: 0 5px;
    font-weight: bold;
    font-size: 13px;
}
.sku-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 18px;
    justify-content: flex-start;
}
.sku {
    width: 36px;
    height: 36px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    text-decoration: none;
    cursor: pointer;
}
</style>

<script>
function navegar(sku, sector) {
    const url = new URL(window.location.href);
    url.searchParams.set("sku", sku);
    url.searchParams.set("sector", sector);
    window.location.href = url.toString();
}
</script>
""", unsafe_allow_html=True)

# Dibujar la grilla de sectores
st.markdown('<div class="grilla">', unsafe_allow_html=True)

for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]
    html = f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">'
    for _, row in grupo.iterrows():
        color = color_por_codigo(str(row['codigo']))
        cantidad = int(row['cantidad'])
        sku = row["codigo"]
        html += f'<div class="sku" onclick="navegar(\'{sku}\', \'{sector}\')" style="background-color:{color};" title="{sku}">{cantidad}</div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Mostrar detalles si hay selección
if sku_sel and sector_sel:
    st.markdown(f"### 🔍 Registros para SKU **{sku_sel}** en sector **{sector_sel}**")
    detalle = df[(df["Sector"] == sector_sel) & (df["codigo"] == sku_sel)]
    st.dataframe(detalle.reset_index(drop=True), use_container_width=True)
