# Manimations

Este repositorio sirve como colección central de simulaciones y animaciones de conceptos matemáticos y físicos creadas con [Manim Community Edition](https://www.manim.community/).

## Estructura del Repositorio

El código se encuentra organizado en dos ramas principales:

### 🔬 Investigación
Contiene proyectos y animaciones orientadas a conceptos de materiales e investigación.
- **Barium_Titanate_Crystal/**: Animaciones sobre la caracterización estructural (XRD), graficación de transiciones de fase (permitividad vs temperatura) y efecto geométrico del tamaño de grano en la piezoelectricidad del $BaTiO_3$.
- **SEM_Functionality/**: (En desarrollo)

### 🧮 Matemáticas
Animaciones dedicadas a la ilustración y demostración de conceptos matemáticos y numéricos.
- **Teorema_de_Maclaurin/**: Recopilación de scripts (Calculadoras, demostraciones de convergencia logarítmica y teoremas).
- **Teorema_Euler/**: (En desarrollo)
- **Fourier_Series/**: (En desarrollo)

### 🎨 Assets
- **assets/**: Directorio global diseñado para almacenar recursos comunes que pueden compartirse entre múltiples videos (texturas, efectos de sonido, locuciones, logos corporativos, etc.).

## Requisitos y Modo de Uso

Para compilar los videos localmente en tu máquina, requieres **Python 3** y las dependencias de Manim:
```bash
pip install manim
```

Para renderizar un video, simplemente debes navegar por consola a la carpeta respectiva y usar el compilador de Manim. Por ejemplo:
```bash
cd Investigacion/Barium_Titanate_Crystal
python -m manim -qh script.py -a
```
*(El argumento `-qh` fuerza una renderización de Alta Calidad: 1080p a 60 fps).*
