#! /usr/bin/env python3

"""
PIPELINE ETL - Dataset Calidad del Aire Navarra (2011-2025). 
Transformación a Modelo Relacional (Estrella) / Formato Tidy Data.
Aimar Rollán-González

"""

import pandas as pd
import glob
import os
import re
import warnings
import gc

# Ignorar advertencias de rendimiento de Pandas al concatenar masivamente
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# ********************************************************
# 1. CONFIGURACIÓN DE CARPETAS Y SALIDA
# ********************************************************

# Se supone que ya hemos descargado los 149 csv para nuestra fase previa de auditoría y los tenemos descargados en las siguientes rutas relativas. 

estaciones_dict = {
    "./Alsasua_id1": 1,
    "./Arguedas_id2": 2,
    "./Funes_id3": 3,
    "./Leiza_id4": 4,
    "./Lesaka_id5": 5,
    "./Olite_id6": 6,
    "./Pamplona_Felisa_Munarriz_id7": 7,
    "./Pamplona_Iturrama_id8": 8,
    "./Pamplona_Plaza_de_la_Cruz_id9": 9,
    "./Pamplona_Rotxapea_id10": 10,
    "./Sangüesa_id11": 11,
    "./Tudela_Canraso_id12": 12,
    "./Tudela_Centro_id13": 13,
    "./UPNA_id14": 14
}

ruta_salida_final = "./navarra_aqh_2011_2025_facts.csv"

# ********************************************************
# 2. FUNCIÓN DE ESTANDARIZACIÓN 
# ********************************************************
def estandarizar_contaminante_eionet(col_name):
    name = str(col_name).upper().strip()
    
    # Excluir fechas y metadatos del sistema
    if 'FECHA' in name or name in ['_ID', 'ID']:
        return None

    # Contaminantes principales y cambio a números según diccionario de datos de EIONET (Red Europea de Información y Observación del Medio Ambiente). Orden estricto en la secuencia de "ifs", 'NO' ha de escanearse el último.
    if 'NO2' in name: return 8
    if 'NOX' in name: return 9
    if 'SO2' in name: return 1
    if 'O3' in name or 'OZONO' in name: return 7
    if 'PM2.5' in name or 'PM2,5' in name: return 6001
    if 'PM10' in name: return 5
    if re.search(r'\bPM1\b', name) or 'PM1(' in name: return 6002 
    if 'CO' in name: return 10
    if 'BENCENO' in name: return 20
    if 'TOLUENO' in name: return 21
    if 'XILENO' in name: return 78
    if re.search(r'\bNO\b', name) or name.endswith('NO'): return 38
        
    return None

# ********************************************************
# 3. EXTRACCIÓN, TRANSFORMACIÓN Y CARGA 
# ********************************************************

#Optimizado para Pydroid3 y dispositivos móviles o computadores de baja capacidad, para demostrar que no hacen falta equipos costosos para procesar millones de filas. El archivo final subido a Zenodo ha sido procesado desde un móvil Android modesto en el primer intento, en aproximadamente 25 minutos, sin freirse. 

print("--- INICIANDO PROCESAMIENTO ETL DE 149 ARCHIVOS ---")

contador_global_id = 1
primer_guardado = True

