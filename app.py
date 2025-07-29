import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import numpy as np

# Configuración de la app
st.set_page_config(page_title="Mapa del Depósito", layout="wide")
st.title("📦 Mapa del Depósito")

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

# Validar columnas necesarias
if not {'sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: sector, cantidad, codigo")
    st.stop()

# Agrupar por sector (sumar cantidad)
df_agg = df.groupby('sector', as_index=False).agg({'cantidad': 'sum'})

# Crear una grilla visual
st.subheader("🗺️ Grilla del depósito")

# Generar coordenadas de la grilla desde los nombres de sectores
# Suponiendo que los sectores sean tipo A1, A2, B1, B2, etc.
def parse_sector(sector):
    try:
        fila = ord(sector[0].upper()) - ord('A')
        columna = int(sector[1:]) - 1
        return fila, columna
    except:
        return None, None

df_agg[['fila', 'col']] = df_agg['sector'].apply(lambda s: pd.Series(parse_sector(s)))

max_fila = df_agg['fila'].max()
max_col = df_agg['col'].max()

# Crear matriz vacía para la grilla
matriz = np.full((max_fila + 1, max_col + 1), '', dtype=object)

# Rellenar la grilla
for _, row in df_agg.iterrows():
    if pd.notna(row['fila']) and pd.notna(row['col']):
        matriz[int(row['fila']), int(row['col'])] = str(int(row['cantidad']))

# Mostrar como tabla
st.write("🔢 Cantidades por sector:")
st.dataframe(pd.DataFrame(matriz), use_container_width=True)
