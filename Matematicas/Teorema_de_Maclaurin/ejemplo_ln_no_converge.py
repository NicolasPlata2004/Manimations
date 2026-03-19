# ejemplo_ln_no_converge.py

import numpy as np
from manim import *

# Para audio
import wave              # duración de WAV PCM (frames / framerate)
import os                # rutas y verificación de archivos

# ==========================
# CONFIG: carpeta de audios
# ==========================
AUDIO_DIR = r"C:\Users\nicao\manimations\Audios\TercerVideo"

# Nombres de audios (deben existir dentro de AUDIO_DIR)
AUDIO_1 = "Audio_1.wav"
AUDIO_2 = "Audio_2.wav"
AUDIO_3 = "Audio_3.wav"


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



class ejemplo_ln_no_converge(Scene):


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



    def ln_1_mas_x(self, x: float) -> float:
        # f(x) = ln(1+x), dominio: x > -1
        return float(np.log1p(x))

    def maclaurin_ln_1_mas_x(self, x: float, n: int) -> float:
        """
        Serie de Maclaurin de ln(1+x):
        ln(1+x) = sum_{k=1..∞} (-1)^{k+1} x^k / k

        Polinomio parcial (grado n):
        P_n(x) = sum_{k=1..n} (-1)^{k+1} x^k / k
        """
        s = 0.0
        for k in range(1, n + 1):
            s += ((-1) ** (k + 1)) * (x**k) / k
        return float(s)

    def construct(self):

        # ----------------------------- Titulo / advertencia -----------------------------
        titulo = Tex(r"No siempre la serie de Maclaurin representa la función").scale(0.72).to_edge(UP)
        subtitulo = Tex(r"Ejemplo: $\ln(1+x)$ solo converge para $|x|<1$").scale(0.5).next_to(titulo, DOWN, buff=0.16)


        self.play_audio_over_animations(  # reproduce el audio 1 con las animaciones iniciales
            AUDIO_1,  # selecciona el primer archivo de audio
            {"anim": Write(titulo), "run_time": 5.0},  # escribe el titulo en pantalla
            {"wait": 5},  # pausa para lectura mientras suena el audio
            {"anim": FadeIn(subtitulo, shift=DOWN), "run_time": 5},  # muestra el subtitulo
            {"wait": 5},  # pausa breve antes del ajuste del titulo
            {"anim": [titulo.animate.scale(0.7).to_corner(UL), FadeOut(subtitulo)], "run_time": 4},  # escala y mueve el titulo mientras se desvanece el subtitulo
        )  # cierra el bloque de audio 1

        # ----------------------------- Formulas (serie y parciales) -----------------------------
        formula_serie = MathTex(
            r"\ln(1+x)=\sum_{n=1}^{\infty}(-1)^{n+1}\frac{x^n}{n}"
        ).scale(0.5).next_to(titulo, DOWN, buff=0.16).align_to(titulo, LEFT)

        # Polinomios parciales SOLO hasta n=6 (luego desaparecen en n=10 y n=21)
        aprox_1 = MathTex(r"\ln(1+x)", r"\approx", r"x").scale(0.5).set_color(YELLOW)
        aprox_2 = MathTex(r"\ln(1+x)", r"\approx", r"x", r"-", r"\frac{x^2}{2}").scale(0.5).set_color(YELLOW)
        aprox_3 = MathTex(r"\ln(1+x)", r"\approx", r"x", r"-", r"\frac{x^2}{2}", r"+", r"\frac{x^3}{3}").scale(0.5).set_color(YELLOW)
        aprox_4 = MathTex(
            r"\ln(1+x)", r"\approx",
            r"x", r"-", r"\frac{x^2}{2}", r"+", r"\frac{x^3}{3}", r"-", r"\frac{x^4}{4}"
        ).scale(0.5).set_color(YELLOW)
        aprox_5 = MathTex(
            r"\ln(1+x)", r"\approx",
            r"x", r"-", r"\frac{x^2}{2}", r"+", r"\frac{x^3}{3}", r"-", r"\frac{x^4}{4}", r"+", r"\frac{x^5}{5}"
        ).scale(0.5).set_color(YELLOW)
        aprox_6 = MathTex(
            r"\ln(1+x)", r"\approx",
            r"x", r"-", r"\frac{x^2}{2}", r"+", r"\frac{x^3}{3}", r"-", r"\frac{x^4}{4}", r"+", r"\frac{x^5}{5}", r"-", r"\frac{x^6}{6}"
        ).scale(0.5).set_color(YELLOW)

        for a in (aprox_1, aprox_2, aprox_3, aprox_4, aprox_5, aprox_6):
            a.next_to(formula_serie, DOWN, buff=0.12).align_to(formula_serie, LEFT)

        # ----------------------------- Ejes (mas pequenos) -----------------------------
        ejes = Axes(
            x_range=[-1.2, 2.0, 0.5],
            y_range=[-4, 1.2, 1],
            tips=True,
        ).scale(0.78).to_edge(DOWN)  # SE MODIFICA: mas pequeno

        etiqueta_x = ejes.get_x_axis_label(Tex("x").scale(0.65), edge=RIGHT, direction=RIGHT)
        etiqueta_y = ejes.get_y_axis_label(Tex("y").scale(0.65), edge=UP, direction=UP)

        # ----------------------------- Zona de convergencia |x|<1 -----------------------------
        y_abajo = -4
        y_arriba = 1.2

        franja_convergencia = Polygon(
            ejes.c2p(-1, y_abajo),
            ejes.c2p(1,  y_abajo),
            ejes.c2p(1,  y_arriba),
            ejes.c2p(-1, y_arriba),
        )
        franja_convergencia.set_fill(GRAY, opacity=0.18)
        franja_convergencia.set_stroke(width=0)

        linea_menos1 = DashedLine(
            ejes.c2p(-1, y_abajo),
            ejes.c2p(-1, y_arriba),
            dash_length=0.12
        ).set_color(GRAY)

        linea_mas1 = DashedLine(
            ejes.c2p(1, y_abajo),
            ejes.c2p(1, y_arriba),
            dash_length=0.12
        ).set_color(GRAY)

        etiqueta_zona = Tex(r"Converge: $|x|<1$").scale(0.48).set_color(GRAY)
        etiqueta_zona.next_to(franja_convergencia, UP, buff=0.12).shift(LEFT * 1.5)

        # ----------------------------- Graficas -----------------------------
        grafica_real = ejes.plot(lambda x: self.ln_1_mas_x(x), x_range=[-0.99, 2.0], color=GREEN)
        tag_real = MathTex(r"f(x)=\ln(1+x)").scale(0.62).set_color(GREEN)
        tag_real.next_to(ejes, UR, buff=0.18).shift(LEFT * 0.55 + DOWN * 0.10)

        # ----------------------------- Indicador de n -----------------------------
        grados = [1, 2, 3, 4, 5, 6, 10, 21]  # SE MODIFICA: lista exacta
        n_actual = grados[0]

        etiqueta_n = Tex("n =").scale(0.7).to_corner(UR)
        valor_n = Integer(n_actual).scale(0.7).next_to(etiqueta_n, RIGHT, buff=0.10)

        # ----------------------------- Primer polinomio -----------------------------
        grafica_polinomio = ejes.plot(
            lambda x: self.maclaurin_ln_1_mas_x(x, n_actual),
            x_range=[-0.99, 2.0],
            color=YELLOW
        )

        # ----------------------------- Punticos + linea vertical -----------------------------
        x0 = ValueTracker(-0.8)

        t_morph = ValueTracker(0.0)
        n_desde = ValueTracker(n_actual)
        n_hasta = ValueTracker(n_actual)

        linea_vertical = always_redraw(lambda: ejes.get_vertical_line(ejes.c2p(x0.get_value(), 0), line_func=Line))

        punto_real = always_redraw(
            lambda: Dot(
                ejes.c2p(x0.get_value(), self.ln_1_mas_x(x0.get_value())),
                color=GREEN
            ).scale(0.75)
        )

        punto_polinomio = always_redraw(
            lambda: Dot(
                ejes.c2p(
                    x0.get_value(),
                    (1 - t_morph.get_value()) * self.maclaurin_ln_1_mas_x(x0.get_value(), int(round(n_desde.get_value()))) +
                    (t_morph.get_value())     * self.maclaurin_ln_1_mas_x(x0.get_value(), int(round(n_hasta.get_value())))
                ),
                color=YELLOW
            ).scale(0.75)
        )

        self.play_audio_over_animations(  # reproduce el audio 2 con la secuencia intermedia
            AUDIO_2,  # selecciona el segundo archivo de audio
            {"wait": 0.3},  # deja una pausa inicial mientras corre el audio
            {"anim": FadeIn(formula_serie, shift=DOWN), "run_time": 1.0},  # muestra la serie
            {"wait": 0.15},  # pausa corta
            {"anim": FadeIn(aprox_1, shift=DOWN), "run_time": 1.0},  # muestra el primer polinomio
            {"wait": 0.3},  # pausa corta para lectura
            {"anim": [Create(ejes), FadeIn(etiqueta_x), FadeIn(etiqueta_y)], "run_time": 1.0},  # crea ejes y etiquetas
            {"wait": 0.15},  # pausa corta
            {"anim": [FadeIn(franja_convergencia), Create(linea_menos1), Create(linea_mas1), FadeIn(etiqueta_zona)], "run_time": 1.0},  # muestra zona de convergencia
            {"wait": 0.15},  # pausa corta
            {"anim": [Create(grafica_real), FadeIn(tag_real)], "run_time": 1.0},  # dibuja la grafica real y su etiqueta
            {"wait": 0.15},  # pausa corta
            {"anim": [FadeIn(etiqueta_n), FadeIn(valor_n)], "run_time": 1.0},  # muestra el indicador de n
            {"wait": 0.1},  # pausa corta
            {"anim": Create(grafica_polinomio), "run_time": 1.0},  # dibuja el primer polinomio
            {"wait": 0.15},  # pausa corta
            {"anim": [Create(linea_vertical), FadeIn(punto_real), FadeIn(punto_polinomio)], "run_time": 1.0},  # muestra linea y puntos
            {"anim": x0.animate.set_value(1.8), "run_time": 1.8, "rate_func": linear},  # barre x0 hacia 1.8
            {"wait": 0.25},  # pausa final del segundo audio
        )  # cierra el bloque de audio 2

        # ----------------------------- Iteraciones (sube n) -----------------------------
        formula_aprox_actual = aprox_1  # SE GUARDA: para ir transformando y luego ocultar

        def _iteraciones():  # agrupa las iteraciones para sincronizar con el audio 3
            nonlocal n_actual, formula_aprox_actual  # permite actualizar variables externas en el bucle
            for nuevo_n in grados[1:]:
                self.play(
                    n_desde.animate.set_value(n_actual),
                    n_hasta.animate.set_value(nuevo_n),
                    t_morph.animate.set_value(0.0),
                    run_time=0.001
                )

                nueva_grafica = ejes.plot(
                    lambda x, nn=nuevo_n: self.maclaurin_ln_1_mas_x(x, nn),
                    x_range=[-0.99, 2.0],
                    color=YELLOW
                )

                # Animacion de la formula SOLO hasta n=6
                anim_formula = []
                if nuevo_n == 2:
                    anim_formula.append(TransformMatchingTex(formula_aprox_actual, aprox_2, replace_mobject_with_target_in_scene=True))
                    formula_aprox_actual = aprox_2
                elif nuevo_n == 3:
                    anim_formula.append(TransformMatchingTex(formula_aprox_actual, aprox_3, replace_mobject_with_target_in_scene=True))
                    formula_aprox_actual = aprox_3
                elif nuevo_n == 4:
                    anim_formula.append(TransformMatchingTex(formula_aprox_actual, aprox_4, replace_mobject_with_target_in_scene=True))
                    formula_aprox_actual = aprox_4
                elif nuevo_n == 5:
                    anim_formula.append(TransformMatchingTex(formula_aprox_actual, aprox_5, replace_mobject_with_target_in_scene=True))
                    formula_aprox_actual = aprox_5
                elif nuevo_n == 6:
                    anim_formula.append(TransformMatchingTex(formula_aprox_actual, aprox_6, replace_mobject_with_target_in_scene=True))
                    formula_aprox_actual = aprox_6

                # Si ya pase a 10 o 21, oculto la aproximacion textual
                ocultar_formula = []
                if nuevo_n in (10, 21) and formula_aprox_actual is not None:
                    ocultar_formula.append(FadeOut(formula_aprox_actual, run_time=0.5))
                    formula_aprox_actual = None

                self.play(
                    Transform(grafica_polinomio, nueva_grafica),
                    valor_n.animate.set_value(nuevo_n),
                    t_morph.animate.set_value(1.0),
                    *anim_formula,
                    *ocultar_formula,
                    run_time=1.05
                )

                n_actual = nuevo_n

                # Barrido: dentro |x|<1 mejora; luego en x>1 NO converge
                self.play(x0.animate.set_value(-0.8), run_time=0.85, rate_func=linear)
                self.play(x0.animate.set_value(0.9), run_time=0.85, rate_func=linear)
                self.play(x0.animate.set_value(1.8), run_time=1.0, rate_func=linear)
                self.wait(0.08)

        # ----------------------------- Mensaje final (abajo derecha) -----------------------------
        cierre = Tex(
            r"En $|x|<1$ la aproximacion mejora, \\", 
            r"pero para $x>1$ NO converge a $\ln(1+x)$."
        ).scale(0.50).to_corner(DR)

        self.play_audio_over_animations(  # reproduce el audio 3 sobre el resto de animaciones
            AUDIO_3,  # selecciona el tercer archivo de audio
            {"call": _iteraciones},  # ejecuta las iteraciones durante el audio
            {"anim": FadeIn(cierre), "run_time": 1.0},  # muestra el mensaje final
            {"wait": 1.2},  # espera final con el mensaje en pantalla
        )  # cierra el bloque de audio 3
