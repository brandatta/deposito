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

# Leer parámetros de selección
params = st.query_params
sku_sel = params.get("sku", [None])[0]
sector_sel = params.get("sector", [None])[0]

# Filtrar primeros 3 sectores únicos
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y sku, sumando cantidades
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Función para color único por SKU
def color_por_codigo(codigo):
    hash_object = hashlib.md5(codigo.encode())
    return '#' + hash_object.hexdigest()[:6]

# CSS + JS para diseño y modal
st.markdown("""
<style>
.grilla {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
    margin-top: 20px;
    justify-items: center;
}
.sector {
    width: 120px;
    height: 120px;
    border: 2px solid black;
    border-radius: 6px;
    padding: 8px 5px 5px 5px;
    background-color: white;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
}
.sector-label {
    font-weight: bold;
    font-size: 13px;
    margin-bottom: 6px;
    text-align: center;
    width: 100%;
}
.sku-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    overflow-y: auto;
    justify-content: center;
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
    cursor: pointer;
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

<script>
function navegar(sku, sector) {
    const url = new URL(window.location.href);
    url.searchParams.set("sku", sku);
    url.searchParams.set("sector", sector);
    window.location.href = url.toString();
}
</script>

<div class="grilla">
""", unsafe_allow_html=True)

# Renderizar sectores
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

# Mostrar modal con detalle si hay selección
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
