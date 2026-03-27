from manim import *
import numpy as np

# Paleta de colores
COLOR_BLUE = "#517696"
COLOR_HIGHLIGHT = "#D95C14"

config.background_color = WHITE

class ConstructionScene(Scene):
    def construct(self):
        # --- INTRO ---
        intro_text = Tex(
            r"¿Cómo creamos la ecuación\\del trébol estilizado?", 
            color=BLACK, font_size=48, tex_environment="center"
        )
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # --- PLANO POLAR (Radio 9 para soportar Escala 1.5) ---
        polar_plane = PolarPlane(
            radius_max=9.0,
            radius_step=0.5,
            azimuth_step=30 * DEGREES,
            size=9.5, # Agrando campo visual
            background_line_style={
                "stroke_color": GREY_C, 
                "stroke_opacity": 0.8,
                "stroke_width": 2.0
            },
            azimuth_units="degrees"
        )
        
        radial_labels = VGroup()
        for r_val in np.arange(0.5, 9.5, 0.5):
            lbl = MathTex(f"{r_val}", color=BLACK, font_size=16)
            lbl.move_to(polar_plane.polar_to_point(r_val, 0) + DOWN * 0.25)
            radial_labels.add(lbl)
            
        azimuth_labels = VGroup()
        for angle_deg in range(0, 360, 30):
            lbl = MathTex(f"{angle_deg}^\\circ", color=BLACK, font_size=16)
            angle_rad = angle_deg * DEGREES
            lbl.move_to(polar_plane.polar_to_point(9.0 + 0.35, angle_rad))
            azimuth_labels.add(lbl)
            
        polar_plane.add(radial_labels, azimuth_labels)
        polar_plane.shift(LEFT * 4.4).scale(0.5) # Más zoom out para radio 9

        text_anchor = polar_plane.get_right() + RIGHT * 0.3 + UP * 2.5

        # --- ETAPA 1: r = a (Escena 1) ---
        title1 = MathTex(r"1)\ r =", r"a", color=BLACK).to_corner(UL, buff=0.5).scale(1.1)
        
        desc1 = Tex(
            r"Radio constante,\\es un simple círculo.", 
            color=BLACK, font_size=32
        ).move_to(text_anchor, aligned_edge=LEFT)

        circle_a = ParametricFunction(
            lambda t: polar_plane.polar_to_point(1, t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        val1 = MathTex("a = 1.00", color=BLACK, font_size=32).next_to(polar_plane, DOWN, buff=0.4)

        self.play(Write(title1))
        self.play(Indicate(title1[1], color=COLOR_HIGHLIGHT))
        self.play(Write(desc1))
        self.play(Create(polar_plane))
        self.play(Create(circle_a), Write(val1))
        self.wait(2)
        self.play(FadeOut(circle_a), FadeOut(desc1), FadeOut(title1), FadeOut(val1))

        # --- ETAPA 2: r = cos(k * theta) (Escena 2) ---
        title2 = MathTex(r"2)\ r =", r"\cos(k \cdot \theta)", color=BLACK).to_corner(UL, buff=0.5).scale(1.1)
        
        text2_1 = Tex(
            r"Al meter el ángulo dentro de un coseno, el radio\\deja de ser constante y empieza a `entrar y salir'\\del centro.",
            color=BLACK, font_size=26
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        text2_2 = Tex(
            r"$\bullet$ Si $k$ es entero: Determina el número de pétalos.\\Si $k$ es impar (como 7), la rosa tiene $k$ pétalos.\\Si es par, tiene $2k$.",
            color=BLACK, font_size=26
        ).next_to(text2_1, DOWN, buff=0.4, aligned_edge=LEFT)
        
        text2_3 = Tex(
            r"$\bullet$ El primer pétalo nace `acostado' sobre el eje\\horizontal (Eje X). Esto es porque $\cos(0) = 1$\\(máxima extensión).",
            color=BLACK, font_size=26
        ).next_to(text2_2, DOWN, buff=0.4, aligned_edge=LEFT)

        self.play(Write(title2))
        self.play(Indicate(title2[1], color=COLOR_HIGHLIGHT))
        self.play(Write(text2_1))

        k_tracker = ValueTracker(3)
        cos_curve = always_redraw(lambda: ParametricFunction(
            lambda t: polar_plane.polar_to_point(np.cos(k_tracker.get_value() * t), t),
            t_range=[0, 2*PI], color=COLOR_BLUE, stroke_width=4
        ))
        val2 = always_redraw(lambda: MathTex(f"k = {k_tracker.get_value():.2f}", color=BLACK, font_size=32).next_to(polar_plane, DOWN, buff=0.4))

        self.play(Create(cos_curve), Write(val2))
        self.wait(1)
        
        for k_val in [4, 5, 6, 7]:
            self.play(k_tracker.animate.set_value(k_val), run_time=1.5)
            if k_val == 5: self.play(Write(text2_2))
            if k_val == 7: self.play(Write(text2_3))
            self.wait(1)
        
        self.play(FadeOut(cos_curve), FadeOut(text2_1), FadeOut(text2_2), FadeOut(text2_3), FadeOut(title2), FadeOut(val2))

        # --- ETAPA 3: r = sin(k * theta) (Escena 3) ---
        title3_cos = MathTex(r"3)\ r =", r"\cos", r"(k \cdot \theta)", color=BLACK).to_corner(UL, buff=0.5).scale(1.1)
        title3_sin = MathTex(r"3)\ r =", r"\sin", r"(k \cdot \theta)", color=BLACK).to_corner(UL, buff=0.5).scale(1.1)
        
        text3 = Tex(
            r"Primer pétalo nace `girado'.\\Esto es porque $\sin(0)=0$. El brazo\\empieza en el centro y el primer pico\\del pétalo ocurre un poco después.",
            color=BLACK, font_size=26
        ).move_to(text_anchor, aligned_edge=LEFT)

        curve_3_cos = ParametricFunction(
            lambda t: polar_plane.polar_to_point(np.cos(3 * t), t),
            t_range=[0, 2*PI], color=COLOR_BLUE, stroke_width=4
        )
        curve_3_sin = ParametricFunction(
            lambda t: polar_plane.polar_to_point(np.sin(3 * t), t),
            t_range=[0, 2*PI], color=COLOR_BLUE, stroke_width=4
        )
        val3 = MathTex("k = 3.00", color=BLACK, font_size=32).next_to(polar_plane, DOWN, buff=0.4)

        self.play(Write(title3_cos))
        self.play(Write(text3))
        self.play(Create(curve_3_cos), Write(val3))
        self.wait(1.5)
        
        self.play(
            Transform(title3_cos, title3_sin), 
            Transform(curve_3_cos, curve_3_sin),
            run_time=2
        )
        self.play(Indicate(title3_cos[1], color=COLOR_HIGHLIGHT))
        self.wait(2)

        self.play(FadeOut(curve_3_cos), FadeOut(text3), FadeOut(title3_cos), FadeOut(val3))

        # --- ETAPA 4: r = a + sin(k * theta) (Escena 4) ---
        title4 = MathTex(r"4)\ r =", r"a +", r"\sin(k \cdot \theta)", color=BLACK).to_corner(UL, buff=0.5).scale(1.1)
        
        desc4 = Tex(
            r"Su función es ``empujar'' todos los puntos de la\\trayectoria hacia afuera del origen de forma uniforme.\\A medida que ``$a$'' aumenta, el hueco crece, pero también\\el tamaño total de la flor $r_{max} = a + b$.",
            color=BLACK, font_size=24
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        desc4_bottom = Tex(
            r"Se observa que si $a \leq b$ no hay espacio libre\\en el centro. Se requiere $a > b$ para generar una\\trayectoria con radio mínimo positivo y evitar\\el centro del sistema.",
            color=BLACK, font_size=24
        ).next_to(desc4, DOWN, buff=0.4, aligned_edge=LEFT)
        
        a_tracker = ValueTracker(0)
        elevated_curve = always_redraw(lambda: ParametricFunction(
            lambda t: polar_plane.polar_to_point(a_tracker.get_value() + np.sin(3 * t), t),
            t_range=[0, 2*PI], color=COLOR_BLUE, stroke_width=4
        ))
        val4 = always_redraw(lambda: MathTex(f"a = {a_tracker.get_value():.2f}", color=BLACK, font_size=32).next_to(polar_plane, DOWN, buff=0.4))

        self.play(Write(title4))
        self.play(Indicate(title4[1], color=COLOR_HIGHLIGHT))
        self.play(Write(desc4))
        self.play(Create(elevated_curve), Write(val4))
        self.wait(1)
        
        for a_val in [1.0, 2.0, 3.0]:
            self.play(a_tracker.animate.set_value(a_val), run_time=2)
            if a_val == 2.0: self.play(Write(desc4_bottom))
            self.wait(1.5)

        self.wait(1)
        self.play(FadeOut(elevated_curve), FadeOut(desc4), FadeOut(desc4_bottom), FadeOut(title4), FadeOut(val4))

        # --- ETAPA 5: r = a + b * sin(k * theta) (Escena 5) ---
        title5 = MathTex(r"5)\ r =", r"a +", r"b \cdot", r"\sin(k \cdot \theta)", color=BLACK).to_corner(UL, buff=0.5).scale(1.1)
        
        desc5 = Tex(
            r"Mientras que $a$ define la posición media, $b$ define la\\ \textbf{intensidad} del pétalo. Es la distancia máxima que\\el brazo se aleja de su radio base. Al aumentar $b$,\\los pétalos se vuelven más prominentes.",
            color=BLACK, font_size=24
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        formulas5 = MathTex(
            r"r_{max} = a + b \quad \text{(Punta del pétalo)}\\",
            r"r_{min} = a - b \quad \text{(Valle del pétalo)}",
            color=BLACK, font_size=32
        ).next_to(desc5, DOWN, buff=0.6).set_x(desc5.get_x())

        b_tracker = ValueTracker(1) 
        final_curve = always_redraw(lambda: ParametricFunction(
            lambda t: polar_plane.polar_to_point(3 + b_tracker.get_value() * np.sin(3 * t), t),
            t_range=[0, 2*PI], color=COLOR_BLUE, stroke_width=4
        ))
        val5 = always_redraw(lambda: MathTex(
            rf"a = 3.00, \quad b = {b_tracker.get_value():.2f}, \quad k = 3.00", 
            color=BLACK, font_size=32
        ).next_to(polar_plane, DOWN, buff=0.4))

        self.play(Write(title5))
        self.play(Indicate(title5[2], color=COLOR_HIGHLIGHT))
        self.play(Write(desc5))
        self.play(Write(formulas5))
        self.play(Create(final_curve), Write(val5))
        self.wait(1)
        
        for b_val in [2.0, 3.0]:
            self.play(b_tracker.animate.set_value(b_val), run_time=2)
            self.wait(1.5)

        self.wait(1)
        self.play(FadeOut(final_curve), FadeOut(desc5), FadeOut(formulas5), FadeOut(title5), FadeOut(val5))

        # --- ETAPA 6: r = a + b * sin(k * theta + d) (Escena 6) ---
        title6 = MathTex(r"6)\ r =", r"a + b \cdot \sin(k \cdot \theta", r" + d", r")", color=BLACK).to_corner(UL, buff=0.5).scale(1.1)
        
        desc6 = Tex(
            r"$d$ (radianes) añade una rotación a la flor\\ \textbf{PERO} esta rotación es:",
            color=BLACK, font_size=32, tex_environment="center"
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        formula6 = MathTex(
            r"\theta_{rot} = \frac{d}{k}",
            color=BLACK, font_size=42
        ).next_to(desc6, DOWN, buff=0.6).set_x(desc6.get_x())

        d_tracker = ValueTracker(30 * DEGREES) 
        rotated_curve = always_redraw(lambda: ParametricFunction(
            lambda t: polar_plane.polar_to_point(3 + 3 * np.sin(3 * t + d_tracker.get_value()), t),
            t_range=[0, 2*PI], color=COLOR_BLUE, stroke_width=4
        ))
        val6 = always_redraw(lambda: MathTex(
            rf"d = {d_tracker.get_value()/DEGREES:.1f}^\circ, \quad \theta_{{rot}} = {d_tracker.get_value()/(3*DEGREES):.1f}^\circ", 
            color=BLACK, font_size=32
        ).next_to(polar_plane, DOWN, buff=0.4))

        self.play(Write(title6))
        self.play(Indicate(title6[2], color=COLOR_HIGHLIGHT))
        self.play(Write(desc6))
        self.play(Write(formula6))
        self.play(Create(rotated_curve), Write(val6))
        self.wait(1)
        
        self.play(d_tracker.animate.set_value(90 * DEGREES), run_time=4)
        self.wait(2)
        self.play(FadeOut(rotated_curve), FadeOut(desc6), FadeOut(formula6), FadeOut(title6), FadeOut(val6))

        # --- ETAPA 7: r = a + b * sin(k * theta + k * d) (Escena 7) ---
        title7 = MathTex(r"7)\ r =", r"a + b \cdot \sin(k \cdot \theta", r" + k \cdot d", r")", color=BLACK).to_corner(UL, buff=0.5).scale(1.1)
        
        desc7 = Tex(
            r"Para que la flor gire de verdad lo que\\queremos, tenemos que compensar esa\\frecuencia multiplicando ``$d$'' por la\\misma cantidad de pétalos ``$k$''.",
            color=BLACK, font_size=26
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        formula7 = MathTex(
            r"\text{Fase} = k \cdot d",
            color=BLACK, font_size=42
        ).next_to(desc7, DOWN, buff=0.6).set_x(desc7.get_x())

        d_comp_tracker = ValueTracker(30 * DEGREES)
        comp_curve = always_redraw(lambda: ParametricFunction(
            lambda t: polar_plane.polar_to_point(3 + 3 * np.sin(3 * t + 3 * d_comp_tracker.get_value()), t),
            t_range=[0, 2*PI], color=COLOR_BLUE, stroke_width=4
        ))
        val7 = always_redraw(lambda: MathTex(
            rf"\text{Fase} = {3 * d_comp_tracker.get_value()/DEGREES:.1f}^\circ, \quad \text{Rotación} = {d_comp_tracker.get_value()/DEGREES:.1f}^\circ", 
            color=BLACK, font_size=32
        ).next_to(polar_plane, DOWN, buff=0.4))

        self.play(Write(title7))
        self.play(Indicate(title7[2], color=COLOR_HIGHLIGHT))
        self.play(Write(desc7))
        self.play(Write(formula7))
        self.play(Create(comp_curve), Write(val7))
        self.wait(1)
        self.play(d_comp_tracker.animate.set_value(90 * DEGREES), run_time=4)
        self.wait(2)
        self.play(FadeOut(comp_curve), FadeOut(desc7), FadeOut(formula7), FadeOut(title7), FadeOut(val7))

        # --- ETAPA 8: r = escala * (a + b * sin(k * theta + k * d)) (Escena 8) ---
        title8 = MathTex(r"8)\ r =", r"\text{Escala}", r"\cdot (a + b \cdot \sin(k \cdot \theta + k \cdot d))", color=BLACK).to_corner(UL, buff=0.5).scale(1.0)
        
        desc8 = Tex(
            r"Finalmente, aplicamos un multiplicador de\\ \textbf{Escala}. Este factor transforma las unidades\\abstractas de la función en medidas físicas\\reales (mm o cm), asegurando que la\\trayectoria se ajuste al área del robot.",
            color=BLACK, font_size=24
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        scale_tracker = ValueTracker(1.0)
        scaled_curve = always_redraw(lambda: ParametricFunction(
            lambda t: polar_plane.polar_to_point(scale_tracker.get_value() * (3 + 3 * np.sin(3 * t + 3 * PI/2)), t),
            t_range=[0, 2*PI], color=COLOR_BLUE, stroke_width=4
        ))
        val8 = always_redraw(lambda: MathTex(
            rf"\text{Escala} = {scale_tracker.get_value():.2f}, \quad r_{{max}} = {scale_tracker.get_value()*6:.2f}", 
            color=BLACK, font_size=32
        ).next_to(polar_plane, DOWN, buff=0.4))

        self.play(Write(title8))
        self.play(Indicate(title8[1], color=COLOR_HIGHLIGHT))
        self.play(Write(desc8))
        self.play(Create(scaled_curve), Write(val8))
        self.wait(1)
        
        for s_val in [0.75, 1.5]:
            self.play(scale_tracker.animate.set_value(s_val), run_time=3)
            self.wait(1.5)

        self.wait(3)
        self.play(FadeOut(scaled_curve), FadeOut(desc8), FadeOut(title8), FadeOut(val8), FadeOut(polar_plane))
        self.wait(1)
