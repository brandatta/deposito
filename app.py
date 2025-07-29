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
if not {'Sector', 'cantidad', 'codigo', 'descripcion'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo, descripcion")
    st.stop()

# Estado del modal
if "sku_modal" not in st.session_state:
    st.session_state.sku_modal = None
if "sector_modal" not in st.session_state:
    st.session_state.sector_modal = None

# Tomar primeros 3 sectores únicos
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Función para color SKU
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Mostrar estilos
st.markdown("""
<style>
.grilla {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 20px;
}
.sector {
    width: 120px;
    height: 120px;
    border: 2px solid black;
    border-radius: 6px;
    background-color: white;
    padding: 5px;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
}
.sector-label {
    position: absolute;
    top: -14px;
    left: 6px;
    background-color: white;
    padding: 0 5px;
    font-size: 12px;
    font-weight: bold;
}
.sku-container {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    justify-content: center;
    margin-top: 20px;
}
.sku-btn {
    width: 36px;
    height: 36px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    color: white;
    border: none;
    cursor: pointer;
}
.modal-overlay {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.85);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}
.modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    max-height: 80%;
    max-width: 500px;
    overflow-y: auto;
    position: relative;
}
.modal-close {
    position: absolute;
    top: 8px;
    right: 12px;
    font-size: 22px;
    cursor: pointer;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Mostrar grilla
st.markdown('<div class="grilla">', unsafe_allow_html=True)
for sector in sectores:
    html = f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">'
    grupo = df_grouped[df_grouped["Sector"] == sector]
    for _, row in grupo.iterrows():
        color = color_por_codigo(row["codigo"])
        sku = row["codigo"]
        cantidad = int(row["cantidad"])
        btn_key = f"{sector}_{sku}"
        if st.button(f"{cantidad}", key=btn_key):
            st.session_state.sku_modal = sku
            st.session_state.sector_modal = sector
        html += f'<button class="sku-btn" style="background-color:{color};" disabled>{cantidad}</button>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Mostrar modal si hay selección
if st.session_state.sku_modal and st.session_state.sector_modal:
    sku = st.session_state.sku_modal
    sector = st.session_state.sector_modal
    detalle = df[(df["codigo"] == sku) & (df["Sector"] == sector)]

    st.markdown(f"""
    <div class="modal-overlay" onclick="window.location.reload()">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-close" onclick="window.location.reload()">×</div>
            <h4>📦 Registros para <b>{sku}</b> en sector <b>{sector}</b></h4>
            <ul>
                {''.join(f"<li>{r}</li>" for r in detalle['descripcion'])}
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
