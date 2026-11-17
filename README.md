# Análisis Semántico Latente (LSA) sobre Reseñas de Videojuegos en Steam

**Curso:** Álgebra Lineal Avanzada y Modelamiento (IMT2230) — Pontificia Universidad Católica de Chile  
**Autor:** Benjamín Quijada  

Este repositorio contiene el código, los datos reproducibles y las visualizaciones para aplicar **Análisis Semántico Latente (LSA)** mediante **Descomposición en Valores Singulares (SVD)** sobre una matriz término-documento construida a partir de 240 reseñas públicas de videojuegos en Steam.

---

## Estructura del repositorio

```text
.
├── data/
│   └── steam_reviews.csv          # Corpus de 240 reseñas (60 por juego)
├── figures/
│   ├── singular_values.png        # Espectro de valores singulares y energía acumulada
│   ├── docs_2d.png                # Proyección 2D de documentos en Span(u1, u2) y Span(u2, u3)
│   └── terms_2d.png               # Proyección 2D de términos en Span(v2, v3)
├── report/
│   ├── informe.html               # Versión HTML del informe académico
│   └── informe.tex                # Fuente LaTeX (para Overleaf)
├── download_data.py               # Script reproducible de descarga desde GitHub
├── lsa_steam_reviews.ipynb        # Notebook principal con los 9 pasos del análisis
├── Informe_Proyecto_LSA_Benjamin_Quijada.pdf  # Informe final en PDF
├── requirements.txt               # Dependencias de Python
└── README.md
```

---

## Fuente de los datos

El corpus se construyó a partir del repositorio público [`mulhod/steam_reviews`](https://github.com/mulhod/steam_reviews) en GitHub (archivos `.jsonlines` con reseñas reales de usuarios de Steam).

Se seleccionaron **60 reseñas sustanciales en inglés** (entre 300 y 3000 caracteres) de 4 títulos pertenecientes a géneros contrastantes (**240 documentos en total**):

| Videojuego | Género | Documentos | Palabras promedio |
|---|---|---:|---:|
| *The Elder Scrolls V: Skyrim* | RPG / Fantasy | 60 | 180.2 |
| *Sid Meier's Civilization V* | Strategy 4X | 60 | 183.2 |
| *Counter-Strike: Global Offensive* | Tactical FPS | 60 | 190.8 |
| *Football Manager 2015* | Sports Sim | 60 | 206.9 |

---

## Cómo ejecutar y reproducir los resultados

1. **Clonar el repositorio** e instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. **(Opcional) Volver a descargar el corpus** desde la fuente pública:
   ```bash
   python download_data.py
   ```
   *(El archivo `data/steam_reviews.csv` ya se incluye en el repositorio para garantizar reproducibilidad exacta.)*

3. **Ejecutar el notebook completo** en Jupyter o Google Colab:
   ```bash
   jupyter notebook lsa_steam_reviews.ipynb
   ```
   O ejecutarlo por línea de comandos para regenerar las figuras en `figures/`:
   ```bash
   jupyter nbconvert --to notebook --execute --inplace lsa_steam_reviews.ipynb
   ```
