# Calidad del Aire en Navarra (2011-2025): Pipeline ETL y Curación de Datos
 * Autor: Aimar Rollán-González | Investigador Independiente
 * ORCID: https://orcid.org/0009-0005-2969-1006
 * Disponibilidad del código: https://github.com/Aimarus22/etl-can
 * Fecha: Jun 2026
Abstract:
Un pipeline de datos donde la información fragmentada se encuentra con el orden relacional. Aquí, 15 años históricos de contaminación atmosférica se codifican en un esquema en estrella bajo la filosofía Tidy Data.
Keywords: Data Engineering, ETL, Tidy Data, Python, Open Data, Air Quality
## Disponibilidad de los Datos (Zenodo)
Este repositorio de GitHub aloja exclusivamente el código fuente (scripts Python) de la arquitectura ETL y de auditoría. Las matrices de datos resultantes en formato abierto .csv (incluyendo la tabla de hechos con ~8,3 millones de registros y las tablas de dimensiones) se encuentran publicadas y versionadas en Zenodo para su descarga:
👉 **[Base de datos histórica de calidad del aire en Navarra (2011-2025)] (https://doi.org/10.5281/zenodo.)**
### Fase I: La topología de la auditoría
Antes de transformar, es necesario comprender el caos. El script audit_headers_navarra_aqh_2011_2025.py actúa como un escáner previo. Su único propósito es mirar los 149 archivos en crudo y extraer sus cabeceras sin saturar la memoria, utilizando una lectura superficial (nrows=0) para mapear las variables detectadas.
### Fase II: El motor de transformación
Para estructurar esta asimetría original, invocamos al núcleo del proyecto: etl_navarra_aqh_2011_2025.py.
 * **Su función:** Transposición estricta mediante *unpivot* para lograr simetría en todas las filas (Tidy Data).
 * **Su traducción:** Reemplazo de nomenclaturas químicas y metadatos locales por códigos numéricos internacionales de la Agencia Europea de Medio Ambiente (EIONET) y reemplazo de comas por puntos flotantes.
 * **Su exigencia:** Mantener una política de "no supresión" para los fallos físicos de los sensores, pero purgando implacablemente los registros huérfanos sin marca de tiempo válida.
### Fase III: El guardián de la integridad
Existe una frontera donde los datos mal formados prohíben el análisis. Definimos el script qc_navarra_aqh_2011_2025.py como un escáner de flujo de bajo consumo.
Incapaz de saturar la RAM, este guardián lee el archivo maestro línea por línea emulando herramientas de consola bash. Valida la geometría estricta de 5 columnas y asegura que ninguna clave relacional esté vacía antes de declarar el archivo apto para producción.
## El lienzo ejecutable pydroidiano
Para atestiguar la transformación estructural de millones de registros, los scripts se encuentran en la raíz de este repositorio.
Puedes invocar la curación clonando este repositorio y ejecutando los scripts desde tu terminal en este orden estricto:
```bash
python audit_headers_navarra_aqh_2011_2025.py
python etl_navarra_aqh_2011_2025.py
python qc_navarra_aqh_2011_2025.py

```
**Instrucciones para la ejecución material:** Se recomienda encarecidamente probar la ejecución de etl_navarra_aqh_2011_2025.py dentro del entorno confinado de **Pydroid 3** en un dispositivo móvil. El código ha sido optimizado con liberación de memoria iterativa (gc.collect()) para procesar la historia atmosférica de Navarra en apenas 25 minutos desde un hardware modesto, demostrando que no hacen falta equipos costosos para el procesamiento masivo de datos.
## Declaración Ética sobre el Uso de Inteligencia Artificial
En consonancia con las políticas de transparencia tecnológica y ciencia abierta, se declara el uso de herramientas de Inteligencia Artificial (específicamente **Gemini Pro**) durante el desarrollo de este repositorio. Su asistencia se limitó a tareas de amplificación cognitiva, formateo de la documentación y asistencia en la escritura (*picado*) del código ejecutable.
La arquitectura del *pipeline*, la lógica conceptual de reducción de memoria, la política de preservación de datos y la validación metodológica son autoría y responsabilidad exclusiva del investigador principal. En ningún caso, el modelo fundacional de IA ha generado, alterado o "alucinado" los datos empíricos del registro atmosférico.
## CRediT (Contributor Roles Taxonomy)
 * Aimar Rollán-González: Conceptualización, Metodología, Investigación, Software, Recursos, Curación de datos, Validación, Redacción - borrador original, Redacción - revisión y edición.
## Licencias
 * **MIT**, para los 3 scripts de código en Python alojados en este repositorio.
 * **CC-BY 4.0**, para el conjunto de datos final alojado en el repositorio de Zenodo.
