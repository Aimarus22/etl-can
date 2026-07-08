#! /usr/bin/env python3

"""
CONTROL DE CALIDAD (QC) - Dataset Calidad del Aire Navarra (2011-2025)
Escáner de flujo de bajo consumo de memoria.
Valida la integridad estructural e imprime cabeceras y colas del archivo.
Aimar Rollán-González
"""

import os
import time
from collections import deque

# ********************************************************
# 1. CONFIGURACIÓN
# ********************************************************

# Usa ruta relativa para que funcione clonando el repositorio
ruta_csv = "./navarra_aqh_2011_2025_facts.csv"

# ********************************************************
# 2. INICIALIZACIÓN
# ********************************************************

total_lineas = 0
errores_estructura = 0
errores_nulos = 0

# Variables para almacenar el "head" (primeras 15) y "tail" (últimas 15)
primeras_lineas = []
ultimas_lineas = deque(maxlen=15)

print("="*60)
print("🔍 INICIANDO AUDITORÍA Y CONTROL DE CALIDAD (QC)")
print("="*60)

if not os.path.exists(ruta_csv):
    print(f"❌ Error: No se encuentra el archivo maestro en {ruta_csv}")
    exit()

print(f"⏳ Escaneando archivo: {os.path.basename(ruta_csv)}")
inicio = time.time()

# ********************************************************
# 3. ESCANEO LÍNEA POR LÍNEA
# ********************************************************

# Emulamos el modo de una consola bash (awk, sed) para leer línea por línea sin saturar la RAM. 

with open(ruta_csv, 'r', encoding='utf-8') as f:
    cabecera = f.readline()
    total_lineas += 1
    primeras_lineas.append(cabecera.strip())
    
    for numero_linea, linea in enumerate(f, start=2):
        total_lineas += 1
        linea_limpia = linea.strip()
        
        # Guardar para el log visual
        if numero_linea <= 16: # Cabecera + 15 datos
            primeras_lineas.append(linea_limpia)
        ultimas_lineas.append(linea_limpia)
        
        # CONTROL 1: Geometría estricta (exactamente 4 comas = 5 columnas)
        if linea_limpia.count(',') != 4:
            errores_estructura += 1
            if errores_estructura <= 5:
                print(f"   ❌ Error estructural en línea {numero_linea}: {linea_limpia}")
            continue 
        
        # CONTROL 2: Integridad relacional (claves no nulas)
        partes = linea_limpia.split(',')
        if not partes[0] or not partes[1] or not partes[2] or not partes[3]:
            errores_nulos += 1
            if errores_nulos <= 5:
                print(f"   ❌ Clave primaria/foránea vacía en línea {numero_linea}: {linea_limpia}")

# ********************************************************
# 4. REPORTE VISUAL 
# ********************************************************

print("\n👁️  INSPECCIÓN VISUAL (Primeras 15 y últimas 15 filas):")
print("-" * 60)
for linea in primeras_lineas:
    print(linea)

print("\n... [ REGISTROS INTERMEDIOS OCULTOS ] ...\n")

for linea in ultimas_lineas:
    print(linea)

# ********************************************************
# 5. INFORME FINAL DE INTEGRIDAD
# ********************************************************

tiempo_total = time.time() - inicio
total_datos = total_lineas - 1

print("\n" + "="*60)
print("📋 REPORTE DE INTEGRIDAD FAIR")
print("="*60)
print(f"⏱️ Tiempo de procesamiento: {tiempo_total:.2f} segundos")
print(f"📊 Total de registros evaluados: {total_datos:,}".replace(',', '.'))
print("-" * 60)

if errores_estructura == 0 and errores_nulos == 0:
    print("✅ ESTADO: APTO PARA PRODUCCIÓN (PASSED)")
    print("   - Geometría de columnas (5 columnas): PERFECTA")
    print("   - Integridad de claves relacionales: PERFECTA")
else:
    print("❌ ESTADO: FALLO DE INTEGRIDAD (FAILED)")
    print(f"   - Filas con número de separadores incorrecto: {errores_estructura}")
    print(f"   - Filas con claves fundamentales vacías: {errores_nulos}")

print("="*60)
