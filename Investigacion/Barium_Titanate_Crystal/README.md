# Manimations: Titanato de Bario ($BaTiO_3$)

Este repositorio contiene los scripts de [Manim Community Edition](https://www.manim.community/) utilizados para generar videos educativos sobre la **caracterización estructural y térmica del Titanato de Bario** como material piezoeléctrico.

## Requisitos
- Python 3.9+
- Manim Community Edition (`pip install manim`)
- Dependencias de sistema (FFmpeg, Pango, Cairo, LaTeX opcional).

## Escenas Incluidas

El archivo principal es `batio3_video.py`. Contiene tres animaciones clave:

1. **MicroscopyScene**: Explica el impacto del tamaño de grano (< 100 nm vs > 1 μm) al evaluar densificación y piezoelectricidad, ilustrándolo visualmente con dominios cristalinos sobre geometría poligonal.
2. **XRDPhaseScene**: Muestra el desdoblamiento cristalográfico (*splitting*) de la simetría Cúbica (no piezoeléctrico) hacia Tetragonal (piezoeléctrico) a los ~45° (2-THETA).
3. **PhaseTransitionsScene**: Representa una curva térmica de la permitividad y la pérdida de la capacidad piezoeléctrica por encima de la temperatura de Curie (~120 °C).

## ¿Cómo renderizar las animaciones?

Puedes generar los videos en **Alta Calidad (1080p, 60fps)** ejecutando los siguientes comandos en tu terminal dentro de la carpeta:

```bash
# Renderizar las 3 escenas una tras otra automáticamente
python -m manim -qh batio3_video.py -a

# O si deseas renderizarlas de manera manual e individual:
python -m manim -qh batio3_video.py MicroscopyScene
python -m manim -qh batio3_video.py XRDPhaseScene
python -m manim -qh batio3_video.py PhaseTransitionsScene
```

Los videos generados se guardarán automáticamente en `media/videos/batio3_video/1080p60/`. 

## Notas de Desarrollo
En la versión final, las celdas cristalinas de perovskita se modelan usando simulaciones matemáticas de **proyección isométrica 2D nativa**, en lugar de motores de renderización 3D predeterminados de Manim. Esto garantiza que todos los textos, métricas ($a$ y $c$) y gráficas se alineen perfectamente sin superposiciones (z-buffer bugs) en cualquier computadora.
