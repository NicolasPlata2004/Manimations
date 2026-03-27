from manim import *
import numpy as np

# Paleta de colores
COLOR_BLUE = "#517696"

config.background_color = WHITE

class ConstructionScene(Scene):
    def construct(self):
        # --- INTRO ---
        intro_text = Tex(
            r"¿Cómo creamos la ecuación\\del trébol estilizado?", 
            color=BLACK, font_size=42, tex_environment="center"
        )
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # --- PLANO POLAR (Expandido para Etapa 4) ---
        polar_plane = PolarPlane(
            radius_max=4.0,
            radius_step=0.5,
            azimuth_step=30 * DEGREES,
            size=7.0, # Un poco más grande para compensar el radio max 4
            background_line_style={
                "stroke_color": GREY_C, 
                "stroke_opacity": 0.8,
                "stroke_width": 2.0
            },
            azimuth_units="degrees"
        )
        
        # Etiquetas Manuales para evitar superposiciones
        radial_labels = VGroup()
        for r_val in np.arange(0.5, 4.5, 0.5):
            lbl = MathTex(f"{r_val}", color=BLACK, font_size=18)
            lbl.move_to(polar_plane.polar_to_point(r_val, 0) + DOWN * 0.25)
            radial_labels.add(lbl)
            
        azimuth_labels = VGroup()
        for angle_deg in range(0, 360, 30):
            lbl = MathTex(f"{angle_deg}^\\circ", color=BLACK, font_size=18)
            angle_rad = angle_deg * DEGREES
            lbl.move_to(polar_plane.polar_to_point(4.0 + 0.35, angle_rad))
            azimuth_labels.add(lbl)
            
        polar_plane.add(radial_labels, azimuth_labels)
        polar_plane.shift(LEFT * 3.5).scale(0.7) # Escalado para que quepa todo el radio 4 y texto a la derecha

        # Texto base para reutilizar posición a la derecha
        text_anchor = polar_plane.get_right() + RIGHT * 0.4 + UP * 2.2

        # --- ETAPA 1: r = a (Escena 1) ---
        title1 = MathTex(r"1)\ r = a", color=BLACK).to_corner(UL).scale(1.2)
        circle_a = ParametricFunction(
            lambda t: polar_plane.polar_to_point(1, t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        desc1 = Tex(
            r"Radio constante,\\es un simple círculo", 
            color=BLACK, font_size=24
        ).move_to(text_anchor, aligned_edge=LEFT)

        self.play(Write(title1))
        self.play(Create(polar_plane))
        self.play(Create(circle_a), Write(desc1))
        self.wait(2)
        self.play(FadeOut(circle_a), FadeOut(desc1), FadeOut(title1))

        # --- ETAPA 2: r = cos(k * theta) (Escena 2) ---
        title2 = MathTex(r"2)\ r = \cos(k \cdot \theta)", color=BLACK).to_corner(UL).scale(1.2)
        
        k_tracker = ValueTracker(3)
        def get_cos_curve():
            k = k_tracker.get_value()
            return ParametricFunction(
                lambda t: polar_plane.polar_to_point(np.cos(k * t), t),
                t_range=[0, 2*PI],
                color=COLOR_BLUE, stroke_width=4
            )
        cos_curve = always_redraw(get_cos_curve)
        
        text2_1 = Tex(
            r"Al meter el ángulo dentro de un\\coseno, el radio deja de ser\\constante y empieza a `entrar y\\salir' del centro.",
            color=BLACK, font_size=20
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        text2_2 = Tex(
            r"$\bullet$ Si $k$ es entero: Determina el número\\de pétalos. Si $k$ es impar (como 7),\\la rosa tiene $k$ pétalos.\\Si es par, tiene $2k$.",
            color=BLACK, font_size=20
        ).next_to(text2_1, DOWN, buff=0.4, aligned_edge=LEFT)
        
        text2_3 = Tex(
            r"$\bullet$ El primer pétalo nace `acostado'\\sobre el eje horizontal (Eje X).\\Esto es porque $\cos(0) = 1$\\(máxima extensión).",
            color=BLACK, font_size=20
        ).next_to(text2_2, DOWN, buff=0.4, aligned_edge=LEFT)

        self.play(Write(title2), Create(cos_curve))
        self.wait(1)
        self.play(Write(text2_1))
        self.wait(0.5)
        
        for k_val in [4, 5, 6, 7]:
            self.play(k_tracker.animate.set_value(k_val), run_time=1.5)
            if k_val == 5: self.play(Write(text2_2))
            if k_val == 7: self.play(Write(text2_3))
            self.wait(1)
        
        self.wait(1)
        self.play(FadeOut(cos_curve), FadeOut(text2_1), FadeOut(text2_2), FadeOut(text2_3), FadeOut(title2))

        # --- ETAPA 3: r = sin(k * theta) (Escena 3) ---
        title3_cos = MathTex(r"3)\ r = \cos(k \cdot \theta)", color=BLACK).to_corner(UL).scale(1.2)
        title3_sin = MathTex(r"3)\ r = \sin(k \cdot \theta)", color=BLACK).to_corner(UL).scale(1.2)
        
        curve_3_cos = ParametricFunction(
            lambda t: polar_plane.polar_to_point(np.cos(3 * t), t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        curve_3_sin = ParametricFunction(
            lambda t: polar_plane.polar_to_point(np.sin(3 * t), t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        
        text3 = Tex(
            r"Primer pétalo nace `girado'.\\Esto es porque $\sin(0)=0$. El brazo\\empieza en el centro y el primer pico\\del pétalo ocurre un poco después.",
            color=BLACK, font_size=20
        ).move_to(text_anchor, aligned_edge=LEFT)

        self.play(Write(title3_cos), Create(curve_3_cos))
        self.wait(1.5)
        self.play(Transform(title3_cos, title3_sin), Transform(curve_3_cos, curve_3_sin), run_time=2)
        self.wait(0.5)
        self.play(Write(text3))
        self.wait(2)
        self.play(FadeOut(text3), FadeOut(title3_cos)) # Remove title3_cos (which became title3_sin)

        # --- ETAPA 4: r = a + sin(k * theta) (Escena 4) ---
        title4 = MathTex(r"4)\ r = a + \sin(k \cdot \theta)", color=BLACK).to_corner(UL).scale(1.2)
        
        a_tracker = ValueTracker(0)
        def get_elevated_curve():
            a = a_tracker.get_value()
            return ParametricFunction(
                lambda t: polar_plane.polar_to_point(a + np.sin(3 * t), t),
                t_range=[0, 2*PI],
                color=COLOR_BLUE, stroke_width=4
            )
        elevated_curve = always_redraw(get_elevated_curve)

        desc4 = Tex(
            r"Su función es ``empujar'' todos los puntos de\\la trayectoria hacia afuera del origen\\de forma uniforme. A medida que ``$a$''\\aumenta, el hueco crece, pero también\\el tamaño total de la flor $r_{max} = a + b$.",
            color=BLACK, font_size=18
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        desc4_bottom = Tex(
            r"Se observa que si $a \leq b$ no hay espacio\\libre en el centro. Se requiere $a > b$\\para generar una trayectoria con radio\\mínimo positivo y evitar el centro del sistema.",
            color=BLACK, font_size=18
        ).next_to(desc4, DOWN, buff=0.4, aligned_edge=LEFT)

        self.play(Write(title4))
        self.add(elevated_curve) # curve_3_sin was already sin(3t), elevated_curve starts at a=0 so it's the same
        self.remove(curve_3_sin)
        
        self.play(Write(desc4))
        self.wait(1)
        
        for a_val in [1.0, 2.0, 3.0]:
            self.play(a_tracker.animate.set_value(a_val), run_time=2)
            if a_val == 2.0: self.play(Write(desc4_bottom))
            self.wait(1.5)

        self.wait(3)
        self.play(FadeOut(elevated_curve), FadeOut(desc4), FadeOut(desc4_bottom), FadeOut(title4), FadeOut(polar_plane))
        self.wait(1)
