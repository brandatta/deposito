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

# Renombrar columna Sector a 'sector' para consistencia interna
df.rename(columns={"Sector": "sector"}, inplace=True)

# Verificar columnas necesarias
if not {'sector', 'cantidad', 'codigo'}.issubset(df.columns):
    st.error("La tabla debe tener las columnas: Sector, cantidad, codigo")
    st.write("Columnas actuales:", df.columns.tolist())
    st.stop()

# Agrupar por sector, sumar cantidades
df_agg = df.groupby('sector', as_index=False).agg({'cantidad': 'sum'})

# Función para convertir sector tipo A1, B2, etc. en coordenadas de grilla
def parse_sector(sector):
    try:
        fila = ord(sector[0].upper()) - ord('A')
        columna = int(sector[1:]) - 1
        return fila, columna
    except:
        return None, None

# Aplicar conversión
df_agg[['fila', 'col']] = df_agg['sector'].apply(lambda s: pd.Series(parse_sector(s)))

# Definir dimensiones máximas de la grilla
max_fila = df_agg['fila'].max()
max_col = df_agg['col'].max()

# Crear matriz vacía
matriz = np.full((max_fila + 1, max_col + 1), '', dtype=object)

# Rellenar la matriz con cantidades
for _, row in df_agg.iterrows():
    if pd.notna(row['fila']) and pd.notna(row['col']):
        matriz[int(row['fila']), int(row['col'])] = str(int(row['cantidad']))

# Mostrar como tabla
st.subheader("🗺️ Grilla del depósito")
st.dataframe(pd.DataFrame(matriz), use_container_width=True)
