import streamlit as st
import pandas as pd
import mysql.connector
import hashlib

# Configuración
st.set_page_config(page_title="Mapa del Depósito Visual", layout="wide")
st.title("📦 Plano del Depósito con SKUs y cantidades")

# Conexión
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

# Primeros 3 sectores
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y SKU
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Color único por código
def color_por_codigo(codigo):
    hex_color = hashlib.md5(codigo.encode()).hexdigest()[:6]
    return f"#{hex_color}"

# Estado inicial
if 'sku_seleccionado' not in st.session_state:
    st.session_state['sku_seleccionado'] = None
    st.session_state['sector_seleccionado'] = None

# Estilos básicos
st.markdown("""
<style>
.sector-box {
    border: 2px solid black;
    border-radius: 6px;
    background-color: white;
    padding: 10px;
    width: 130px;
    height: 130px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.sku-button {
    border: none;
    color: white;
    font-weight: bold;
    font-size: 13px;
    width: 40px;
    height: 40px;
    border-radius: 4px;
    margin: 2px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# Grilla de sectores
cols = st.columns(len(sectores))
for i, sector in enumerate(sectores):
    grupo = df_grouped[df_grouped['Sector'] == sector]

    with cols[i]:
        st.markdown(f'<div class="sector-box"><div style="font-weight:bold; font-size:13px; margin-bottom:6px;">{sector}</div>', unsafe_allow_html=True)

        # Cuadraditos SKU como botones
        for _, row in grupo.iterrows():
            color = color_por_codigo(str(row['codigo']))
            button_label = str(int(row['cantidad']))
            button_key = f"{sector}_{row['codigo']}"
            if st.button(button_label, key=button_key):
                st.session_state['sku_seleccionado'] = row['codigo']
                st.session_state['sector_seleccionado'] = sector
            st.markdown(
                f"""
                <style>
                [data-testid="baseButton-secondary"]#{button_key} {{
                    background-color: {color} !important;
                    color: white !important;
                    width: 40px !important;
                    height: 40px !important;
                    border-radius: 4px !important;
                    margin: 2px;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

# Mostrar detalle si se hizo clic
sku = st.session_state.get('sku_seleccionado')
sector = st.session_state.get('sector_seleccionado')

if sku and sector:
    st.markdown(f"### 🔍 Registros para SKU **{sku}** en sector **{sector}**")
    registros = df[(df['Sector'] == sector) & (df['codigo'] == sku)]
    st.dataframe(registros.reset_index(drop=True), use_container_width=True)
