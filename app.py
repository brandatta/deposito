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

# Leer parámetros
params = st.query_params
sku_sel = params.get("sku", [None])[0]
sector_sel = params.get("sector", [None])[0]

# Filtrar primeros 3 sectores
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar cantidades por sector y sku
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Color único por SKU
def color_por_codigo(codigo):
    return "#" + hashlib.md5(codigo.encode()).hexdigest()[:6]

# CSS y grilla
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
}
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
}
.modal {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    position: relative;
}
.close-btn {
    position: absolute;
    top: 8px;
    right: 12px;
    font-size: 20px;
    font-weight: bold;
    color: #999;
    cursor: pointer;
}
</style>
<div class="grilla">
""", unsafe_allow_html=True)

# Renderizar sectores con SKUs
for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]
    html = f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">'
    for _, row in grupo.iterrows():
        color = color_por_codigo(str(row['codigo']))
        cantidad = int(row['cantidad'])
        sku = row["codigo"]
        url = f"?sku={sku}&sector={sector}"
        html += f'<a class="sku" href="{url}" style="background-color:{color};" title="{sku}">{cantidad}</a>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Mostrar modal si hay selección
if sku_sel and sector_sel:
    detalle = df[(df["Sector"] == sector_sel) & (df["codigo"] == sku_sel)]
    
    st.markdown(f"""
    <div class="overlay" onclick="window.location.href='.'">
        <div class="modal" onclick="event.stopPropagation()">
            <div class="close-btn" onclick="window.location.href='.'">&times;</div>
            <h4>📦 Registros para <b>{sku_sel}</b> en sector <b>{sector_sel}</b></h4>
            <div id="detalle-table"></div>
        </div>
    </div>
    <script>
    const table = `{detalle.to_html(index=False, classes='dataframe', border=0)}`;
    document.getElementById("detalle-table").innerHTML = table;
    </script>
    """, unsafe_allow_html=True)
