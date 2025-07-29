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

# Validación
if not {'Sector', 'cantidad', 'codigo', 'descripcion'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo, descripcion")
    st.stop()

# Inicializar estado del modal
if "modal_sku" not in st.session_state:
    st.session_state.modal_sku = None
    st.session_state.modal_sector = None
    st.session_state.modal_open = False

# Función para color único por SKU
def color_por_codigo(codigo):
    return "#" + hashlib.md5(codigo.encode()).hexdigest()[:6]

# Filtrar primeros 3 sectores
sectores = df['Sector'].dropna().unique()[:3]
df = df[df['Sector'].isin(sectores)]

# Agrupar por sector y SKU
df_grouped = df.groupby(['Sector', 'codigo'], as_index=False)['cantidad'].sum()

# CSS para hacer todo más compacto
st.markdown("""
<style>
.sku-button {
    width: 40px !important;
    height: 40px !important;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    color: white !important;
    margin: 3px 3px 0 0;
    padding: 0 !important;
}
.sector-box {
    border: 2px solid black;
    border-radius: 6px;
    padding: 10px;
    background-color: white;
    height: 160px;
}
.sector-title {
    font-weight: bold;
    font-size: 14px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Mostrar grilla
cols = st.columns(3)
for idx, sector in enumerate(sectores):
    with cols[idx]:
        st.markdown(f"<div class='sector-box'><div class='sector-title'>{sector}</div>", unsafe_allow_html=True)

        grupo = df_grouped[df_grouped['Sector'] == sector]
        for _, row in grupo.iterrows():
            color = color_por_codigo(str(row['codigo']))
            cantidad = int(row['cantidad'])
            key = f"{sector}_{row['codigo']}"
            btn = st.button(
                str(cantidad),
                key=key,
                help=f"{row['codigo']}",
            )
            st.markdown(
                f"""
                <style>
                button[data-testid="baseButton-{key}"] {{
                    background-color: {color} !important;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )
            if btn:
                st.session_state.modal_sku = row['codigo']
                st.session_state.modal_sector = sector
                st.session_state.modal_open = True

        st.markdown("</div>", unsafe_allow_html=True)

# MODAL
if st.session_state.modal_open:
    sku = st.session_state.modal_sku
    sector = st.session_state.modal_sector
    registros = df[(df['Sector'] == sector) & (df['codigo'] == sku)]

    with st.container():
        with st.expander(f"🔍 Registros para SKU **{sku}** en sector **{sector}**", expanded=True):
            st.write("Descripción de registros:")
            st.dataframe(registros[['descripcion']], use_container_width=True)
            if st.button("❌ Cerrar modal"):
                st.session_state.modal_open = False
