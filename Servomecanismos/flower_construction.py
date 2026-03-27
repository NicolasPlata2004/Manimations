from manim import *
import numpy as np

# Paleta de colores
COLOR_BLUE = "#517696"

config.background_color = WHITE

class ConstructionScene(Scene):
    def construct(self):
        # --- INTRO ---
        intro_text = Text(
            "¿Cómo creamos la ecuación\ndel trébol estilizado?", 
            color=BLACK, font_size=42, weight=BOLD,
            line_spacing=1.2
        )
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # --- PLANO POLAR (Común) ---
        polar_plane = PolarPlane(
            radius_max=2.0,
            radius_step=0.5,
            azimuth_step=30 * DEGREES,
            size=6.0,
            background_line_style={
                "stroke_color": GREY_C, 
                "stroke_opacity": 0.8,
                "stroke_width": 2.0
            },
            azimuth_units="degrees"
        )
        
        # Etiquetas Manuales para evitar superposiciones de Manim (.add_coordinates)
        radial_labels = VGroup()
        for r_val in [0.5, 1.0, 1.5, 2.0]:
            lbl = MathTex(f"{r_val}", color=BLACK, font_size=20)
            lbl.move_to(polar_plane.polar_to_point(r_val, 0) + DOWN * 0.25)
            radial_labels.add(lbl)
            
        azimuth_labels = VGroup()
        for angle_deg in range(0, 360, 30):
            lbl = MathTex(f"{angle_deg}^\\circ", color=BLACK, font_size=20)
            angle_rad = angle_deg * DEGREES
            lbl.move_to(polar_plane.polar_to_point(2.0 + 0.35, angle_rad))
            azimuth_labels.add(lbl)
            
        # Agregamos las etiquetas como hijos del plano polar para que se muevan con él
        polar_plane.add(radial_labels, azimuth_labels)
        polar_plane.shift(LEFT * 3).scale(0.85)

        # Texto base para reutilizar posición a la derecha cuidando los limites
        text_anchor = polar_plane.get_right() + RIGHT * 0.5 + UP * 2

        # --- ETAPA 1: r = a (Imagen 2) ---
        title1 = MathTex(r"1)\ r = a", color=BLACK).to_corner(UL).scale(1.2)
        circle_a = ParametricFunction(
            lambda t: polar_plane.polar_to_point(1, t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        desc1 = Text(
            "Radio constante,\nes un simple círculo", 
            color=BLACK, font_size=20, line_spacing=0.8
        ).move_to(text_anchor, aligned_edge=LEFT)

        self.play(Write(title1))
        self.play(Create(polar_plane))
        self.play(Create(circle_a), Write(desc1))
        self.wait(2)
        self.play(FadeOut(circle_a), FadeOut(desc1), FadeOut(title1))

        # --- ETAPA 2: r = cos(k * theta) (Imagen 3) ---
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
        
        text2_1 = Text(
            "Al meter el ángulo dentro de un\ncoseno, el radio deja de ser\nconstante y empieza a 'entrar y\nsalir' del centro.",
            color=BLACK, font_size=16, line_spacing=0.8
        ).move_to(text_anchor, aligned_edge=LEFT)
        
        text2_2 = Text(
            "• Si k es entero: Determina el número\n  de pétalos. Si k es impar (como 7),\n  la rosa tiene k pétalos.\n  Si es par, tiene 2k.",
            color=BLACK, font_size=16, line_spacing=0.8
        ).next_to(text2_1, DOWN, buff=0.4, aligned_edge=LEFT)
        
        text2_3 = Text(
            "• El primer pétalo nace 'acostado'\n  sobre el eje horizontal (Eje X).\n  Esto es porque cos(0) = 1\n  (máxima extensión).",
            color=BLACK, font_size=16, line_spacing=0.8
        ).next_to(text2_2, DOWN, buff=0.4, aligned_edge=LEFT)

        self.play(Write(title2), Create(cos_curve))
        self.wait(1)
        self.play(Write(text2_1))
        self.wait(0.5)
        
        # Animaciones de transición deteniéndose en enteros
        self.play(k_tracker.animate.set_value(4), run_time=1.5)
        self.wait(1)
        
        self.play(k_tracker.animate.set_value(5), Write(text2_2), run_time=1.5)
        self.wait(1)
        
        self.play(k_tracker.animate.set_value(6), run_time=1.5)
        self.wait(1)
        
        self.play(k_tracker.animate.set_value(7), Write(text2_3), run_time=1.5)
        self.wait(2)

        self.play(FadeOut(cos_curve), FadeOut(text2_1), FadeOut(text2_2), FadeOut(text2_3), FadeOut(title2))

        # --- ETAPA 3: r = sin(k * theta) (Imagen 4) ---
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
        
        text3 = Text(
            "Primer pétalo nace 'girado'.\nEsto es porque sin(0)=0. El brazo\nempieza en el centro y el primer pico\ndel pétalo ocurre un poco después.",
            color=BLACK, font_size=16, line_spacing=0.8
        ).move_to(text_anchor, aligned_edge=LEFT)

        self.play(Write(title3_cos), Create(curve_3_cos))
        self.wait(1.5)
        
        # Transición fluida de la curva del Coseno al Seno
        self.play(
            Transform(title3_cos, title3_sin), 
            Transform(curve_3_cos, curve_3_sin),
            run_time=2
        )
        self.wait(0.5)
        
        self.play(Write(text3))
        self.wait(3)

        self.play(FadeOut(curve_3_cos), FadeOut(text3), FadeOut(title3_cos), FadeOut(polar_plane))
        self.wait(1)
