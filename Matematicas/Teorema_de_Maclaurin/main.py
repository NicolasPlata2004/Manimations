# main.py

'''
Para escribir formula tipo latex sin maquinarle mucho:
https://editor.codecogs.com/
'''

'''
Para hacer saltos de linea...
Text: \n
Tex: \\
MathTex: aligned + \\
'''

r"""
Como renderizar solo una parte del codigo:
os aseguramos estar en poweshell o terminal

Luego en la carpeta correcta
cd C:\Users\nicao\manimations

Activamos el entorno
.\.venv\Scripts\Activate.ps1

y renderizamos
python -m manim -pql main.py demo -n "5,10" -o demo.mp4

El 5 y 10 pueden ser ajustados

OJOOOOO: Cada animation corresponde a cada self.play y self.wait
"""

import math
import numpy as np
from manim import *

# Para audio
import wave              # duración de WAV PCM (frames / framerate)
import os                # rutas y verificación de archivos


# ==========================
# CONFIG: carpeta de audios
# ==========================
AUDIO_DIR = r"C:\Users\nicao\manimations\Audios\SegundoVideo"

# Nombres de audios (deben existir dentro de AUDIO_DIR)
AUDIO_1 = "01.wav"
AUDIO_2 = "02.wav"
AUDIO_3 = "03.wav"
AUDIO_4 = "04.wav"
AUDIO_5 = "05.wav"
AUDIO_6 = "06.wav"
AUDIO_7 = "07.wav"
AUDIO_8 = "08.wav"
AUDIO_8_1 = "08_1.wav"
AUDIO_9 = "09.wav"
AUDIO_10 = "10.wav"
AUDIO_11 = "11.wav"
AUDIO_12 = "12.wav"
AUDIO_13 = "13.wav"
AUDIO_14 = "14.wav"



# ==========================
# DURACIÓN WAV
# ==========================
def audio_duration_wav(path: str) -> float:
    """
    Duración (segundos) de un .wav PCM usando la librería estándar wave.
    duration = nframes / framerate
    """
    with wave.open(path, "rb") as w:
        frames = w.getnframes()
        rate = w.getframerate()
        return frames / float(rate)


