import streamlit as st
import pandas as pd
import mysql.connector

# Configuración general
st.set_page_config(page_title="Mapa del Depósito", layout="wide")
st.title("📦 Plano del Depósito - 1 Fila x 3 Columnas")

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

# Agrupar por sector y mostrar los primeros 3 únicos
df_summary = df.groupby('Sector').agg({
    'cantidad': 'sum',
    'codigo': lambda x: ', '.join(sorted(set(map(str, x))))
}).reset_index()

# Tomar los primeros 3 sectores reales de la tabla
df_grilla = df_summary.head(3)

# HTML para formato grilla limpia
st.markdown("""
<style>
    .grilla {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        border: 2px solid black;
        margin-top: 20px;
    }
    .celda {
        border: 1px solid black;
        padding: 15px;
        text-align: center;
        font-family: sans-serif;
        background-color: #fff;
    }
    .titulo {
        font-weight: bold;
        font-size: 16px;
    }
    .cantidad {
        margin-top: 5px;
        font-size: 14px;
    }
    .codigo {
        margin-top: 5px;
        font-size: 12px;
    }
</style>
<div class="grilla">
""", unsafe_allow_html=True)

# Renderizar cada celda sin errores si hay datos faltantes
for _, row in df_grilla.iterrows():
    sector = row['Sector'] if pd.notna(row['Sector']) else 'Sin nombre'
    cantidad = int(row['cantidad']) if pd.notna(row['cantidad']) else 0
    codigos = row['codigo'] if pd.notna(row['codigo']) and row['codigo'] else 'Sin productos'

    st.markdown(f"""
    <div class="celda">
        <div class="titulo">{sector}</div>
        <div class="cantidad">Cantidad: {cantidad}</div>
        <div class="codigo">Códigos:<br>{codigos}</div>
    </div>
    """, unsafe_allow_html=True)

# Cerrar contenedor
st.markdown("</div>", unsafe_allow_html=True)
