#! /usr/bin/env python3

"""
AUDITORÍA PREVIA AL ETL - Dataset Calidad del Aire Navarra (2011-2025)
Escaneo de archivos y cabeceras.
Aimar Rollán-González

"""

import pandas as pd
import glob
import os

# ********************************************************
# 1. CONFIGURACIÓN DE CARPETAS 
# ********************************************************

# Lo primero de todo es descargar los 149 archivos dispersos en la web de Datos Abiertos de Navarra en carpetas agrupadas por estación, verificar que se han descargado todos los años y cambiar el nombre de archivo por el del año en cuestión. También asignarles un número id de estación arbitrario (por orden alfabético). Esta parte se podría optimizar y establecer un protocolo de extracción directa desde la web de Datos Abiertos de Navarra (web scraping), pero he decidido hacerlo así en este proyecto, priorizando el "data discovery" y el pragmatismo (me iba a llevar más tiempo desarrollar el script que hacer la descarga manual de esta serie de datos históricos cerrados). 

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

ruta_salida_auditoria = "./audit_headers_navarra_aqh_2011_2025.csv"

# ********************************************************
# 2. PROCESAMIENTO Y EXTRACCIÓN
# ********************************************************

datos_archivos = []

print("🔍 Escaneando cabeceras archivo por archivo...\n")

for carpeta, id_station in estaciones_dict.items():
    if not os.path.exists(carpeta):
        print(f"⚠️ No se encuentra la carpeta: {carpeta}")
        continue
        
    archivos_csv = glob.glob(os.path.join(carpeta, "*.csv"))
    
    for archivo in archivos_csv:
        try:
            # nrows=0 es vital para que Pydroid no consuma RAM, solo lee la primera fila. También valido para python3 normal en un PC potente o no. 
            df_temp = pd.read_csv(archivo, sep=',', nrows=0, encoding='utf-8')
            columnas = df_temp.columns.tolist()
            
            # Guardamos la información de este archivo concreto. 
            datos_archivos.append({
                "id_station": id_station,
                "carpeta": os.path.basename(carpeta),
                "nombre_archivo": os.path.basename(archivo),
                "num_variables": len(columnas),
                "variables_detectadas": ", ".join(columnas)
            })
            
        except Exception as e:
            print(f"❌ Error leyendo cabecera de {archivo}: {e}")

# ********************************************************
# 3. CREACIÓN DEL CSV DE AUDITORÍA
# ********************************************************

if datos_archivos:
    df_auditoria = pd.DataFrame(datos_archivos)
    
    # Ordenamos por estación y luego por nombre de archivo (año). 
    df_auditoria = df_auditoria.sort_values(by=["id_station", "nombre_archivo"])
    
    df_auditoria.to_csv(ruta_salida_auditoria, index=False, sep=',', encoding='utf-8')
    
    print(f"✅ ¡Auditoría completada con éxito! Se escanearon {len(datos_archivos)} archivos.")
    print(f"💾 El reporte detallado se ha guardado en: {ruta_salida_auditoria}")
else:
    print("❌ No se procesó ningún archivo válido. Comprueba que las rutas existen y tienen archivos .csv dentro.")
