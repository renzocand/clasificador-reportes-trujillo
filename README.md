# Clasificación y priorización automática de reportes ciudadanos

Sistema inteligente que, a partir del texto libre de un reporte ciudadano sobre
infraestructura pública, determina a qué gerencia municipal corresponde derivarlo
y con qué urgencia debe atenderse.

**Curso:** Sistemas Inteligentes y Machine Learning — Universidad Privada del Norte
**Docente:** Dr. Víctor Jaime Polo Romero
**Ciudad de aplicación:** Trujillo, La Libertad, Perú

---

## Aviso sobre los datos

**El corpus es de elaboración propia y simulado.** No existe un repositorio público
y estructurado de reportes ciudadanos de la Municipalidad Provincial de Trujillo en
formato utilizable, por lo que el equipo redactó 500 reportes reproduciendo el
registro informal, las faltas de ortografía y la taxonomía observados en los canales
municipales abiertos.

Las métricas obtenidas deben interpretarse como **cota optimista** y no como el
desempeño esperable en un despliegue real. El script generador se incluye en el
repositorio para que el corpus sea íntegramente reproducible y auditable.

---

## Arquitectura

El sistema combina cuatro capas; tres están implementadas.

| Capa | Función | Estado |
|---|---|---|
| 1. Percepción y representación | Normalización del texto y vectorización TF-IDF | Implementada |
| 2. Aprendizaje | Modelo A (categoría) y Modelo B (prioridad) | Implementada |
| 3. Conocimiento | Reglas de producción sobre la salida del clasificador | Implementada (6 de 8 reglas) |
| 4. Búsqueda | Planificador de la jornada de atención | Trabajo futuro |

La separación entre las capas 2 y 3 responde a un problema concreto: un modelo
estadístico aprende lo frecuente, pero los casos críticos —un cable caído, un buzón
destapado— son raros precisamente por ser críticos. Las reglas cubren ese vacío.

---

## Resultados

### Clasificación por categoría (6 clases)

| Algoritmo | F1 macro | Exactitud |
|---|---|---|
| Naive Bayes | 0,807 | 0,790 |
| **Regresión logística** | **0,847** | 0,840 |

Meta declarada: F1 macro ≥ 0,75. **Cumple.**

### Asignación de prioridad (3 niveles)

| Algoritmo | F1 macro | Recall clase alta |
|---|---|---|
| **Naive Bayes** | **0,759** | **0,878** |
| Regresión logística | 0,755 | 0,829 |

Meta declarada: recall ≥ 0,90 en la clase alta. **No la alcanza la capa de aprendizaje.**

### Efecto de la capa de reglas

| Medición | Resultado |
|---|---|
| Recall en prioridad alta, solo el modelo | 0,878 |
| Recall en prioridad alta, con reglas | **0,951** |

Este es el hallazgo central: la arquitectura híbrida es la que permite alcanzar el
criterio de éxito comprometido.

---

## Estructura

```
.
├── data/
│   └── reportes_ciudadanos_trujillo_2026.csv   Corpus de 500 reportes etiquetados
├── notebooks/
│   ├── 01_modelos_supervisados.ipynb           Pipeline completo y capa de reglas
│   └── 02_modelo_no_supervisado.ipynb          Agrupamiento con K-Means
├── src/
│   └── generar_corpus.py                       Generador del corpus (semilla fija)
└── requirements.txt
```

---

## Cómo ejecutar

### En Google Colab (recomendado)

1. Abrir el notebook desde GitHub: en Colab, `Archivo → Abrir cuaderno → GitHub`
   y pegar la URL de este repositorio.
2. Ejecutar la primera celda. Si el CSV no está presente, el notebook solicita
   subirlo; también puede descargarse directamente agregando esta celda al inicio:

   ```python
   !wget -q https://raw.githubusercontent.com/USUARIO/REPOSITORIO/main/data/reportes_ciudadanos_trujillo_2026.csv
   ```

   (reemplazar `USUARIO/REPOSITORIO` por la ruta real)
3. Ejecutar todas las celdas con `Entorno de ejecución → Ejecutar todas`.

### En local

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_modelos_supervisados.ipynb
```

### Regenerar el corpus

```bash
python src/generar_corpus.py
```

La semilla está fijada en 42, de modo que el CSV resultante es idéntico al incluido
en `data/`.

---

## Decisiones metodológicas

**Partición antes de vectorizar.** El vectorizador TF-IDF se ajusta únicamente sobre
el conjunto de entrenamiento; al conjunto de prueba solo se le aplica la
transformación. Construir el vocabulario con el corpus completo antes de particionar
produce fuga de datos y métricas infladas.

**Dos modelos separados.** Las señales lingüísticas difieren: «poste» determina la
categoría pero no la urgencia; «casi se cae un niño» determina la urgencia pero no
la categoría. Un modelo único con 18 clases combinadas tendría muy pocos ejemplos
por clase.

**F1 macro y recall de la clase alta.** La exactitud global engaña con clases
desbalanceadas. En prioridad, los errores tienen costo asimétrico: sobreestimar la
urgencia de un caso leve cuesta minutos; subestimar la de un caso grave puede costar
un accidente. Ambas metas se fijaron antes de disponer del corpus.

**Ninguna regla puede reducir una prioridad.** Es una salvaguarda ética implementada
como restricción técnica en el motor de inferencia.

**La variable de zona se excluye de las predictoras.** Se reserva para auditar la
equidad territorial del desempeño, no para alimentar el modelo.

---

## Equipo

- Azcarate Noriega, Miguel Alonso
- Candiotti Arancibia, Renzo
- Del Portal Quevedo de la Cruz, Augusto
- Arteaga Sánchez, Heyner Jhonel

Trujillo — La Libertad, Perú · 2026
