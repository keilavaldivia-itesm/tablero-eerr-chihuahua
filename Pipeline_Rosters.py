# ============================================================
# PIPELINE AUTOMÁTICO - ROSTERS EERR CHIHUAHUA
# Este script lee el Excel, limpia los datos y actualiza la BD
# ============================================================

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("🚀 INICIANDO PIPELINE DE ROSTERS EERR")
print(f"🕐 Fecha y hora: {datetime.now()}")
print("=" * 60)

# ----------------------------------------------------------
# PASO 1: Leer el archivo Excel
# ----------------------------------------------------------
print("\n📂 PASO 1: Leyendo archivo Excel...")
ruta_archivo = "Copy of 202608 RostersAD26_ CHIHUAHUA.xlsx"

try:
    df = pd.read_excel(ruta_archivo, header=1)
    df = df.iloc[1:].reset_index(drop=True)
    print(f"✅ Leídos {len(df)} atletas correctamente")
except FileNotFoundError:
    print(f"❌ ERROR: No se encontró el archivo '{ruta_archivo}'")
    print("   Asegúrate de que el Excel esté en la misma carpeta que este script.")
    input("Presiona Enter para salir...")
    exit()
except Exception as e:
    print(f"❌ ERROR al leer el Excel: {e}")
    input("Presiona Enter para salir...")
    exit()

# ----------------------------------------------------------
# PASO 2: Limpiar los datos
# ----------------------------------------------------------
print("\n🧹 PASO 2: Limpiando datos...")

# Función para limpiar % de beca
def limpiar_beca(valor):
    if pd.isna(valor):
        return 0
    texto = str(valor).replace('%', '').replace(',', '.').strip()
    if 'y' in texto.lower():
        partes = texto.lower().split('y')
        try:
            return float(partes[0].strip()) + float(partes[1].strip().replace('%', ''))
        except:
            return 0
    try:
        return float(texto)
    except:
        return 0

df['% de Beca'] = df['% de Beca'].apply(limpiar_beca)

# Función para limpiar semestre
def limpiar_semestre(valor):
    if pd.isna(valor):
        return 1
    texto = str(valor).lower()
    texto = texto.replace('°', '').replace('o', '').replace('er', '').replace('to', '')
    texto = texto.replace('sem', '').strip()
    try:
        return int(texto)
    except:
        return 1

df['Semestre FJ26 (Número)'] = df['Semestre FJ26 (Número)'].apply(limpiar_semestre)

# Estandarizar texto
for columna in ['Nivel (Preparatoria / Profesional / Posgrado', 
                'Rama (Femenil, Varonil, Mixto)', 
                'Equipo / Disciplina', 
                'Tipo de Beca']:
    if columna in df.columns:
        df[columna] = df[columna].astype(str).str.strip().str.title()

# Corregir porcentajes (0.4 → 40)
def corregir_porcentaje(valor):
    if pd.isna(valor):
        return 0
    if valor <= 1:
        return valor * 100
    return valor

df['% de Beca'] = df['% de Beca'].apply(corregir_porcentaje)

print("✅ Datos limpiados correctamente")

# ----------------------------------------------------------
# PASO 3: Guardar en la base de datos
# ----------------------------------------------------------
print("\n💾 PASO 3: Guardando en base de datos...")

conexion = sqlite3.connect("rosters_eerr.db")
df.to_sql('roster_ad26', conexion, if_exists='replace', index=False)
print("✅ Datos guardados en la tabla 'roster_ad26'")

# Verificar
consulta = "SELECT COUNT(*) as total FROM roster_ad26"
resultado = pd.read_sql(consulta, conexion)
print(f"📊 Total de atletas en la base de datos: {resultado['total'][0]}")

# Resumen por equipo
consulta2 = """
SELECT "Equipo / Disciplina" as Equipo, 
       "Rama (Femenil, Varonil, Mixto)" as Rama,
       COUNT(*) as Total_Atletas,
       ROUND(AVG("% de Beca"), 1) as Beca_Promedio
FROM roster_ad26 
GROUP BY "Equipo / Disciplina", "Rama (Femenil, Varonil, Mixto)"
ORDER BY Total_Atletas DESC
"""
resumen = pd.read_sql(consulta2, conexion)
print("\n📋 Resumen de atletas por equipo:")
print(resumen.to_string(index=False))

conexion.close()

# ----------------------------------------------------------
# FIN
# ----------------------------------------------------------
print("\n" + "=" * 60)
print("✅ PIPELINE COMPLETADO EXITOSAMENTE")
print(f"🕐 Hora de finalización: {datetime.now()}")
print("=" * 60)
print("\n💡 La base de datos 'rosters_eerr.db' ha sido actualizada.")
input("\nPresiona Enter para cerrar...")