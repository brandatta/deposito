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

# Primeros 3 sectores
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# Colores únicos por SKU
def color_por_codigo(codigo):
    hash_object = hashlib.md5(codigo.encode())
    return '#' + hash_object.hexdigest()[:6]

# Estado inicial
if 'sku_seleccionado' not in st.session_state:
    st.session_state['sku_seleccionado'] = None
    st.session_state['sector_seleccionado'] = None

# CSS
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
    justify-content: center;
}
.sku-button {
    width: 40px;
    height: 40px;
    border-radius: 4px;
    border: none;
    font-weight: bold;
    font-size: 13px;
    color: white;
    cursor: pointer;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)

# Render grilla
st.markdown('<div class="grilla">', unsafe_allow_html=True)

for sector in sectores:
    grupo = df_grouped[df_grouped['Sector'] == sector]

    with st.container():
        st.markdown(f'<div class="sector"><div class="sector-label">{sector}</div><div class="sku-container">', unsafe_allow_html=True)

        for _, row in grupo.iterrows():
            color = color_por_codigo(str(row['codigo']))
            cantidad = int(row['cantidad'])
            form_key = f"form_{sector}_{row['codigo']}"
            with st.form(key=form_key):
                submit = st.form_submit_button(
                    label=str(cantidad),
                    help=f"SKU: {row['codigo']}",
                    use_container_width=False
                )
                if submit:
                    st.session_state['sku_seleccionado'] = row['codigo']
                    st.session_state['sector_seleccionado'] = sector
                st.markdown(f"""
                <style>
                [data-testid="stForm"] button {{
                    background-color: {color};
                    width: 40px;
                    height: 40px;
                    border-radius: 4px;
                    border: none;
                    color: white;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 0;
                    margin: 0;
                }}
                </style>
                """, unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Mostrar detalles si hay selección
sku = st.session_state.get('sku_seleccionado')
sector = st.session_state.get('sector_seleccionado')

if sku and sector:
    st.markdown(f"### 🔍 Registros para SKU **{sku}** en sector **{sector}**")
    registros = df[(df['Sector'] == sector) & (df['codigo'] == sku)]
    st.dataframe(registros.reset_index(drop=True), use_container_width=True)
