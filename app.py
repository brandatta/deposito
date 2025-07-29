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

# Filtrar primeros 3 sectores únicos
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y SKU
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Función color
def color_por_codigo(codigo):
    return "#" + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Captura de clic en POST
if 'clicked' in st.session_state:
    clicked = st.session_state['clicked']
    if clicked:
        sector_clicked, sku_clicked = clicked.split("__")
        st.session_state['sector_seleccionado'] = sector_clicked
        st.session_state['sku_seleccionado'] = sku_clicked
        st.session_state['clicked'] = None  # reset

# CSS
st.markdown("""
<style>
.grilla {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 20px;
    justify-items: center;
}
.sector-box {
    border: 2px solid black;
    border-radius: 6px;
    background-color: white;
    padding: 8px;
    width: 130px;
    height: 130px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.sector-label {
    font-weight: bold;
    font-size: 13px;
    margin-bottom: 8px;
}
.sku-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 4px;
}
.sku-btn {
    width: 36px;
    height: 36px;
    border-radius: 4px;
    border: none;
    color: white;
    font-weight: bold;
    font-size: 13px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# Iniciar grilla visual
st.markdown('<div class="grilla">', unsafe_allow_html=True)

for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]

    html = f'<div class="sector-box"><div class="sector-label">{sector}</div><div class="sku-container">'

    for _, row in grupo.iterrows():
        color = color_por_codigo(str(row['codigo']))
        cantidad = int(row['cantidad'])
        key = f"{sector}__{row['codigo']}"
        html += f"""
        <form method="post">
            <input type="hidden" name="clicked" value="{key}"/>
            <button class="sku-btn" type="submit" style="background-color:{color};" title="{row['codigo']}">
                {cantidad}
            </button>
        </form>
        """

    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Mostrar detalle si se seleccionó algo
sku = st.session_state.get('sku_seleccionado')
sector = st.session_state.get('sector_seleccionado')

if sku and sector:
    st.markdown(f"### 🔍 Registros para SKU **{sku}** en sector **{sector}**")
    registros = df[(df['Sector'] == sector) & (df['codigo'] == sku)]
    st.dataframe(registros.reset_index(drop=True), use_container_width=True)
