from manim import *
import numpy as np

config.background_color = "#FFFFFF"
TEXT_COLOR = "#333333"

COLOR_PINK = "#FF6699"
COLOR_ORANGE_DASH = "#FF8C00"
COLOR_BROWN = "#5C4033"
COLOR_ORANGE = "#FF4500"
COLOR_PURPLE = "#800080"
COLOR_RED = "#FF0000"
COLOR_BLACK = "#000000"

def txt(s, size=18, color=TEXT_COLOR, b=False):
    s_f = rf"\textbf{{{s}}}" if b else s
    return Tex(s_f, color=color, font_size=size)

class CinematicaInversaScene(Scene):
    def construct(self):
        # 1. TÍTULO
        title = Tex(r"\textbf{Cinemática Inversa: Robot 2R ADANISS (Codo arriba)}", color=TEXT_COLOR, font_size=40)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP, buff=0.4))
        
        # 2. PLANO CARTESIANO Y TRÉBOL
        axes = Axes(
            x_range=[-1, 6, 1], y_range=[-1, 6, 1],
            x_length=6.0, y_length=6.0,
            axis_config={"color": COLOR_BLACK, "stroke_width": 2, "include_numbers": False, "include_tip": True},
            x_axis_config={"include_ticks": True}, y_axis_config={"include_ticks": True}
        ).to_edge(LEFT, buff=0.5).shift(DOWN * 0.2)
        
        self.play(Create(axes), run_time=1.5)
        
        a, b, k, d = 1.0, 0.4, 3, PI/2
        escala = 1.0
        g, f = 3.0, 3.0
        
        flower_local = ParametricFunction(
            lambda t: axes.c2p(escala*(a+b*np.sin(k*t+k*d))*np.cos(t), escala*(a+b*np.sin(k*t+k*d))*np.sin(t)),
            t_range=[0, 2*PI], color="#1E88E5", stroke_width=4
        )
        self.play(Create(flower_local), run_time=2)
        
        # 3. TEXTOS 1
        t1_1 = txt(r"Recordemos que ya tenemos la ecuación para cada punto $P_i$ del", 18)
        t1_2 = txt(r"trébol en coordenadas polares locales ($\theta$):", 18)
        eq1 = MathTex(r"r(\theta) = \text{escala} \cdot (a + b \cdot \sin(k \cdot \theta + k \cdot d))", color=TEXT_COLOR, font_size=22)
        t1_3 = txt(r"Nuestro objetivo es llevar cada uno de estos puntos $(r, \theta)$ a la mesa de", 18)
        t1_4 = txt(r"trabajo del robot y calcular los ángulos de los motores $q_1$ y $q_2$ para", 18)
        t1_5 = txt(r"que la punta del brazo (marcador) toque ese punto.", 18)
        
        grp_text1 = VGroup(t1_1, t1_2, eq1, t1_3, t1_4, t1_5).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        grp_text1.to_edge(RIGHT, buff=0.5).shift(UP * 1.0)
        
        self.play(Write(grp_text1), run_time=3)
        self.wait(1)
        self.play(FadeOut(grp_text1))
        
        # 4. TEXTOS 2 (Offset)
        sec1_t = txt(r"1. Polares Locales $\rightarrow$ Cartesianas Locales:", 18, b=True)
        sec1_d = txt(r"Primero, convertimos el punto paramétrico polar a coordenadas $X, Y$ centradas en $(0,0)$:", 16)
        sec1_eq1 = MathTex(r"x_{local} = r(\theta) \cdot \cos(\theta)", color=TEXT_COLOR, font_size=20)
        sec1_eq2 = MathTex(r"y_{local} = r(\theta) \cdot \sin(\theta)", color=TEXT_COLOR, font_size=20)
        grp_sec1 = VGroup(sec1_t, sec1_d, sec1_eq1, sec1_eq2).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        grp_sec1.to_edge(RIGHT, buff=0.5).shift(UP * 1.5).align_to(grp_text1, LEFT)
        
        self.play(Write(grp_sec1), run_time=2.5)
        
        sec2_t = txt(r"2. Posicionamiento Global (Offset):", 18, b=True)
        sec2_d1 = txt(r"No queremos que el robot dibuje sobre su propio eje. Usamos los desfases $g$", 16)
        sec2_d2 = txt(r"(horizontal) y $f$ (vertical) para ubicar el trébol en una zona segura de la", 16)
        sec2_d3 = txt(r"mesa de trabajo. Las coordenadas finales $(X_{obj}, Y_{obj})$ que debe alcanzar el robot son:", 16)
        sec2_eq1 = MathTex(r"X_{obj} = x_{local} + g", color=TEXT_COLOR, font_size=20)
        sec2_eq2 = MathTex(r"Y_{obj} = y_{local} + f", color=TEXT_COLOR, font_size=20)
        grp_sec2 = VGroup(sec2_t, sec2_d1, sec2_d2, sec2_d3, sec2_eq1, sec2_eq2).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        grp_sec2.next_to(grp_sec1, DOWN, buff=0.3).align_to(grp_sec1, LEFT)
        
        self.play(Write(grp_sec2), run_time=3)
        
        flower_global = ParametricFunction(
            lambda t: axes.c2p(escala*(a+b*np.sin(k*t+k*d))*np.cos(t) + g, escala*(a+b*np.sin(k*t+k*d))*np.sin(t) + f),
            t_range=[0, 2*PI], color="#E53935", stroke_width=4
        )
        dot_g_f = Dot(axes.c2p(g, f), color=COLOR_BLACK)
        shift_arrow = Arrow(axes.c2p(0, 0), axes.c2p(g, f), color="#888888", buff=0, stroke_width=2)
        
        self.play(Transform(flower_local, flower_global), Create(dot_g_f), Create(shift_arrow), run_time=2)
        
        sec3_t = txt(r"3. Cartesianas Globales $\rightarrow$ Polares Globales:", 18, b=True)
        sec3_d1 = txt(r"Ahora, calculamos la distancia final $r_P$ desde el hombro del robot hasta", 16)
        sec3_d2 = txt(r"el punto y el ángulo global $\theta_P$:", 16)
        # sec3_eq1: r_P = sqrt(X^2 + Y^2)  -> r_P is index 0
        sec3_eq1 = MathTex(r"r_P", r" = \sqrt{X_{obj}^2 + Y_{obj}^2}", color=COLOR_BLACK, font_size=20)
        sec3_eq1[0].set_color(COLOR_ORANGE_DASH)
        # sec3_eq2: theta_P = atan2(...)  -> theta_P is index 0
        sec3_eq2 = MathTex(r"\theta_P", r" = \text{atan2}(Y_{obj}, X_{obj})", color=COLOR_BLACK, font_size=20)
        sec3_eq2[0].set_color(COLOR_PURPLE)
        grp_sec3 = VGroup(sec3_t, sec3_d1, sec3_d2, sec3_eq1, sec3_eq2).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        grp_sec3.next_to(grp_sec2, DOWN, buff=0.3).align_to(grp_sec1, LEFT)
        
        self.play(Write(grp_sec3))
        self.wait(1)
        
        self.play(FadeOut(shift_arrow), FadeOut(dot_g_f))
        
        # 5. ROBOT DINÁMICO
        curr_t = ValueTracker(PI/6)
        L1, L2 = 3.2, 3.2
        
        self.show_q1 = False
        self.show_q2 = False
        
        def get_static_robot(t_val, draw_q1, draw_q2):
            X = escala*(a+b*np.sin(k*t_val+k*d))*np.cos(t_val) + g
            Y = escala*(a+b*np.sin(k*t_val+k*d))*np.sin(t_val) + f
            
            r_P = np.clip(np.sqrt(X**2 + Y**2), 0.001, L1 + L2 - 0.001)
            theta_P = np.arctan2(Y, X)
            
            th1 = np.arccos(np.clip((L2**2 - L1**2 - r_P**2)/(-2*r_P*L1), -1.0, 1.0))
            th2 = np.arccos(np.clip((r_P**2 - L1**2 - L2**2)/(-2*L2*L1), -1.0, 1.0))
            th3 = np.arccos(np.clip((L1**2 - L2**2 - r_P**2)/(-2*r_P*L2), -1.0, 1.0))
            
            angle_L1 = theta_P + th1
            angle_L2 = theta_P - th3
            
            p0 = axes.c2p(0, 0)
            p1 = axes.c2p(L1*np.cos(angle_L1), L1*np.sin(angle_L1))
            p2 = axes.c2p(X, Y)
            
            grp = VGroup()
            
            grp.line_rp = DashedLine(p0, p2, color=COLOR_ORANGE_DASH, dash_length=0.15, dashed_ratio=0.5, stroke_width=4)
            grp.line_L1 = Line(p0, p1, color=COLOR_PINK, stroke_width=6)
            grp.line_L2 = Line(p1, p2, color=COLOR_PINK, stroke_width=6)
            grp.ext_L1 = DashedLine(p1, p1 + (p1-p0)*0.4, color="#AAAAAA", stroke_width=3)
            
            grp.dots = VGroup(Dot(p0, color=COLOR_BLACK, radius=0.08), Dot(p1, color=COLOR_BLACK, radius=0.08), Dot(p2, color=COLOR_RED, radius=0.15))
            
            grp.arc_thP = Arc(1.0, 0, theta_P, color=COLOR_PURPLE, stroke_width=3, arc_center=p0)
            grp.lbl_thP = MathTex(r"\theta_P", color=COLOR_PURPLE, font_size=20).move_to(p0 + 1.25*np.array([np.cos(theta_P/2), np.sin(theta_P/2), 0]))
            
            grp.arc_th1 = Arc(1.5, theta_P, th1, color=COLOR_BROWN, stroke_width=3, arc_center=p0)
            grp.lbl_th1 = MathTex(r"\theta_1", color=COLOR_BROWN, font_size=20).move_to(p0 + 1.75*np.array([np.cos(theta_P+th1/2), np.sin(theta_P+th1/2), 0]))
            
            st_th2 = angle_L1 - PI
            grp.arc_th2 = Arc(0.7, st_th2, th2, color=COLOR_BROWN, stroke_width=3, arc_center=p1)
            grp.lbl_th2 = MathTex(r"\theta_2", color=COLOR_BROWN, font_size=20).move_to(p1 + 0.9*np.array([np.cos(st_th2+th2/2), np.sin(st_th2+th2/2), 0]))
            
            grp.arc_th3 = Arc(0.7, angle_L2+PI, th3, color=COLOR_BROWN, stroke_width=3, arc_center=p2)
            grp.lbl_th3 = MathTex(r"\theta_3", color=COLOR_BROWN, font_size=20).move_to(p2 + 0.9*np.array([np.cos(angle_L2+PI+th3/2), np.sin(angle_L2+PI+th3/2), 0]))
            
            grp.lbl_L1 = MathTex(r"L_1", color=COLOR_PINK, font_size=26).move_to((p0+p1)/2 + 0.3*np.array([-np.sin(angle_L1), np.cos(angle_L1), 0]))
            grp.lbl_L2 = MathTex(r"L_2", color=COLOR_PINK, font_size=26).move_to((p1+p2)/2 + 0.3*np.array([-np.sin(angle_L2), np.cos(angle_L2), 0]))
            grp.lbl_rp = MathTex(r"r_P", color=COLOR_ORANGE_DASH, font_size=26).move_to((p0+p2)/2 + 0.3*np.array([np.sin(theta_P), -np.cos(theta_P), 0]))
            
            grp.add(grp.line_rp, grp.line_L1, grp.line_L2, grp.ext_L1, grp.dots,
                    grp.arc_thP, grp.lbl_thP, grp.arc_th1, grp.lbl_th1,
                    grp.arc_th2, grp.lbl_th2, grp.arc_th3, grp.lbl_th3,
                    grp.lbl_L1, grp.lbl_L2, grp.lbl_rp)
            
            # Componentes q1 y q2 condicionales
            grp.arc_q1 = Arc(1.3, 0, angle_L1, color=COLOR_ORANGE, stroke_width=4, arc_center=p0)
            grp.lbl_q1 = MathTex(r"q_1", color=COLOR_ORANGE, font_size=20).move_to(p0 + 1.55*np.array([np.cos(angle_L1/2), np.sin(angle_L1/2), 0]))
            if not draw_q1:
                grp.arc_q1.set_opacity(0)
                grp.lbl_q1.set_opacity(0)
            grp.add(grp.arc_q1, grp.lbl_q1)
            
            grp.arc_q2 = Arc(0.9, angle_L2, angle_L1 - angle_L2, color=COLOR_ORANGE, stroke_width=4, arc_center=p1)
            grp.lbl_q2 = MathTex(r"q_2", color=COLOR_ORANGE, font_size=20).move_to(p1 + 1.15*np.array([np.cos((angle_L1+angle_L2)/2), np.sin((angle_L1+angle_L2)/2), 0]))
            if not draw_q2:
                grp.arc_q2.set_opacity(0)
                grp.lbl_q2.set_opacity(0)
            grp.add(grp.arc_q2, grp.lbl_q2)
                
            return grp

        # Dynamic Updater
        robot_group = VGroup()
        robot_group.add(get_static_robot(curr_t.get_value(), self.show_q1, self.show_q2))
        
        def update_robot(mob):
            new_r = get_static_robot(curr_t.get_value(), self.show_q1, self.show_q2)
            mob.become(new_r)
        
        self.play(FadeIn(robot_group), run_time=1.5)
        # We add the updater safely AFTER the FadeIn transformation to strictly avoid zip array manipulation during animations
        robot_group.add_updater(update_robot)
        
        # PARTE 1 DEL RECORRIDO (mitad)
        self.play(curr_t.animate.set_value(PI/6 + PI/4), run_time=3, rate_func=smooth)
        self.wait(1)
        
        self.play(FadeOut(grp_sec1), FadeOut(grp_sec2), FadeOut(grp_sec3))
        
        # Parar dinámico para indicar
        robot_group.clear_updaters()
        sr = get_static_robot(curr_t.get_value(), self.show_q1, self.show_q2)
        self.remove(robot_group)
        self.add(sr)
        
        # 6. TEXTOS IMAGEN 3 (LEY DE COSENOS) & HIGHLIGHTS
        t3_intro = Tex(r"Una vez que conocemos ", r"$r_P$", r" y ", r"$\theta_P$", r", el problema se", color=TEXT_COLOR, font_size=16)
        t3_intro[1].set_color(COLOR_ORANGE_DASH)
        t3_intro[3].set_color(COLOR_PURPLE)
        
        t3_intro2 = Tex(r"reduce a resolver un triángulo formado por el \textbf{Hombro (Base)},", color=TEXT_COLOR, font_size=16)
        t3_intro3 = Tex(r"el \textbf{Codo} y la \textbf{Punta}. Los lados de este triángulo son", color=TEXT_COLOR, font_size=16)
        
        t3_intro4 = Tex(r"$L_1$", r", ", r"$L_2$", r" y la distancia total ", r"$r_P$", r". Usamos la \textbf{Ley de Cosenos}", color=TEXT_COLOR, font_size=16)
        t3_intro4[0].set_color(COLOR_PINK)
        t3_intro4[2].set_color(COLOR_PINK)
        t3_intro4[4].set_color(COLOR_ORANGE_DASH)
        
        t3_intro5 = Tex(r"para hallar los ángulos internos $\mathbf{\theta_1}$ y $\mathbf{\theta_2}$:", color=TEXT_COLOR, font_size=16)
        
        t3_s1 = Tex(r"\textbf{1. Cálculo del Ángulo Interno del Hombro }(", r"$\mathbf{\theta_1}$", r"):", color=TEXT_COLOR, font_size=16)
        t3_s1[1].set_color(COLOR_BROWN)
        t3_s1_d = Tex(r"El ángulo entre el primer brazo (", r"$L_1$", r") y la línea imaginaria ", r"$r_P$", r":", color=TEXT_COLOR, font_size=14)
        t3_s1_d[1].set_color(COLOR_PINK)
        t3_s1_d[3].set_color(COLOR_ORANGE_DASH)
        
        # Split formula chunks — index coloring is robust against superscripts
        # t3_eq1 chunks: [0]\cos( [1]\theta_1 [2])=\frac{ [3]L_2^2 [4]- [5]L_1^2 [6]- [7]r_P^2 [8]}{-2\cdot [9]r_P [10]\cdot [11]L_1 [12]}
        t3_eq1 = MathTex(r"\cos(", r"\theta_1", r") = \frac{", r"L_2^2", r" - ", r"L_1^2", r" - ", r"r_P^2", r"}{-2 \cdot ", r"r_P", r" \cdot ", r"L_1", r"}", color=COLOR_BLACK, font_size=22)
        t3_eq1[1].set_color(COLOR_BROWN)   # \theta_1
        t3_eq1[3].set_color(COLOR_PINK)    # L_2^2
        t3_eq1[5].set_color(COLOR_PINK)    # L_1^2
        t3_eq1[7].set_color(COLOR_ORANGE_DASH)  # r_P^2
        t3_eq1[9].set_color(COLOR_ORANGE_DASH)  # r_P (denominator)
        t3_eq1[11].set_color(COLOR_PINK)   # L_1 (denominator)
        
        t3_s2 = Tex(r"\textbf{2. Cálculo del Ángulo Interno del Codo }(", r"$\mathbf{\theta_2}$", r"):", color=TEXT_COLOR, font_size=16)
        t3_s2[1].set_color(COLOR_BROWN)
        t3_s2_d = Tex(r"El ángulo entre los dos eslabones (", r"$L_1$", r" y ", r"$L_2$", r"):", color=TEXT_COLOR, font_size=14)
        t3_s2_d[1].set_color(COLOR_PINK)
        t3_s2_d[3].set_color(COLOR_PINK)
        
        # t3_eq2 chunks: [0]\cos( [1]\theta_2 [2])=\frac{ [3]r_P^2 [4]- [5]L_1^2 [6]- [7]L_2^2 [8]}{-2\cdot [9]L_1 [10]\cdot [11]L_2 [12]}
        t3_eq2 = MathTex(r"\cos(", r"\theta_2", r") = \frac{", r"r_P^2", r" - ", r"L_1^2", r" - ", r"L_2^2", r"}{-2 \cdot ", r"L_1", r" \cdot ", r"L_2", r"}", color=COLOR_BLACK, font_size=22)
        t3_eq2[1].set_color(COLOR_BROWN)   # \theta_2
        t3_eq2[3].set_color(COLOR_ORANGE_DASH)  # r_P^2
        t3_eq2[5].set_color(COLOR_PINK)    # L_1^2
        t3_eq2[7].set_color(COLOR_PINK)    # L_2^2
        t3_eq2[9].set_color(COLOR_PINK)    # L_1 (denominator)
        t3_eq2[11].set_color(COLOR_PINK)   # L_2 (denominator)
        
        grp_im3 = VGroup(t3_intro, t3_intro2, t3_intro3, t3_intro4, t3_intro5, 
                         t3_s1, t3_s1_d, t3_eq1, 
                         t3_s2, t3_s2_d, t3_eq2).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        grp_im3.to_edge(RIGHT, buff=1.4).shift(UP*1.0)
        
        self.play(FadeIn(grp_im3))
        
        # Highlight theta 1 y 2 en grafo y texto
        self.play(
            Indicate(sr.arc_th1, color=COLOR_BROWN, scale_factor=1.2), Indicate(sr.lbl_th1, color=COLOR_BROWN, scale_factor=1.5),
            Circumscribe(t3_s1, color=COLOR_BROWN, time_width=1.5), 
            Circumscribe(t3_eq1, color=COLOR_BROWN, time_width=1.5),
            run_time=1.5
        )
        self.play(
            Indicate(sr.arc_th2, color=COLOR_BROWN, scale_factor=1.2), Indicate(sr.lbl_th2, color=COLOR_BROWN, scale_factor=1.5),
            Circumscribe(t3_s2, color=COLOR_BROWN, time_width=1.5), 
            Circumscribe(t3_eq2, color=COLOR_BROWN, time_width=1.5),
            run_time=1.5
        )
        self.wait(1)
        
        # 7. TEXTOS IMAGEN 4 (CINEMÁTICA MOTORES) & HIGHLIGHTS
        self.play(FadeOut(grp_im3))
        
        # Construct q1 geometry for static frame manually
        t_val = curr_t.get_value()
        X = escala*(a+b*np.sin(k*t_val+k*d))*np.cos(t_val) + g
        Y = escala*(a+b*np.sin(k*t_val+k*d))*np.sin(t_val) + f
        theta_P = np.arctan2(Y, X)
        r_P = np.clip(np.sqrt(X**2 + Y**2), 0.001, L1 + L2 - 0.001)
        th1 = np.arccos(np.clip((L2**2 - L1**2 - r_P**2)/(-2*r_P*L1), -1.0, 1.0))
        th3 = np.arccos(np.clip((L1**2 - L2**2 - r_P**2)/(-2*r_P*L2), -1.0, 1.0))
        angle_L1 = theta_P + th1
        angle_L2 = theta_P - th3
        p0 = axes.c2p(0, 0)
        p1 = axes.c2p(L1*np.cos(angle_L1), L1*np.sin(angle_L1))
        
        arc_q1 = Arc(1.3, 0, angle_L1, color=COLOR_ORANGE, stroke_width=4, arc_center=p0)
        lbl_q1 = MathTex(r"q_1", color=COLOR_ORANGE, font_size=20).move_to(p0 + 1.55*np.array([np.cos(angle_L1/2), np.sin(angle_L1/2), 0]))
        
        # Update show_q1 for Motor Hombro state flag
        self.show_q1 = True
        
        t4_s1 = Tex(r"\textbf{1. Motor del Hombro }(", r"$\mathbf{q_1}$", r"):", color=TEXT_COLOR, font_size=16)
        t4_s1[1].set_color(COLOR_ORANGE)
        t4_s1_d = Tex(r"El ángulo total que debe girar la base es la suma del ángulo", color=TEXT_COLOR, font_size=14)
        t4_s1_d2 = Tex(r"global hacia el punto (", r"$\theta_P$", r") más el ángulo interno del triángulo (", r"$\theta_1$", r"):", color=TEXT_COLOR, font_size=14)
        t4_s1_d2[1].set_color(COLOR_PURPLE)
        t4_s1_d2[3].set_color(COLOR_BROWN)
        
        t4_eq1 = MathTex(r"q_1", r" = ", r"\theta_P", r" + ", r"\theta_1", color=COLOR_BLACK, font_size=22)
        t4_eq1.set_color_by_tex(r"q_1", COLOR_ORANGE)
        t4_eq1.set_color_by_tex(r"\theta_P", COLOR_PURPLE)
        t4_eq1.set_color_by_tex(r"\theta_1", COLOR_BROWN)
        
        grp_im4_p1 = VGroup(t4_s1, t4_s1_d, t4_s1_d2, t4_eq1).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        grp_im4_p1.to_edge(RIGHT, buff=1.4).shift(UP*1.5)
        
        self.play(FadeIn(grp_im4_p1), Create(arc_q1), FadeIn(lbl_q1), run_time=2)
        
        # Construct q2 geometry statically
        arc_q2 = Arc(0.9, angle_L2, angle_L1 - angle_L2, color=COLOR_ORANGE, stroke_width=4, arc_center=p1)
        lbl_q2 = MathTex(r"q_2", color=COLOR_ORANGE, font_size=20).move_to(p1 + 1.15*np.array([np.cos((angle_L1+angle_L2)/2), np.sin((angle_L1+angle_L2)/2), 0]))
        self.show_q2 = True
        
        t4_s2 = Tex(r"\textbf{2. Motor del Codo }(", r"$\mathbf{q_2}$", r"):", color=TEXT_COLOR, font_size=16)
        t4_s2[1].set_color(COLOR_ORANGE)
        t4_s2_msg_a = Tex(r"\textbf{¡CORRECCIÓN IMPORTANTE!} Para la configuración", color=TEXT_COLOR, font_size=14)
        t4_s2_msg_b = Tex(r"de Codo Arriba (Bano), el ángulo $q_2$ debe ser \textbf{negativo},", color=TEXT_COLOR, font_size=14)
        t4_s2_msg3 = Tex(r"ya que es externo suplementario medido hacia ``arriba\":", color=TEXT_COLOR, font_size=14)
        
        t4_eq2 = MathTex(r"q_2", r" = -(\pi \text{ Rad} - ", r"\theta_2", r")", color=COLOR_BLACK, font_size=22)
        t4_eq2.set_color_by_tex(r"q_2", COLOR_ORANGE)
        t4_eq2.set_color_by_tex(r"\theta_2", COLOR_BROWN)
        
        grp_im4_p2 = VGroup(t4_s2, t4_s2_msg_a, t4_s2_msg_b, t4_s2_msg3, t4_eq2).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        grp_im4_p2.next_to(grp_im4_p1, DOWN, buff=0.4).align_to(grp_im4_p1, LEFT)
        
        self.play(FadeIn(grp_im4_p2), Create(arc_q2), FadeIn(lbl_q2), run_time=2)
        
        # Highlight both Q1 and Q2
        self.play(
            Indicate(arc_q1, color=COLOR_ORANGE, scale_factor=1.2), Indicate(lbl_q1, color=COLOR_ORANGE, scale_factor=1.5),
            Circumscribe(t4_s1, color=COLOR_ORANGE, time_width=1.5), 
            Circumscribe(t4_eq1, color=COLOR_ORANGE, time_width=1.5),
            run_time=1.5
        )
        self.play(
            Indicate(arc_q2, color=COLOR_ORANGE, scale_factor=1.2), Indicate(lbl_q2, color=COLOR_ORANGE, scale_factor=1.5),
            Circumscribe(t4_s2, color=COLOR_ORANGE, time_width=1.5), 
            Circumscribe(t4_eq2, color=COLOR_ORANGE, time_width=1.5),
            run_time=1.5
        )
        self.wait(1)
        
        # 8. Verificacion alcance
        veri_t1 = Tex(r"\textbf{Verificación de alcance}", color=COLOR_RED, font_size=16)
        veri_eq = MathTex(r"r_P", r" \leq ", r"L_1", r" + ", r"L_2", color=COLOR_BLACK, font_size=20)
        veri_eq.set_color_by_tex(r"r_P", COLOR_ORANGE_DASH)
        veri_eq.set_color_by_tex(r"L_1", COLOR_PINK)
        veri_eq.set_color_by_tex(r"L_2", COLOR_PINK)
        
        grp_veri = VGroup(veri_t1, veri_eq).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        grp_veri.next_to(grp_im4_p2, DOWN, buff=0.4).align_to(grp_im4_p1, LEFT)
        
        self.play(FadeIn(grp_veri))
        self.wait(1)
        
        # Re-activar dinámica y completar recorrido de ida
        self.remove(sr, arc_q1, lbl_q1, arc_q2, lbl_q2)
        
        dynamic_robot = always_redraw(lambda: get_static_robot(curr_t.get_value(), self.show_q1, self.show_q2))
        self.add(dynamic_robot)
        
        self.play(curr_t.animate.set_value(PI/6 + 2*PI), run_time=5, rate_func=linear)
        self.wait(2)
