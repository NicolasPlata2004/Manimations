# =========================================================================================
# CalculadoraIntro.py  (Manim)
# - Calculadora animada que teclea: cos(0,8)=?  y luego muestra el resultado.
# - Incluye 3 MODOS de sincronización audio/animación:
#   (1) SIMULTÁNEO: audio y animación empiezan al mismo tiempo
#   (2) AUDIO->ANIM: primero suena el audio completo, luego corre la animación
#   (3) ANIM->AUDIO: primero corre la animación, luego suena el audio completo
#
# - También incluye cómo "disparar" un audio EXACTAMENTE al presionar "="
#   (con la animación de presionar).
# =========================================================================================

# ==========================
# IMPORTS
# ==========================
import math              # cos() y formato numérico
import wave              # duración de WAV PCM (frames / framerate)
import os                # rutas y verificación de archivos
from manim import *      # Scene, VGroup, animaciones, etc.

# ==========================
# CONFIG: carpeta de audios
# ==========================
AUDIO_DIR = r"C:\Users\nicao\manimations\Audios"

# Nombres de audios (deben existir dentro de AUDIO_DIR)
AUDIO_HOOK = "01_Hook.wav"
AUDIO_EJEMPLOS = "02_Ejemplos.wav"
# Si no lo tienes, déjalo igual y NO lo uses (las llamadas están comentadas)
AUDIO_EXTRA = "03_puente_maclaurin.wav"


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


