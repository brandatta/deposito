import streamlit as st
import pandas as pd
import mysql.connector
import hashlib

# Configuración
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

# Validación
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Inicializar estado de modal
if "modal_abierto" not in st.session_state:
    st.session_state.modal_abierto = False
    st.session_state.sku_modal = None
    st.session_state.sector_modal = None

# Filtrar primeros sectores
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Función color SKU
def color_por_codigo(codigo):
    return '#' + hashlib.md5(codigo.encode()).hexdigest()[:6]

# CSS para grilla + modal
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
    padding: 8px;
    background-color: white;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    position: relative;
}
.sector-label {
    font-weight: bold;
    font-size: 13px;
    position: absolute;
    top: -14px;
    background: white;
    padding: 0 5px;
}
.sku-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 20px;
    justify-content: center;
}
button.sku {
    width: 40px;
    height: 40px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    color: white;
    border: none;
    cursor: pointer;
}
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.6);
    z-index: 999;
    display: flex;
    justify-content: center;
    align-items: center;
}
.modal-content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    width: 80%;
    max-height: 80%;
    overflow-y: auto;
}
.modal-close {
    text-align: right;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Grilla HTML
st.markdown('<div class="grilla">', unsafe_allow_html=True)

for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]
    html = f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">'
    for _, row in grupo.iterrows():
        color = color_por_codigo(str(row['codigo']))
        cantidad = int(row['cantidad'])
        sku = row["codigo"]
        # Botón Streamlit invisible
        if st.button(f"{sector}-{sku}", key=f"{sector}-{sku}"):
            st.session_state.modal_abierto = True
            st.session_state.sku_modal = sku
            st.session_state.sector_modal = sector
        # Render HTML
        html += f'<button class="sku" style="background-color:{color};">{cantidad}</button>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Modal
if st.session_state.modal_abierto:
    st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="modal-content">', unsafe_allow_html=True)
    st.markdown('<div class="modal-close">', unsafe_allow_html=True)
    if st.button("❌ Cerrar"):
        st.session_state.modal_abierto = False
        st.stop()
    st.markdown('</div>', unsafe_allow_html=True)
    
    sku = st.session_state.sku_modal
    sector = st.session_state.sector_modal
    st.markdown(f"### 📦 Registros para SKU **{sku}** en sector **{sector}**")
    df_detalle = df[(df["Sector"] == sector) & (df["codigo"] == sku)]
    st.dataframe(df_detalle.reset_index(drop=True), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
