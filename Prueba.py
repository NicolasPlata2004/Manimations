# CalculadoraIntro.py
import math
from manim import *


class CalculadoraIntro(Scene):
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
        pantalla.move_to([cuerpo.get_center()[0], pantalla.get_center()[1], 0])  # centrado horizontal real

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
            boton = VGroup(rect, etiqueta)
            return boton

        # =========================================================================================
        # 4) TECLADO SUPERIOR (cos ( ) =  y 0 , . x)
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
        # 5) TECLADO INFERIOR (decorativo 7-1)
        # =========================================================================================
        boton_7 = crear_boton("7")
        boton_8 = crear_boton("8")   # <- 8 aquí (posición "del medio" en 7 8 9)
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
        #teclado_inferior.scale(0.95)

        teclado_inferior.next_to(teclado_superior, DOWN, buff=1.5)#.shift(UP * 1.4)
        teclado_inferior.align_to(teclado_superior, LEFT)

        # Blindaje para que no se salga por abajo
        if teclado_inferior.get_bottom()[1] < (cuerpo.get_bottom()[1] + 0.25):
            teclado_inferior.shift(UP * ((cuerpo.get_bottom()[1] + 0.25) - teclado_inferior.get_bottom()[1]))

        teclado_completo = VGroup(teclado_superior, teclado_inferior)

        # =========================================================================================
        # 6) TEXTO EN PANTALLA
        # =========================================================================================
        tokens = [r"\cos", r"(", r"0", r"{,}", r"8", r")", r"=", r"?"]
        expresion = MathTex(*tokens).scale(0.95)
        expresion.move_to(pantalla.get_center())

        for pedazo in expresion:
            pedazo.set_opacity(0)

        # =========================================================================================
        # 7) ANIMACIÓN DE PRESIONAR (AHORA SÍ SE NOTA)
        # =========================================================================================
        def presionar_boton(boton: VGroup):
            """
            Presión visible:
            - hundimiento fuerte (baja más)
            - escala más notoria
            - flash claro arriba (más opacidad)
            - el relleno se oscurece y el borde se ilumina un poco
            - vuelve EXACTO al estado original
            """
            rect = boton[0]
            etiqueta = boton[1]

            boton.save_state()

            # Flash MUY visible encima
            flash = rect.copy()
            flash.set_stroke(opacity=0)
            flash.set_fill(WHITE, opacity=0.55)
            flash.move_to(rect.get_center())
            flash.set_z_index(10_000)  # ultra arriba

            # Asegurar que el botón esté por encima del teclado
            boton.set_z_index(9_000)

            # Estado hundido (más oscuro)
            color_hundido = "#141414"

            return Succession(
                AnimationGroup(
                    boton.animate.shift(DOWN * 0.14).scale(0.94),        # <- MÁS hundimiento y escala
                    rect.animate.set_fill(color_hundido, opacity=1.0),
                    rect.animate.set_stroke(width=2.2, opacity=1.0),     # <- borde más “presente”
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
        calculadora = VGroup(cuerpo, pantalla, brillo_pantalla, teclado_completo)

        # Para agrandar/achicar la calculadora: cambia este número
        calculadora.scale(0.92).move_to(ORIGIN)

        self.play(FadeIn(calculadora, shift=DOWN), run_time=2)
        self.wait(3)
        self.add(expresion)

        # =========================================================================================
        # 9) SECUENCIA DE TECLAS cos(0,8)=?
        # =========================================================================================
        mapa_botones = {
            0: boton_cos,
            1: boton_par_izq,
            2: boton_0,
            3: boton_coma,
            4: boton_8,       # <- 8 sale de la fila 7-8-9
            5: boton_par_der,
            6: boton_igual,
        }

        for i in range(len(tokens)):
            if i in mapa_botones:
                self.play(presionar_boton(mapa_botones[i]))
            self.play(expresion[i].animate.set_opacity(1), run_time=0.18)

        self.wait(5)

        # =========================================================================================
        # 10) RESULTADO
        # =========================================================================================
        valor = math.cos(0.8)
        valor_txt = f"{valor:.4f}"

        resultado = MathTex(r"\cos", r"(", r"0", r"{,}", r"8", r")", r"=", valor_txt).scale(0.95)
        resultado.move_to(expresion.get_center())

        self.play(presionar_boton(boton_igual))
        self.play(TransformMatchingTex(expresion, resultado), run_time=0.6)
        self.wait(0.6)