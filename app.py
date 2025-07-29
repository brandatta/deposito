import streamlit as st
import pandas as pd
import mysql.connector

# Configuración
st.set_page_config(page_title="Mapa del Depósito", layout="wide")
st.title("📦 Mapa visual del Depósito")

# Conexión a MySQL
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
    query = "SELECT * FROM mapa_deposito"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()

# Verificar columnas
if not {'Sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.stop()

# Agrupar por sector
df_summary = df.groupby('Sector').agg({
    'cantidad': 'sum',
    'codigo': lambda x: ', '.join(sorted(set(map(str, x))))
}).reset_index()

# Cantidad de columnas por fila en la grilla
columnas_por_fila = 5

st.subheader("🗺️ Grilla de sectores (disposición visual)")

# Renderizar la grilla como tarjetas en una cuadrícula
for i in range(0, len(df_summary), columnas_por_fila):
    fila = df_summary.iloc[i:i+columnas_por_fila]
    cols = st.columns(columnas_por_fila)
    for j, (_, row) in enumerate(fila.iterrows()):
        with cols[j]:
            st.markdown(f"""
                <div style="
                    border: 2px solid #ccc;
                    border-radius: 10px;
                    padding: 10px;
                    margin: 5px;
                    background-color: #f4faff;
                    text-align: center;
                    min-height: 120px;
                ">
                    <h5 style="margin: 0; color: #444;">{row['Sector']}</h5>
                    <p style="margin: 5px 0;"><strong>Cantidad:</strong> {row['cantidad']}</p>
                    <p style="margin: 0; font-size: 12px;"><strong>Códigos:</strong><br>{row['codigo']}</p>
                </div>
            """, unsafe_allow_html=True)