# ==========================
# ESCENA
# ==========================
class CalculadoraIntro(Scene):

    # -------------------------------------------------------------------------
    # Utilidad: ruta absoluta del audio + verificación
    # -------------------------------------------------------------------------
    def _audio_path(self, filename: str) -> str:
        path = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No existe el audio: {path}")
        return path

    # -------------------------------------------------------------------------
    # (1) SIMULTÁNEO: audio y animación arrancan al mismo tiempo
    # -------------------------------------------------------------------------
    def play_audio_with_anim(
        self,
        animation,
        filename: str,
        anim_run_time: float,
        audio_offset: float = 0.0,   # >0: audio arranca después; <0: arranca antes (ver nota abajo)
        gain: float = 1.0,
        extra_wait: float = 0.15,
        **play_kwargs
    ):
        """
        - add_sound pega el audio al timeline en el tiempo actual de la escena.
        - self.play corre la animación inmediatamente.
        - luego esperamos lo que falte para que termine el audio.

        Nota sobre audio_offset:
        - Si audio_offset = 0.2, el audio empieza 0.2s DESPUÉS del inicio de la animación.
        - Si audio_offset = -0.2, en teoría sería 0.2s ANTES, pero en la práctica Manim no puede
          poner audio "en el pasado" relativo al timeline actual. Para "audio antes", la forma
          sencilla es: self.add_sound(...); self.wait(0.2); self.play(...)
          (te dejo un helper abajo para eso).
        """
        path = self._audio_path(filename)
        dur = audio_duration_wav(path)

        # Pega el audio en el timeline (no bloquea)
        self.add_sound(path, gain=gain, time_offset=audio_offset)

        # Corre la animación
        self.play(animation, run_time=anim_run_time, **play_kwargs)

        # Espera lo restante hasta que acabe el audio (considerando offset)
        end_audio = audio_offset + dur
        restante = end_audio - anim_run_time

        if restante > 0:
            self.wait(restante + extra_wait)
        else:
            self.wait(extra_wait)

    # -------------------------------------------------------------------------
    # Helper simple: "audio empieza ANTES que la animación" (sin offsets negativos)
    # -------------------------------------------------------------------------
    def play_audio_then_wait_then_anim(
        self,
        filename: str,
        wait_before_anim: float,
        animation,
        anim_run_time: float,
        gain: float = 1.0,
        extra_wait: float = 0.15,
        **play_kwargs
    ):
        """
        Caso "audio arranca primero" pero SIN esperar a que termine:
        - Inicia audio
        - Espera wait_before_anim
        - Inicia animación mientras el audio sigue sonando
        - Al final espera lo necesario para que el audio termine
        """
        path = self._audio_path(filename)
        dur = audio_duration_wav(path)

        self.add_sound(path, gain=gain)
        self.wait(wait_before_anim)

        self.play(animation, run_time=anim_run_time, **play_kwargs)

        # ya pasaron wait_before_anim + anim_run_time segundos desde que empezó el audio
        ya = wait_before_anim + anim_run_time
        restante = dur - ya
        if restante > 0:
            self.wait(restante + extra_wait)
        else:
            self.wait(extra_wait)

    # -------------------------------------------------------------------------
    # (2) AUDIO -> ANIM: primero audio completo, luego animación
    # -------------------------------------------------------------------------
    def play_audio_then_anim(
        self,
        filename: str,
        animation,
        anim_run_time: float,
        gain: float = 1.0,
        extra_wait: float = 0.15,
        delay_after_audio: float = 0.0,
        **play_kwargs
    ):
        path = self._audio_path(filename)
        dur = audio_duration_wav(path)

        self.add_sound(path, gain=gain)
        self.wait(dur + extra_wait)

        if delay_after_audio > 0:
            self.wait(delay_after_audio)

        self.play(animation, run_time=anim_run_time, **play_kwargs)

    # -------------------------------------------------------------------------
    # (3) ANIM -> AUDIO: primero animación, luego audio completo
    # -------------------------------------------------------------------------
    def play_anim_then_audio(
        self,
        animation,
        anim_run_time: float,
        filename: str,
        gain: float = 1.0,
        extra_wait: float = 0.15,
        delay_after_anim: float = 0.0,
        **play_kwargs
    ):
        self.play(animation, run_time=anim_run_time, **play_kwargs)

        if delay_after_anim > 0:
            self.wait(delay_after_anim)

        path = self._audio_path(filename)
        dur = audio_duration_wav(path)
        self.add_sound(path, gain=gain)
        self.wait(dur + extra_wait)

    # -------------------------------------------------------------------------
    # Audio + animaciones en secuencia (misma funcion usada en otros archivos)
    # -------------------------------------------------------------------------
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

        A) Paso con animacion:
           {
             "anim": una animacion (ej: FadeIn(obj))
                     o una lista/tupla de animaciones (ej: [Write(a), Write(b)]),
             "run_time": duracion del self.play en segundos,
             ... opcional: kwargs extra para self.play (rate_func, lag_ratio, etc.)
           }

        B) Paso de espera (pausa mientras el audio sigue):
           { "wait": segundos }
        """
        path = self._audio_path(filename)
        dur = audio_duration_wav(path)

        self.add_sound(path, gain=gain)

        elapsed = 0.0
        for step in steps:
            if "call" in step:
                start_t = self.time
                step["call"]()
                elapsed += self.time - start_t
                continue

            if "wait" in step:
                t = float(step["wait"])
                self.wait(t)
                elapsed += t
                continue

            anim = step["anim"]
            run_time = float(step.get("run_time", 1.0))
            elapsed += run_time

            play_kwargs = {k: v for k, v in step.items() if k not in ("anim", "run_time")}

            if isinstance(anim, (list, tuple)):
                self.play(*anim, run_time=run_time, **play_kwargs)
            else:
                self.play(anim, run_time=run_time, **play_kwargs)

        restante = dur - elapsed
        if restante > 0:
            self.wait(restante + extra_wait)
        else:
            self.wait(extra_wait)

    # -------------------------------------------------------------------------
    # Escena
    # -------------------------------------------------------------------------
    def construct(self):

        # =========================================================================================
        # 1) CUERPO
        # =========================================================================================
        cuerpo = RoundedRectangle(
            corner_radius=0.25,
            width=5.6,
            height=7.4,
            fill_opacity=1.0,
            fill_color="#1f1f1f",
            stroke_color=WHITE,
            stroke_width=2
        ).move_to(ORIGIN)

        # =========================================================================================
        # 2) PANTALLA
        # =========================================================================================
        pantalla = RoundedRectangle(
            corner_radius=0.18,
            width=5.0,
            height=1.5,
            fill_opacity=1.0,
            fill_color="#111111",
            stroke_color=WHITE,
            stroke_width=1.5
        )
        pantalla.next_to(cuerpo.get_top(), DOWN, buff=0.55)
        pantalla.move_to([cuerpo.get_center()[0], pantalla.get_center()[1], 0])

        brillo_pantalla = RoundedRectangle(
            corner_radius=0.06,
            width=pantalla.width * 0.98,
            height=0.28,
            fill_opacity=0.16,
            fill_color=WHITE,
            stroke_opacity=0
        )
        brillo_pantalla.move_to(pantalla.get_top() + DOWN * 0.22)

        # =========================================================================================
        # 3) FUNCIÓN BOTÓN
        # =========================================================================================
        def crear_boton(texto: str, color_relleno="#2a2a2a"):
            rect = RoundedRectangle(
                corner_radius=0.12,
                width=1.15,
                height=0.78,
                fill_opacity=1.0,
                fill_color=color_relleno,
                stroke_color=WHITE,
                stroke_width=1
            )
            etiqueta = Text(texto, font="Consolas").scale(0.5)
            etiqueta.move_to(rect.get_center())
            return VGroup(rect, etiqueta)

        # =========================================================================================
        # 4) TECLADO SUPERIOR
        # =========================================================================================
        boton_cos = crear_boton("cos", "#2f2f2f")
        boton_par_izq = crear_boton("(", "#2a2a2a")
        boton_par_der = crear_boton(")", "#2a2a2a")
        boton_igual = crear_boton("=", "#3b3b3b")

        boton_0 = crear_boton("0", "#2a2a2a")
        boton_coma = crear_boton(",", "#2a2a2a")
        boton_punto = crear_boton(".", "#2a2a2a")
        boton_multiplicar = crear_boton("x", "#2a2a2a")

        fila_superior = VGroup(boton_cos, boton_par_izq, boton_par_der, boton_igual).arrange(RIGHT, buff=0.18)
        fila_inferior = VGroup(boton_0, boton_coma, boton_punto, boton_multiplicar).arrange(RIGHT, buff=0.18)

        teclado_superior = VGroup(fila_superior, fila_inferior).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        teclado_superior.next_to(pantalla, DOWN, buff=0.65)
        teclado_superior.align_to(pantalla, LEFT)

        # =========================================================================================
        # 5) TECLADO INFERIOR
        # =========================================================================================
        boton_7 = crear_boton("7")
        boton_8 = crear_boton("8")
        boton_9 = crear_boton("9")
        boton_div = crear_boton("/")

        boton_4 = crear_boton("4")
        boton_5 = crear_boton("5")
        boton_6 = crear_boton("6")
        boton_mas = crear_boton("+")

        boton_1 = crear_boton("1")
        boton_2 = crear_boton("2")
        boton_3 = crear_boton("3")
        boton_menos = crear_boton("-")

        teclado_inferior = VGroup(
            boton_7, boton_8, boton_9, boton_div,
            boton_4, boton_5, boton_6, boton_mas,
            boton_1, boton_2, boton_3, boton_menos,
        )
        teclado_inferior.arrange_in_grid(rows=3, cols=4, buff=0.18)
        teclado_inferior.next_to(teclado_superior, DOWN, buff=1.5)
        teclado_inferior.align_to(teclado_superior, LEFT)

        if teclado_inferior.get_bottom()[1] < (cuerpo.get_bottom()[1] + 0.25):
            teclado_inferior.shift(UP * ((cuerpo.get_bottom()[1] + 0.25) - teclado_inferior.get_bottom()[1]))

        teclado_completo = VGroup(teclado_superior, teclado_inferior)

        # =========================================================================================
        # 6) TEXTO EN PANTALLA
        # =========================================================================================
        tokens = [r"\cos", r"(", r"0", r"{,}", r"8", r")", r"=", r"?"]
        expresion = MathTex(*tokens).scale(0.95).move_to(pantalla.get_center())
        for pedazo in expresion:
            pedazo.set_opacity(0)

        # =========================================================================================
        # 7) ANIMACIÓN PRESIONAR
        # =========================================================================================
        def presionar_boton(boton: VGroup):
            rect = boton[0]
            boton.save_state()

            flash = rect.copy()
            flash.set_stroke(opacity=0)
            flash.set_fill(WHITE, opacity=0.55)
            flash.move_to(rect.get_center())
            flash.set_z_index(10_000)

            boton.set_z_index(9_000)
            color_hundido = "#141414"

            return Succession(
                AnimationGroup(
                    boton.animate.shift(DOWN * 0.14).scale(0.94),
                    rect.animate.set_fill(color_hundido, opacity=1.0),
                    rect.animate.set_stroke(width=2.2, opacity=1.0),
                    FadeIn(flash),
                    lag_ratio=0.0,
                    run_time=0.10
                ),
                AnimationGroup(
                    Restore(boton),
                    FadeOut(flash),
                    lag_ratio=0.0,
                    run_time=0.14
                ),
            )

        # =========================================================================================
        # 8) ARMADO FINAL
        # =========================================================================================
        calculadora = VGroup(cuerpo, pantalla, brillo_pantalla, teclado_completo).scale(0.92).move_to(ORIGIN)

        # -----------------------------------------------------------------------------------------
        # EJEMPLO (CASO 1): audio y FadeIn simultáneo
        # -----------------------------------------------------------------------------------------

        self.add(expresion)

        # =========================================================================================
        # 9) TECLAS cos(0,8)=?
        # =========================================================================================
        mapa_botones = {
            0: boton_cos,
            1: boton_par_izq,
            2: boton_0,
            3: boton_coma,
            4: boton_8,
            5: boton_par_der,
            6: boton_igual,
        }
        def _teclear_expresion():
            for i in range(len(tokens)):
                if i in mapa_botones:
                    self.play(presionar_boton(mapa_botones[i]))
                self.play(expresion[i].animate.set_opacity(1), run_time=0.18)

        self.play_audio_over_animations(
            AUDIO_HOOK,
            {"anim": FadeIn(calculadora, shift=DOWN), "run_time": 2},
            {"wait": 4},
            {"call": _teclear_expresion},
            {"wait": 2.0},
            extra_wait=0.20,
        )

        # =========================================================================================
        # 10) RESULTADO
        # =========================================================================================
        valor = math.cos(0.8)
        valor_txt = f"{valor:.4f}"
        resultado = MathTex(r"\cos", r"(", r"0", r"{,}", r"8", r")", r"=", valor_txt).scale(0.95)
        resultado.move_to(expresion.get_center())

        # -----------------------------------------------------------------------------------------
        # "DISPARAR" AUDIO AL PRESIONAR "=" (simultáneo con el click)
        # Duración del click = 0.10 + 0.14 = 0.24s
        # Aquí haces que el audio comience EXACTO cuando hundes el "=".
        # -----------------------------------------------------------------------------------------
        self.play_audio_over_animations(
            AUDIO_EJEMPLOS,
            {"anim": presionar_boton(boton_igual), "run_time": 0.5},
            {"anim": TransformMatchingTex(expresion, resultado), "run_time": 2},
            {"wait": 3},
            extra_wait=0.10,
        )

        # -----------------------------------------------------------------------------------------
        # Luego haces el transform visual (puede ser sin audio o con otro audio)
        # Si quieres que el MISMO audio acompañe el transform, usa el "together" aquí y
        # en el click pones un audio cortito tipo "click.wav".
        # -----------------------------------------------------------------------------------------

        # =========================================================================================
        # EJEMPLOS HIPOTÉTICOS DE LOS OTROS DOS MODOS (NO se ejecutan: están comentados)
        # =========================================================================================

        # -------- CASO 2: AUDIO -> ANIM (primero habla completo, luego haces una animación) ------
        # self.play_audio_then_anim(
        #     AUDIO_EXTRA,
        #     FadeOut(resultado),
        #     anim_run_time=0.5,
        #     delay_after_audio=0.2
        # )

        # -------- CASO 3: ANIM -> AUDIO (primero animas, luego narras completo) -----------------
        # self.play_anim_then_audio(
        #     FadeOut(resultado),
        #     anim_run_time=0.5,
        #     filename=AUDIO_EXTRA,
        #     delay_after_anim=0.2
        # )

        # -------- BONUS: audio empieza ANTES y luego entra la animación mientras sigue sonando ---
        # self.play_audio_then_wait_then_anim(
        #     AUDIO_EXTRA,
        #     wait_before_anim=0.4,
        #     animation=FadeOut(resultado),
        #     anim_run_time=0.5
        # )
