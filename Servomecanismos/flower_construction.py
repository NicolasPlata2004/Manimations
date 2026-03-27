from manim import *
import numpy as np

# Configuración global de Manim
config.background_color = WHITE

# Colores sugeridos
COLOR_BLUE = "#517696"

class ConstructionScene(Scene):
    def construct(self):
        # --- ESCENA INTRO ---
        # Usamos Tex para el formato "original de Manim"
        intro_text = Tex(
            r"¿Cómo creamos la ecuación\\del trébol estilizado?", 
            color=BLACK, font_size=42
        )
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # --- PLANO POLAR (Ajustado) ---
        polar_plane = PolarPlane(
            radius_max=2,
            radius_step=0.5,
            azimuth_step=30 * DEGREES,
            size=7.0,
            # 'stroke_color' para que se vean los rayos (azimuth lines)
            background_line_style={
                "stroke_color": GREY_A,
                "stroke_width": 1,
                "stroke_opacity": 0.5
            },
            azimuth_units="degrees",
        ).add_coordinates().shift(LEFT * 3.2).scale(0.8)

        # Aseguramos que todas las etiquetas (radios y ángulos) sean negras (LaTeX style)
        for label in polar_plane.get_coordinate_labels():
            label.set_color(BLACK)
            label.scale(0.6) # Un poco más pequeñas para no encimarse

        # --- ETAPA 1: r = a ---
        title1 = Tex(r"1) $r = a$", color=BLACK).to_corner(UL)
        
        # Círculo base
        circle_a = ParametricFunction(
            lambda t: polar_plane.polar_to_point(1, t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        
        # Texto a la derecha
        desc1 = Tex(
            r"Radio constante,\\es un simple círculo", 
            color=BLACK, font_size=32
        ).next_to(polar_plane, RIGHT, buff=1).shift(UP * 2)

        self.play(Write(title1), Create(polar_plane))
        self.play(Create(circle_a), Write(desc1))
        self.wait(2)
        self.play(FadeOut(circle_a), FadeOut(desc1), FadeOut(title1))

        # --- ETAPA 2: r = cos(k * theta) ---
        title2 = Tex(r"2) $r = \cos(k \cdot \theta)$", color=BLACK).to_corner(UL)
        
        k_tracker = ValueTracker(3)
        def get_cos_curve():
            k = k_tracker.get_value()
            return ParametricFunction(
                lambda t: polar_plane.polar_to_point(np.cos(k * t), t),
                t_range=[0, 2*PI],
                color=COLOR_BLUE, stroke_width=4
            )
        cos_curve = always_redraw(get_cos_curve)
        
        # Textos explicativos (divididos para controlar márgenes)
        text2_1 = Tex(
            r"$\bullet$ Al meter el ángulo dentro de un\\coseno, el radio deja de ser\\constante y empieza a ``entrar y\\salir'' del centro.",
            color=BLACK, font_size=28
        ).next_to(polar_plane, RIGHT, buff=0.8).shift(UP * 2)
        
        text2_2 = Tex(
            r"$\bullet$ Si $k$ es entero: Determina el\\número de pétalos. Si $k$ es impar\\(como 7), la rosa tiene $k$ pétalos.\\Si es par, tiene $2k$.",
            color=BLACK, font_size=28
        ).next_to(text2_1, DOWN, buff=0.5, aligned_edge=LEFT)
        
        text2_3 = Tex(
            r"$\bullet$ El primer pétalo nace ``acostado''\\sobre el eje horizontal (Eje X).\\Esto es porque $\cos(0) = 1$\\(máxima extensión).",
            color=BLACK, font_size=28
        ).next_to(text2_2, DOWN, buff=0.5, aligned_edge=LEFT)

        self.play(Write(title2), Create(cos_curve))
        self.wait(1)
        self.play(Write(text2_1))
        
        # Animación de K con pausas en enteros
        for k_val in [4, 5, 6, 7]:
            self.play(k_tracker.animate.set_value(k_val), run_time=1.5)
            if k_val == 5:
                self.play(Write(text2_2))
            if k_val == 7:
                self.play(Write(text2_3))
            self.wait(1)

        self.wait(2)
        self.play(FadeOut(text2_1), FadeOut(text2_2), FadeOut(text2_3), FadeOut(title2))

        # --- ETAPA 3: r = sin(k * theta) ---
        # Iniciamos con el título del Coseno para mostrar la transformación
        title3_cos = Tex(r"3) $r = \cos(k \cdot \theta)$", color=BLACK).to_corner(UL)
        title3_sin = Tex(r"3) $r = \sin(k \cdot \theta)$", color=BLACK).to_corner(UL)
        
        # Curva actual (k=7)
        curve_3_cos = ParametricFunction(
            lambda t: polar_plane.polar_to_point(np.cos(7 * t), t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        curve_3_sin = ParametricFunction(
            lambda t: polar_plane.polar_to_point(np.sin(7 * t), t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        
        text3 = Tex(
            r"Primer pétalo nace ``girado''.\\Esto es porque $\sin(0)=0$.\\El brazo empieza en el centro y el\\primer pico del pétalo ocurre\\un poco después.",
            color=BLACK, font_size=28
        ).next_to(polar_plane, RIGHT, buff=0.8)

        self.play(Write(title3_cos), Transform(cos_curve, curve_3_cos))
        self.wait(1)
        
        # Transformación suave del Coseno al Seno
        self.play(
            Transform(title3_cos, title3_sin),
            Transform(cos_curve, curve_3_sin),
            run_time=2
        )
        self.wait(0.5)
        self.play(Write(text3))
        self.wait(4)

        # Limpieza final
        self.play(FadeOut(cos_curve), FadeOut(text3), FadeOut(title3_cos), FadeOut(polar_plane))
        self.wait(2)
