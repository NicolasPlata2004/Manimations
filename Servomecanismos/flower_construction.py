from manim import *
import numpy as np

# Paleta de colores basada en Imagen 1
COLOR_RED = "#E84A4A"
COLOR_BLUE = "#517696"
COLOR_YELLOW = "#D99B16"
COLOR_PINK = "#E06C75"
COLOR_GRID = "#E0E0E0"

config.background_color = WHITE

class ConstructionScene(Scene):
    def construct(self):
        # --- CONFIGURACIÓN DE PANTALLA ---
        # Cuadrícula tipo cuaderno
        grid = NumberPlane(
            x_range=[-10, 10, 1],
            y_range=[-10, 10, 1],
            background_line_style={
                "stroke_color": COLOR_GRID,
                "stroke_width": 1,
                "stroke_opacity": 0.5
            }
        )
        self.add(grid)

        # Plano polar (más pequeño y a la izquierda)
        polar_plane = PolarPlane(
            radius_max=2,
            size=5,
            radius_config={"font_size": 14, "color": BLACK},
            background_line_style={"stroke_color": GREY_B, "stroke_opacity": 0.2},
            azimuth_units="PI radians",
        ).add_coordinates().shift(LEFT * 3).scale(0.8)
        
        # Asegurar que las etiquetas sean negras para el fondo blanco
        for label in polar_plane.get_coordinate_labels():
            label.set_color(BLACK)

        # --- ETAPA 1: r = a (Imagen 2) ---
        title1 = MathTex(r"1) r = a", color=BLACK).to_corner(UL).scale(1.2)
        circle_a = ParametricFunction(
            lambda t: polar_plane.polar_to_point(1, t),
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        desc1 = Text("Radio constante, es un simple círculo", color=BLACK, font_size=24).next_to(polar_plane, RIGHT, buff=1)

        self.play(Write(title1))
        self.play(Create(polar_plane))
        self.play(Create(circle_a), Write(desc1))
        self.wait(2)

        # Limpiar etapa 1
        self.play(FadeOut(circle_a), FadeOut(desc1), FadeOut(title1))

        # --- ETAPA 2: r = cos(k * theta) (Imagen 3) ---
        title2 = MathTex(r"2) r = \cos(k \cdot \theta)", color=BLACK).to_corner(UL).scale(1.2)
        
        # Tracker para K
        k_tracker = ValueTracker(3)
        
        # Curva dinámica
        def get_cos_curve():
            k = k_tracker.get_value()
            return ParametricFunction(
                lambda t: polar_plane.polar_to_point(np.cos(k * t), t),
                t_range=[0, 2*PI],
                color=COLOR_BLUE, stroke_width=4
            )
        
        cos_curve = always_redraw(get_cos_curve)
        
        # Textos de la etapa 2
        text2_1 = Text(
            "Al meter el ángulo dentro de un coseno, el radio deja de\nser constante y empieza a 'entrar y salir' del centro.",
            color=BLACK, font_size=20, line_spacing=0.8
        ).next_to(polar_plane, RIGHT, buff=0.8).shift(UP * 2)
        
        text2_2 = Text(
            "⚠ Si k es entero: Determina el número de pétalos,\nsi k es impar (como 7), la rosa tiene k pétalos.\nSi es par, tiene 2k.",
            color=BLACK, font_size=20, line_spacing=0.8
        ).next_to(text2_1, DOWN, buff=0.5, aligned_edge=LEFT)
        
        text2_3 = Text(
            "? El primer pétalo nace 'acostado' sobre el eje\nhorizontal (Eje X). Esto es porque cos(0) = 1\n(máxima extensión).",
            color=BLACK, font_size=20, line_spacing=0.8
        ).next_to(text2_2, DOWN, buff=0.5, aligned_edge=LEFT)

        self.play(Write(title2))
        self.play(Create(cos_curve))
        
        # Animar k de 3 a 7 MIENTRAS aparecen los textos
        self.play(
            k_tracker.animate.set_value(7),
            Write(text2_1),
            run_time=3
        )
        self.play(Write(text2_2), run_time=2)
        self.play(Write(text2_3), run_time=2)
        self.wait(2)

        # Limpiar etapa 2
        self.play(FadeOut(cos_curve), FadeOut(text2_1), FadeOut(text2_2), FadeOut(text2_3), FadeOut(title2))

        # --- ETAPA 3: r = sin(k * theta) (Imagen 4) ---
        title3 = MathTex(r"3) r = \sin(k \cdot \theta)", color=BLACK).to_corner(UL).scale(1.2)
        
        sin_curve = ParametricFunction(
            lambda t: polar_plane.polar_to_point(np.sin(3 * t), t), # k=3 por defecto
            t_range=[0, 2*PI],
            color=COLOR_BLUE, stroke_width=4
        )
        
        text3 = Text(
            "Primer pétalo nace 'girado'. Esto es porque sin(0)=0.\nEl brazo empieza en el centro y el primer pico\ndel pétalo ocurre un poco después.",
            color=BLACK, font_size=20, line_spacing=0.8
        ).next_to(polar_plane, RIGHT, buff=0.8)

        self.play(Write(title3))
        self.play(Create(sin_curve))
        self.play(Write(text3))
        self.wait(3)

        # Final
        self.play(FadeOut(sin_curve), FadeOut(text3), FadeOut(title3), FadeOut(polar_plane))
        self.wait(1)
