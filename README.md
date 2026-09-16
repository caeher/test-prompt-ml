# Proyecto de detección de discurso de odio

Este repositorio contiene la preparación del dataset y el prototipo funcional de un modelo de clasificación para detectar toxicidad y discurso de odio en español.

## Estructura del proyecto

```text
entrenamientos/
├── README.md
├── 01_dataset_y_entrenamiento/
│   ├── data/
│   │   ├── train.csv
│   │   ├── val.csv
│   │   ├── test.csv
│   │   └── corpus_limpio.csv
│   ├── notebooks/
│   ├── results_xlmr/
│   └── venv/
├── 02_modelo_prototipo/
│   ├── modelo_entrenado/
│   │   ├── config.json
│   │   ├── model.safetensors
│   │   ├── tokenizer.json
│   │   ├── tokenizer_config.json
│   │   └── training_args.bin
│   ├── documentacion/
│   ├── estadisticas.ipynb
│   ├── inferencia.py
│   ├──Imagenes de utilidad/
└── (archivos adicionales de métricas)
```

## Qué hace cada carpeta

- 01_dataset_y_entrenamiento: contiene el dataset, notebooks de entrenamiento y artefactos relacionados con la preparación de datos.
- 02_modelo_prototipo: contiene el modelo ya entrenado listo para inferencia, junto con sus métricas y el script de prueba.
- hateV1_modelo_xlmr.zip: zip opcional del modelo o paquete de entrega.

## Requisitos

- Python 3.10 o superior
- Pip
- Entorno virtual recomendado

### Dependencias principales

```bash
pip install torch transformers
```

Si necesitas versión más específica según tu entorno, puedes instalar adicionalmente:

```bash
pip install pandas numpy scikit-learn
```

## Cómo ejecutar la inferencia

1. Abre una terminal en la carpeta principal del proyecto.
2. Activa tu entorno virtual si lo usas.
3. Dirígete a la carpeta del prototipo:

```bash
cd 02_modelo_prototipo
```

4. Ejecuta el script:

```bash
python inferencia.py
```

## Qué hace el script

- Carga el tokenizador y el modelo ya entrenado.
- Detecta automáticamente si se usa la GPU o la CPU.
- Evalúa frases de ejemplo.
- Permite ingresar textos manualmente en modo interactivo.

## Etiquetas del modelo

El modelo clasifica en estas 4 categorías:

- No Tóxico
- Lenguaje Ofensivo
- Discurso de Odio
- Amenazas/Violencia

## Ejemplo de uso interactivo

```text
Texto > Ese maje no sabe lo que está haciendo
-> Clasificación: Lenguaje Ofensivo (83.21%)
```

## Notas importantes

- El modelo entrenado se encuentra en la ruta: 02_modelo_prototipo/modelo_entrenado
- Si por alguna razón no se encuentra esa carpeta, el script intenta compatibilidad con una ruta vieja llamada mi_modelo_xlmr
- La inferencia se hace por CPU por defecto si no hay GPU disponible

## Si quieres reutilizarlo en otra máquina

1. Copia la carpeta 02_modelo_prototipo completa.
2. Asegúrate de mantener la estructura interna de modelo_entrenado.
3. Ejecuta el script desde esa carpeta.

## Contacto / mantenimiento

Este proyecto está pensado como prototipo funcional para pruebas y validación interna. Si se quiere mantener o desplegar en producción, se recomienda:

- revisar el dataset de entrenamiento,
- validar con más ejemplos reales,
- documentar la política de clasificación,
- y revisar la métrica final del modelo antes de uso operativo.