for carpeta, id_station in estaciones_dict.items():
    if not os.path.exists(carpeta):
        print(f"⚠️ Aviso: La carpeta '{carpeta}' no existe. Saltando...")
        continue
        
    archivos_csv = glob.glob(os.path.join(carpeta, "*.csv"))
    if not archivos_csv:
        continue
        
    print(f"📁 Procesando Estación ID {id_station} - {len(archivos_csv)} archivos encontrados...")
    
    lista_estacion_temporal = []
    
    for archivo in archivos_csv:
        try:
            df = pd.read_csv(archivo, sep=',', decimal=',', encoding='utf-8')
        except Exception as e:
            print(f"❌ Error leyendo {os.path.basename(archivo)}: {e}. Saltando...")
            continue
            
        # Detectar columna de fecha dinámicamente
        cols_fecha_detectadas = [c for c in df.columns if 'FECHA' in str(c).upper()]
        if not cols_fecha_detectadas:
            continue
        col_fecha = cols_fecha_detectadas[0]
        
        # Resolución del conflicto PM10 vs PM10R
        cols_pm10 = [c for c in df.columns if 'PM10' in str(c).upper() and 'PM10R' not in str(c).upper()]
        cols_pm10r = [c for c in df.columns if 'PM10R' in str(c).upper()]
        
        if len(cols_pm10r) > 0:
            if len(cols_pm10) > 0:
                df = df.drop(columns=cols_pm10)
            df = df.rename(columns={cols_pm10r[0]: 'PM10'})
            
        # Renombrar columnas a códigos EIONET y la fecha a 'timestamp'
        renombrar = {col_fecha: 'timestamp'}
        for c in df.columns:
            if c == col_fecha or str(c).upper() in ['_ID', 'ID']:
                continue
            std_p = estandarizar_contaminante_eionet(c)
            if std_p is not None:
                renombrar[c] = std_p
                
        # Mantener solo las columnas útiles
        cols_a_mantener = [col_fecha] + [c for c in df.columns if c in renombrar and c != col_fecha]
        df = df[cols_a_mantener].copy()
        df = df.rename(columns=renombrar)
        
        # Limpieza de coma a punto flotante
        for col in df.columns:
            if col != 'timestamp':
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(',', '.', regex=False).str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # Estructura Tidy Data (Modelo Largo Relacional)
        df_largo = df.melt(
            id_vars=['timestamp'], 
            value_vars=[c for c in df.columns if c != 'timestamp'], 
            var_name='pollutant', 
            value_name='value'
        )
        
        df_largo['pollutant'] = df_largo['pollutant'].astype(int)
        df_largo['id_station'] = id_station
        
        if not df_largo.empty:
            lista_estacion_temporal.append(df_largo)
            
    # --- PROCESAR, GUARDAR Y VACIAR RAM (ESTACIÓN POR ESTACIÓN) ---
    if lista_estacion_temporal:
        df_estacion = pd.concat(lista_estacion_temporal, ignore_index=True)
        
        # ESTÁNDAR 1: Parsear fechas. Si hay basura o texto, se convierte en NaT (Not a Time)
        df_estacion['timestamp'] = pd.to_datetime(df_estacion['timestamp'], format='mixed', dayfirst=True, errors='coerce')
        
        # ESTÁNDAR 2: Eliminar huérfanos temporales. Purga todas las filas donde la fecha no se pudo leer, pies de página o vacíos.
        df_estacion = df_estacion.dropna(subset=['timestamp'])
        
        # Ordenación final (los valores nulos en 'value' se mantienen por la "política de no supresión")
        df_estacion = df_estacion.sort_values(by=['timestamp', 'pollutant']).reset_index(drop=True)
        
        # Generar clave primaria unificada y correlativa
        df_estacion.insert(0, 'id', range(contador_global_id, contador_global_id + len(df_estacion)))
        contador_global_id += len(df_estacion)
        
        # Ordenación final de variables con los nombres requeridos
        df_estacion = df_estacion[['id', 'timestamp', 'id_station', 'pollutant', 'value']]
        
        # Guardado incremental en CSV maestro
        modo = 'w' if primer_guardado else 'a'
        encabezado = True if primer_guardado else False
        
        df_estacion.to_csv(ruta_salida_final, mode=modo, header=encabezado, index=False, sep=',', decimal='.', encoding='utf-8', date_format='%Y-%m-%d %H:%M:%S')
        
        primer_guardado = False
        print(f"   ✅ Guardados {len(df_estacion)} registros purgados de la Estación {id_station}. Total acumulado: {contador_global_id - 1}")
        
        # Liberación de memoria 
        del df_estacion
        del lista_estacion_temporal
        gc.collect()

print("\n🚀 ¡PROCESO ETL COMPLETADO CON ÉXITO!")
print(f"💾 El dataset maestro se ha generado en:\n   {ruta_salida_final}")