class demo(Scene):

    # =========================================================================
    # (A) MATEMÁTICA: Polinomio de Maclaurin para e^x
    # =========================================================================
    def maclaurin_exp(self, x: float, n: int) -> float:
        """
        Polinomio de Maclaurin de e^x:
        P_n(x) = sum_{k=0}^n x^k / k!
        """
        return sum((x**k) / math.factorial(k) for k in range(n + 1))

    # =========================================================================
    # (B) AUDIO: utilidades
    # =========================================================================
    def _audio_path(self, filename: str) -> str:
        """
        Devuelve ruta absoluta del audio y verifica existencia.
        Si no existe, levanta error claro para que no “falle silencioso”.
        """
        path = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No existe el audio: {path}")
        return path

    def play_audio_over_animations(
        self,
        filename: str,
        *steps,
        extra_wait: float = 0.15,
        gain: float = 1.0,
    ):
        """
        Reproduce UN audio y encima ejecuta VARIOS pasos en secuencia.

        Cada step (paso) es un dict con UNA de estas dos formas:

        A) Paso con animación:
           {
             "anim": una animación (ej: FadeIn(obj))
                     o una lista/tupla de animaciones (ej: [Write(a), Write(b)]),
             "run_time": duración del self.play en segundos,
             ... opcional: kwargs extra para self.play (rate_func, lag_ratio, etc.)
           }

        B) Paso de espera (pausa mientras el audio sigue):
           { "wait": segundos }

        Al final:
        - Si el audio dura más que la suma de pasos, esperamos lo que falta.
        - Si los pasos duran más que el audio, el audio se acabará antes (normal).
        """

        # 1) Ruta absoluta y duración real del audio
        path = self._audio_path(filename)
        dur = audio_duration_wav(path)

        # 2) Inicia el audio YA (esto NO bloquea)
        self.add_sound(path, gain=gain)

        # 3) Ejecuta cada paso en orden y cuenta cuánto tiempo pasó
        elapsed = 0.0

        for step in steps:

            # --- Paso de llamada ---
            # Se hace una llamada a una función que usa self.play/self.wait;
            # esto hace que podamos contar el tiempo real y mantener el audio sincronizado.
            if "call" in step:
                start_t = self.time
                step["call"]()
                elapsed += self.time - start_t
                continue

            # --- Paso de espera ---
            if "wait" in step:
                t = float(step["wait"])
                self.wait(t)
                elapsed += t
                continue

            # --- Paso de animación ---
            anim = step["anim"]
            run_time = float(step.get("run_time", 1.0))
            elapsed += run_time

            # kwargs extra para self.play (por si algún día metes rate_func, etc.)
            play_kwargs = {k: v for k, v in step.items() if k not in ("anim", "run_time")}

            # Si anim es lista/tupla => self.play(*anims)
            if isinstance(anim, (list, tuple)):
                self.play(*anim, run_time=run_time, **play_kwargs)
            else:
                self.play(anim, run_time=run_time, **play_kwargs)

        # 4) Espera lo que falte para que el audio termine (si falta)
        restante = dur - elapsed
        if restante > 0:
            self.wait(restante + extra_wait)
        else:
            self.wait(extra_wait)

    # =========================================================================
    # (C) CONSTRUCT: toda la escena
    # =========================================================================
    def construct(self):

        # =========================================================================================
        #                              1) DEDUCCION MATEMATICA
        # =========================================================================================

        # ----------------------------- Presentacion (titulo + autor) -----------------------------
        titulo_deduccion = Tex(r"Deducción matematica de series de Taylor: series de Maclaurin").scale(0.9)
        autor_deduccion = Tex(r"por Nicolas Plata Molano").scale(0.7).next_to(titulo_deduccion, DOWN)
        titulo_deduccion.set_color(RED)

        # Subtítulo (parte superior izquierda)
        subtitulo_deduccion = Tex(r"Deducción matematica formal de la formula").scale(0.6).to_corner(UL)
        subtitulo_deduccion.set_color(WHITE)

        # ----------------------------- BLOQUE 1: Suponemos un polinomio -----------------------------
        polinomio_sup = MathTex(
            r"f(x)=",
            r"a_0", r"+",
            r"a_1", r"x", r"+",
            r"a_2", r"x^2", r"+",
            r"a_3", r"x^3", r"+\cdots+",
            r"a_{n+1}", r"x^{n+1}"
        ).scale(0.68)

        polinomio_sup.set_color(WHITE)
        polinomio_sup.set_color_by_tex("a_0", GREEN)
        polinomio_sup.set_color_by_tex("a_1", BLUE)
        polinomio_sup.set_color_by_tex("a_2", TEAL)
        polinomio_sup.set_color_by_tex("a_3", PINK)
        polinomio_sup.set_color_by_tex("a_{n+1}", PURPLE)
        polinomio_sup.next_to(subtitulo_deduccion, DOWN, buff=0.25).align_to(subtitulo_deduccion, LEFT)

        # ----------------------------- BLOQUE 2: Evaluacion en 0 -----------------------------
        linea_f0 = MathTex(r"f(0)=a_0").scale(0.66)
        linea_f0.set_color(WHITE)
        linea_f0.set_color_by_tex("a_0", GREEN)
        linea_f0.next_to(polinomio_sup, DOWN, buff=0.4).align_to(polinomio_sup, LEFT)

        # ----------------------------- BLOQUE 3: Primera derivada -----------------------------
        etiqueta_d1 = Tex(r"Primera derivada:").scale(0.5)
        etiqueta_d1.set_color(WHITE)
        etiqueta_d1.next_to(linea_f0, DOWN, buff=0.48).align_to(polinomio_sup, LEFT)

        derivada_1 = MathTex(
            r"f'(x)=",
            r"a_1", r"+",
            r"2a_2 x", r"+",
            r"3a_3 x^2", r"+\cdots+",
            r"(n+1)a_{n+1}x^n"
        ).scale(0.62)

        derivada_1.set_color(WHITE)
        derivada_1.set_color_by_tex("a_1", BLUE)
        derivada_1.set_color_by_tex("a_2", TEAL)
        derivada_1.set_color_by_tex("a_3", PINK)
        derivada_1.set_color_by_tex("n+1", PURPLE)
        derivada_1.next_to(etiqueta_d1, DOWN, buff=0.22).align_to(polinomio_sup, LEFT)

        evaluada_1 = MathTex(r"f'(0)=a_1").scale(0.62)
        evaluada_1.set_color(WHITE)
        evaluada_1.set_color_by_tex("a_1", BLUE)
        evaluada_1.next_to(derivada_1, DOWN, buff=0.30).align_to(polinomio_sup, LEFT)

        # ----------------------------- BLOQUE 4: Segunda derivada -----------------------------
        etiqueta_d2 = Tex(r"Segunda derivada:").scale(0.5)
        etiqueta_d2.set_color(WHITE)
        etiqueta_d2.next_to(evaluada_1, DOWN, buff=0.48).align_to(polinomio_sup, LEFT)

        derivada_2 = MathTex(
            r"f''(x)=",
            r"2a_2", r"+",
            r"3\cdot 2\,a_3 x", r"+\cdots+",
            r"n(n+1)a_{n+1}x^{n-1}"
        ).scale(0.62)

        derivada_2.set_color(WHITE)
        derivada_2.set_color_by_tex("a_2", TEAL)
        derivada_2.set_color_by_tex("a_3", PINK)
        derivada_2.set_color_by_tex("n+1", PURPLE)
        derivada_2.next_to(etiqueta_d2, DOWN, buff=0.22).align_to(polinomio_sup, LEFT)

        evaluada_2 = MathTex(r"f''(0)=2a_2").scale(0.62)
        evaluada_2.set_color(WHITE)
        evaluada_2.set_color_by_tex("a_2", TEAL)
        evaluada_2.next_to(derivada_2, DOWN, buff=0.30).align_to(polinomio_sup, LEFT)

        # ----------------------------- BLOQUE 5: Tercera derivada -----------------------------
        etiqueta_d3 = Tex(r"Tercera derivada:").scale(0.5)
        etiqueta_d3.set_color(WHITE)
        etiqueta_d3.next_to(evaluada_2, DOWN, buff=0.48).align_to(polinomio_sup, LEFT)

        derivada_3 = MathTex(
            r"f'''(x)=",
            r"3\cdot 2\,a_3", r"+\cdots+",
            r"(n-1)n(n+1)a_{n+1}x^{n-2}"
        ).scale(0.62)

        derivada_3.set_color(WHITE)
        derivada_3.set_color_by_tex("a_3", PINK)
        derivada_3.set_color_by_tex("n+1", PURPLE)
        derivada_3.next_to(etiqueta_d3, DOWN, buff=0.22).align_to(polinomio_sup, LEFT)

        evaluada_3 = MathTex(r"f'''(0)=3\cdot 2\,a_3").scale(0.62)
        evaluada_3.set_color(WHITE)
        evaluada_3.set_color_by_tex("a_3", PINK)
        evaluada_3.next_to(derivada_3, DOWN, buff=0.30).align_to(polinomio_sup, LEFT)

        # ----------------------------- Despejes: flechas + cajas -----------------------------
        flecha_0 = MathTex(r"\Longrightarrow").scale(0.75).set_color(BLUE)
        despeje_0 = MathTex(r"a_0=\frac{f(0)}{0!}").scale(0.66)
        despeje_0.set_color(WHITE)
        despeje_0.set_color_by_tex("a_0", GREEN)
        caja_0 = SurroundingRectangle(despeje_0, color=GREEN, buff=0.14)
        caja_0.set_fill(GREEN, opacity=0.22)

        flecha_1 = MathTex(r"\Longrightarrow").scale(0.75).set_color(BLUE)
        despeje_1 = MathTex(r"a_1=\frac{f'(0)}{1!}").scale(0.62)
        despeje_1.set_color(WHITE)
        despeje_1.set_color_by_tex("a_1", BLUE)
        caja_1 = SurroundingRectangle(despeje_1, color=BLUE, buff=0.14)
        caja_1.set_fill(BLUE, opacity=0.18)

        flecha_2 = MathTex(r"\Longrightarrow").scale(0.75).set_color(BLUE)
        despeje_2 = MathTex(r"a_2=\frac{f''(0)}{2!}").scale(0.62)
        despeje_2.set_color(WHITE)
        despeje_2.set_color_by_tex("a_2", TEAL)
        caja_2 = SurroundingRectangle(despeje_2, color=TEAL, buff=0.14)
        caja_2.set_fill(TEAL, opacity=0.18)

        flecha_3 = MathTex(r"\Longrightarrow").scale(0.75).set_color(BLUE)
        despeje_3 = MathTex(r"a_3=\frac{f'''(0)}{3!}").scale(0.62)
        despeje_3.set_color(WHITE)
        despeje_3.set_color_by_tex("a_3", PINK)
        caja_3 = SurroundingRectangle(despeje_3, color=PINK, buff=0.14)
        caja_3.set_fill(PINK, opacity=0.18)

        # Posicionamiento de flechas + despejes (alineados con su igualdad)
        flecha_0.next_to(linea_f0, RIGHT, buff=0.45).align_to(linea_f0, DOWN)
        despeje_0.next_to(flecha_0, RIGHT, buff=0.35)
        caja_0.move_to(despeje_0)

        flecha_1.next_to(evaluada_1, RIGHT, buff=0.45).align_to(evaluada_1, DOWN)
        despeje_1.next_to(flecha_1, RIGHT, buff=0.35)
        caja_1.move_to(despeje_1)

        flecha_2.next_to(evaluada_2, RIGHT, buff=0.45).align_to(evaluada_2, DOWN)
        despeje_2.next_to(flecha_2, RIGHT, buff=0.35)
        caja_2.move_to(despeje_2)

        flecha_3.next_to(evaluada_3, RIGHT, buff=0.45).align_to(evaluada_3, DOWN)
        despeje_3.next_to(flecha_3, RIGHT, buff=0.35)
        caja_3.move_to(despeje_3)

        # ----------------------------- BLOQUE 6: Columna derecha -----------------------------
        linea_reescritura = Tex(r"Reescribimos $f(x)$ en terminos de ", r"a").scale(0.55)
        linea_reescritura.set_color(WHITE)
        linea_reescritura.set_color_by_tex("a", RED)

        polinomio_reescrito = MathTex(
            r"f(x)=",
            r"a_0", r"+",
            r"a_1", r"x" ,r"+",
            r"a_2", r" x^2" , r"+",
            r"a_3 ", r"x^3" , r"+\cdots+",
            r"a_{n+1}", r"x^{n+1}"
        ).scale(0.62)

        polinomio_reescrito.set_color(WHITE)
        polinomio_reescrito.set_color_by_tex("a_0", GREEN)
        polinomio_reescrito.set_color_by_tex("a_1", BLUE)
        polinomio_reescrito.set_color_by_tex("a_2", TEAL)
        polinomio_reescrito.set_color_by_tex("a_3", PINK)
        polinomio_reescrito.set_color_by_tex("a_{n+1}", PURPLE)

        sustitucion_coef = MathTex(
            r"f(x)=",
            r"\frac{f(0)}{0!}",
            r"+\frac{f'(0)}{1!}x",
            r"+\frac{f''(0)}{2!}x^2",
            r"+\frac{f'''(0)}{3!}x^3",
            r"+\cdots+",
            r"\frac{f^{(n+1)}(0)}{(n+1)!}x^{n+1}"
        ).scale(0.58)

        sustitucion_coef.set_color(WHITE)
        sustitucion_coef.set_color_by_tex("0!", GREEN)
        sustitucion_coef.set_color_by_tex("1!", BLUE)
        sustitucion_coef.set_color_by_tex("2!", TEAL)
        sustitucion_coef.set_color_by_tex("3!", PINK)
        sustitucion_coef.set_color_by_tex("x^{n+1}", PURPLE)

        formula_final = MathTex(
            r"f(x)=\sum_{n=0}^{\infty}\frac{f^{(n)}(0)}{n!}\,x^n"
        ).scale(0.78)
        formula_final.set_color(WHITE)

        recuadro_final = SurroundingRectangle(formula_final, color=GOLD, buff=0.25)
        recuadro_final.set_fill(GOLD_E, opacity=0.12)
        bloque_final = VGroup(recuadro_final, formula_final)

        bloque_reescritura = VGroup(linea_reescritura, polinomio_reescrito, sustitucion_coef, bloque_final)
        bloque_reescritura.arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        # ----------------------------- Layout 2 columnas (robusto) -----------------------------
        bloque_izquierdo = VGroup(
            subtitulo_deduccion, polinomio_sup,
            linea_f0,
            etiqueta_d1, derivada_1, evaluada_1,
            etiqueta_d2, derivada_2, evaluada_2,
            etiqueta_d3, derivada_3, evaluada_3,
            flecha_0, caja_0, despeje_0,
            flecha_1, caja_1, despeje_1,
            flecha_2, caja_2, despeje_2,
            flecha_3, caja_3, despeje_3,
        )

        layout_columnas = VGroup(bloque_izquierdo, bloque_reescritura)
        layout_columnas.arrange(RIGHT, buff=0.55, aligned_edge=UP)

        ancho_util = config.frame_width * 0.96
        alto_util = config.frame_height * 0.94
        escala_global = min(ancho_util / layout_columnas.width, alto_util / layout_columnas.height)
        layout_columnas.scale(escala_global)
        layout_columnas.move_to(ORIGIN).shift(UP * 0.15)

        # =========================================================================================
        #                          AUDIOS 1→8: DEDUCCIÓN (según PDF)
        # =========================================================================================

        # AUDIO_1 → Portada (título y autor)
        self.play_audio_over_animations(
            AUDIO_1,
            {"anim": [Write(titulo_deduccion), Write(autor_deduccion)], "run_time": 5},
            {"wait": 4},
            {"anim": [FadeOut(titulo_deduccion), FadeOut(autor_deduccion)], "run_time": 1.2},
            extra_wait=0.20
        )

        # AUDIO_2 → Subtítulo + polinomio supuesto
        self.play_audio_over_animations(
            AUDIO_2,
            {"anim": [FadeIn(subtitulo_deduccion)], "run_time": 2.2},
            {"wait": 1.0},
            {"anim": [Write(polinomio_sup)], "run_time": 4.2},
            extra_wait=0.25
        )

        # AUDIO_3 → Aparece f(0)=a0
        self.play_audio_over_animations(
            AUDIO_3,
            {"anim": Write(linea_f0), "run_time": 2.0},
            {"wait": 0.4},  # deja respirar la idea “evaluar en 0”
            extra_wait=0.25
        )

        # AUDIO_4 → Primera derivada completa
        self.play_audio_over_animations(
            AUDIO_4,
            {"anim": FadeIn(etiqueta_d1), "run_time": 0.6},
            {"anim": Write(derivada_1), "run_time": 4.0},
            {"anim": Write(evaluada_1), "run_time": 2.0},
            extra_wait=0.25
        )

        # AUDIO_5 → Segunda derivada completa
        self.play_audio_over_animations(
            AUDIO_5,
            {"anim": FadeIn(etiqueta_d2), "run_time": 0.6},
            {"anim": Write(derivada_2), "run_time": 3.6},
            {"anim": Write(evaluada_2), "run_time": 2.0},
            extra_wait=0.25
        )

        # AUDIO_6 → Tercera derivada + patrón
        self.play_audio_over_animations(
            AUDIO_6,
            {"anim": FadeIn(etiqueta_d3), "run_time": 0.6},
            {"anim": Write(derivada_3), "run_time": 3.0},
            {"anim": Write(evaluada_3), "run_time": 2.0},
            {"wait": 0.4},  # espacio para “aquí ya se ve el patrón”
            extra_wait=0.25
        )

        # AUDIO_7 → Despejes (flechas y cajas)
        self.play_audio_over_animations(
            AUDIO_7,
            {"anim": [Write(flecha_0), FadeIn(caja_0), Write(despeje_0)], "run_time": 2.0},
            {"anim": [Write(flecha_1), FadeIn(caja_1), Write(despeje_1)], "run_time": 2.0},
            {"anim": [Write(flecha_2), FadeIn(caja_2), Write(despeje_2)], "run_time": 2.0},
            {"anim": [Write(flecha_3), FadeIn(caja_3), Write(despeje_3)], "run_time": 2.0},
            extra_wait=0.25
        )

        # AUDIO_8 → Columna derecha (reescritura y fórmula final)
        self.play_audio_over_animations(
            AUDIO_8,
            {"anim": FadeIn(linea_reescritura), "run_time": 1.4},
            {"anim": Write(polinomio_reescrito), "run_time": 3.0},
            {"anim": Write(sustitucion_coef), "run_time": 5.0},
            extra_wait=0.25
        )

        # AUDIO_8 → Reescribir polinomio LARGO para usar terminos como Sumatoria
        self.play_audio_over_animations(
            AUDIO_8_1,
            {"anim": [FadeIn(recuadro_final), Write(formula_final)], "run_time": 5.0},
            extra_wait=0.5
        )

        # Agrupo toda la deducción para borrarla en una transición limpia
        todo_deduccion = VGroup(
            subtitulo_deduccion, polinomio_sup,
            linea_f0,
            etiqueta_d1, derivada_1, evaluada_1,
            etiqueta_d2, derivada_2, evaluada_2,
            etiqueta_d3, derivada_3, evaluada_3,
            flecha_0, caja_0, despeje_0,
            flecha_1, caja_1, despeje_1,
            flecha_2, caja_2, despeje_2,
            flecha_3, caja_3, despeje_3,
            linea_reescritura, polinomio_reescrito, sustitucion_coef,
            bloque_final
        )

        # =========================================================================================
        #                              2) EJEMPLO e^x (parte visual)
        # =========================================================================================

        titulo = Tex(r"Maclaurin para $e^x$").scale(1.1).to_edge(UP)

        formula_expandida = MathTex(
            r"e^x", r"=", r"1", r"+", r"x", r"+", r"\frac{x^2}{2!}", r"+", r"\frac{x^3}{3!}", r"+\cdots", r"+", r"\frac{x^n}{n!}"
        ).next_to(titulo, DOWN)

        formula_sumatoria = MathTex(r"e^x=\sum_{n=0}^{\infty}\frac{x^n}{n!}").next_to(titulo, DOWN)

        # Objetivos para mover título + fórmula juntos a la esquina superior izquierda
        titulo_target = titulo.copy().scale(0.6).to_corner(UL)
        formula_target = formula_sumatoria.copy().scale(0.6).next_to(titulo_target, DOWN, aligned_edge=LEFT)

        # AUDIO_9 → Transición + título "Maclaurin para e^x"
        self.play_audio_over_animations(
            AUDIO_9,
            {"anim": FadeOut(todo_deduccion), "run_time": 1.0},
            {"anim": Write(titulo), "run_time": 2.0},
            {"anim": FadeIn(formula_expandida, shift=DOWN), "run_time": 5},
            {"anim": ReplacementTransform(formula_expandida, formula_sumatoria), "run_time": 2},
            {
                "anim": [
                    Transform(titulo, titulo_target),
                    Transform(formula_sumatoria, formula_target),
                ],
                "run_time": 2
            },
            extra_wait=0.5
        )

        # -------------------- Aproximaciones “por piezas” (n=0..3) --------------------
        aprox_0 = MathTex(r"e^x", r"\approx", r"1").scale(0.6).set_color(YELLOW)
        aprox_1 = MathTex(r"e^x", r"\approx", r"1", r"+", r"x").scale(0.6).set_color(YELLOW)
        aprox_2 = MathTex(r"e^x", r"\approx", r"1", r"+", r"x", r"+", r"\frac{x^2}{2!}").scale(0.6).set_color(YELLOW)
        aprox_3 = MathTex(r"e^x", r"\approx", r"1", r"+", r"x", r"+", r"\frac{x^2}{2!}", r"+", r"\frac{x^3}{3!}").scale(0.6).set_color(YELLOW)

        aprox_0.next_to(titulo, DOWN)
        aprox_1.next_to(titulo, DOWN)
        aprox_2.next_to(titulo, DOWN)
        aprox_3.next_to(titulo, DOWN)

        # -------------------- Ejes --------------------
        ejes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 20, 5],
            tips=True,
        ).scale(0.9).to_edge(DOWN)

        etiqueta_x = ejes.get_x_axis_label(Tex("x").scale(0.8), edge=RIGHT, direction=RIGHT)
        etiqueta_y = ejes.get_y_axis_label(Tex("y").scale(0.8), edge=UP, direction=UP)

        # Curva real e^x (azul)
        grafica_exp = ejes.plot(lambda x: np.exp(x), x_range=[-3, 3], color=BLUE)
        tag_exp = (
            MathTex(r"f(x)=e^x")
            .scale(0.85)
            .set_color(BLUE)
            .next_to(ejes, UR, buff=0.25)
            .shift(LEFT * 0.8 + DOWN * 0.2)
        )

        # AUDIO_10 → Gráfica analítica de e^x
        self.play_audio_over_animations(
            AUDIO_10,
            {"anim": [Create(ejes), FadeIn(etiqueta_x), FadeIn(etiqueta_y)], "run_time": 3.0},
            {"anim": [Create(grafica_exp), FadeIn(tag_exp)], "run_time": 3.0},
            extra_wait=0.20
        )

        # -------------------- Indicador de grado n --------------------
        grados = [0, 1, 2, 3, 5, 10]
        n_actual = grados[0]

        etiqueta_n = Tex("n =").scale(0.8).to_corner(UR)
        valor_n = Integer(n_actual).scale(0.8).next_to(etiqueta_n, RIGHT, buff=0.15)

        # Polinomio inicial (n=0)
        grafica_polinomio = ejes.plot(lambda x: self.maclaurin_exp(x, n_actual), x_range=[-3, 3], color=YELLOW)

        # Trackers para el “punto amarillo” suave (evita teletransporte)
        x_tracker = ValueTracker(-2.5)

        t_transicion = ValueTracker(0.0)   # 0: viejo, 1: nuevo
        n_desde = ValueTracker(n_actual)
        n_hasta = ValueTracker(n_actual)

        linea_vertical = always_redraw(lambda: ejes.get_vertical_line(ejes.c2p(x_tracker.get_value(), 0), line_func=Line))
        punto_exp = always_redraw(lambda: Dot(ejes.c2p(x_tracker.get_value(), float(np.exp(x_tracker.get_value()))), color=BLUE).scale(0.9))

        punto_polinomio = always_redraw(
            lambda: Dot(
                ejes.c2p(
                    x_tracker.get_value(),
                    (1 - t_transicion.get_value()) * self.maclaurin_exp(x_tracker.get_value(), int(round(n_desde.get_value()))) +
                    (t_transicion.get_value())     * self.maclaurin_exp(x_tracker.get_value(), int(round(n_hasta.get_value())))
                ),
                color=YELLOW
            ).scale(0.9)
        )

        # AUDIO_11 → n=0 (solo constante)
        self.play_audio_over_animations(
            AUDIO_11,
            {"anim": [FadeIn(etiqueta_n), FadeIn(valor_n)], "run_time": 1.2},
            {"anim": Create(grafica_polinomio), "run_time": 1.6},
            # Cambio de fórmula sumatoria -> “≈ 1”
            {"anim": TransformMatchingTex(formula_sumatoria, aprox_0, replace_mobject_with_target_in_scene=True), "run_time": 0.8},
            {"anim": [Create(linea_vertical), FadeIn(punto_exp), FadeIn(punto_polinomio)], "run_time": 1.4},
            {"anim": x_tracker.animate.set_value(2.5), "run_time": 2.2, "rate_func": linear},
            extra_wait=0.20
        )
        formula_sumatoria = aprox_0  # actualizo referencia al objeto actual en pantalla

        # =========================================================================
        # Helper: transición suave de n (mantiene el punto amarillo sin saltos)
        # =========================================================================
        def avanzar_n(nuevo_n: int, run_time_transicion: float, anim_formula=None):
            """
            - Prepara trackers para interpolar el punto amarillo (sin teletransporte)
            - Transforma la curva y actualiza el indicador n
            - (Opcional) permite transformar fórmula al mismo tiempo
            """
            nonlocal n_actual, grafica_polinomio, valor_n, formula_sumatoria

            nueva_grafica = ejes.plot(
                lambda x, nn=nuevo_n: self.maclaurin_exp(x, nn),
                x_range=[-3, 3],
                color=YELLOW
            )

            # Se hace la preparación de trackers: "vengo desde n_actual y voy a nuevo_n";
            # esto hace que el punto amarillo interpole en lugar de saltar.
            self.play(
                n_desde.animate.set_value(n_actual),
                n_hasta.animate.set_value(nuevo_n),
                t_transicion.animate.set_value(0.0),
                run_time=1/60
            )

            extras = []
            if anim_formula is not None:
                extras.append(anim_formula)

            # Se hace la transición principal (curva + número n + punto interpolado);
            # esto hace que el cambio de n sea suave y visible.
            self.play(
                Transform(grafica_polinomio, nueva_grafica),
                valor_n.animate.set_value(nuevo_n),
                t_transicion.animate.set_value(1.0),
                *extras,
                run_time=run_time_transicion
            )

            n_actual = nuevo_n

        # AUDIO_12 → n=1 (pendiente coincide)
        # Se hace la transición a n=1 dentro del mismo audio (sin repetirlo);
        # esto hace que la narración coincida con el cambio visual.
        self.play_audio_over_animations(
            AUDIO_12,
            {
                "anim": (
                    TransformMatchingTex(
                        formula_sumatoria, aprox_1,
                        replace_mobject_with_target_in_scene=True
                    )
                ),
                "run_time": 0.8
            },
            # Se hace una pausa corta antes del cambio visual;
            # esto hace que la narración tenga espacio.
            {"wait": 5},
            # Se hace la transición suave de n=0 -> n=1; esto hace que el punto NO se teletransporte.
            {"call": lambda: avanzar_n(1, run_time_transicion=1.1)},
            {"anim": x_tracker.animate.set_value(-2.5), "run_time": 1.0, "rate_func": linear},
            {"anim": x_tracker.animate.set_value(2.5), "run_time": 1.0, "rate_func": linear},
            {"wait": 0.15},
            extra_wait=0.20
        )
        formula_sumatoria = aprox_1

        # AUDIO_13 → n=2 y n=3 (más términos)
        # Se unifica n=2 y n=3 en un solo audio para evitar repeticiones;
        # esto hace que el audio no se duplique.
        self.play_audio_over_animations(
            AUDIO_13,
            # n=2: cambio fórmula + transición
            {
                "anim": TransformMatchingTex(
                    formula_sumatoria, aprox_2,
                    replace_mobject_with_target_in_scene=True
                ),
                "run_time": 0.8
            },
            {"wait": 0.2},
            # Se hace la transición suave de n=1 -> n=2.
            {"call": lambda: avanzar_n(2, run_time_transicion=1.1)},
            {"anim": x_tracker.animate.set_value(-2.5), "run_time": 1.0, "rate_func": linear},
            {"anim": x_tracker.animate.set_value(2.5), "run_time": 1.0, "rate_func": linear},
            # Se hace una pausa para mantener n=2 visible (según tu guion).
            {"wait": 1.0},
            # n=3: cambio fórmula + transición
            {
                "anim": TransformMatchingTex(
                    aprox_2, aprox_3,
                    replace_mobject_with_target_in_scene=True
                ),
                "run_time": 0.8
            },
            {"wait": 0.2},
            # Se hace la transición suave de n=2 -> n=3.
            {"call": lambda: avanzar_n(3, run_time_transicion=1.1)},
            # Se hace el ocultamiento de la fórmula después de n=3;
            # esto hace que la pantalla quede limpia para lo siguiente.
            {"anim": FadeOut(aprox_3), "run_time": 0.6},
            {"anim": x_tracker.animate.set_value(-2.5), "run_time": 1.0, "rate_func": linear},
            {"anim": x_tracker.animate.set_value(2.5), "run_time": 1.0, "rate_func": linear},
            {"wait": 0.15},
            extra_wait=0.20
        )
        formula_sumatoria = aprox_3

        # AUDIO_14 → n=5 y n=10 + nota final
        # Se unifica n=5 y n=10 en un solo audio (sin repetir el audio).
        nota = Tex(r"Mayor $n$ $\Rightarrow$ mejor aproximación cerca de $0$.").scale(0.7)
        nota.next_to(ejes, UP, buff=0.5)
        self.play_audio_over_animations(
            AUDIO_14,
            # transición a n=5
            {"call": lambda: avanzar_n(5, run_time_transicion=1.1)},
            {"anim": x_tracker.animate.set_value(-2.5), "run_time": 1.0, "rate_func": linear},
            {"anim": x_tracker.animate.set_value(2.5), "run_time": 1.0, "rate_func": linear},
            {"wait": 0.5},
            # transición a n=10
            {"call": lambda: avanzar_n(10, run_time_transicion=1.1)},
            {"anim": x_tracker.animate.set_value(-2.5), "run_time": 1.0, "rate_func": linear},
            {"anim": x_tracker.animate.set_value(2.5), "run_time": 1.0, "rate_func": linear},
            {"anim": FadeIn(nota), "run_time": 1.0},
            {"wait": 1.0},
            # Se hace un barrido final completo; esto hace que el punto recorra la función al cierre.
            {"anim": x_tracker.animate.set_value(-2.5), "run_time": 1.0, "rate_func": linear},
            {"anim": x_tracker.animate.set_value(2.5), "run_time": 2.0, "rate_func": linear},
            extra_wait=0.20
        )
