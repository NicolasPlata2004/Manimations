from manim import *
import numpy as np

config.background_color = "#FFFFFF"
TEXT_COLOR = "#333333"
VISUAL_SCALE = 10.0

# ----------------------------------------------------
# 1. MATLAB LOGIC TRANSLATION
# ----------------------------------------------------
def ley_cos(r, L1, L2):
    # MATLAB: Th1 = acos((L2^2-L1^2-r^2)/(-2*r*L1))
    val1 = np.clip((L2**2 - L1**2 - r**2) / (-2 * r * L1), -1.0, 1.0)
    th1 = np.arccos(val1)
    
    val2 = np.clip((r**2 - L1**2 - L2**2) / (-2 * L2 * L1), -1.0, 1.0)
    th2 = np.arccos(val2)
    
    val3 = np.clip((L1**2 - L2**2 - r**2) / (-2 * r * L2), -1.0, 1.0)
    th3 = np.arccos(val3)
    
    return th1, th2, th3

def MCG(alpha, beta, dalpha, dbeta, m1, m2, L1, lc2, lc1, Iz1, Iz2, gr):
    c1 = np.cos(alpha)
    c2 = np.cos(beta)
    s2 = np.sin(beta)
    c12 = np.cos(alpha + beta)

    E = 2 * m2 * L1 * lc2 * s2
    D = E
    N = -m2 * L1 * lc2 * s2

    M = np.array([
        [m1*lc1**2 + Iz1 + m2*L1**2 + m2*lc2**2 + Iz2 + 2*m2*L1*lc2*c2, m2*lc2**2 + Iz2 + m2*L1*lc2*c2],
        [m2*lc2**2 + m2*L1*lc2*c2 + Iz2, m2*lc2**2 + Iz2]
    ])
    
    C = np.array([
        D * dalpha * dbeta + E * dbeta**2,
        N * dalpha * dbeta - (-m2 * L1 * lc2 * s2 * dalpha * (dalpha + dbeta))
    ])
    
    G_vec = gr * np.array([
        (m1*lc1 + m2*L1)*c1 + m2*lc2*c12,
        m2*lc2*c12
    ])
    
    return M, C, G_vec

class SimulationData:
    def __init__(self):
        a = 0.1022; b = a / 4; f = 0.3; g = 0.3
        self.c = 7
        L1 = 0.3; L2 = 0.3
        t_total = 1000; escala = 1.25; angulo = 0
        m1 = 0.1; m2 = 0.1
        ancho = 0.03; alto = 0.01
        
        lc1 = L1 / 2; lc2 = L2 / 2
        Iz1 = (1 / 12) * m1 * (ancho**2 + alto**2)
        Iz2 = (1 / 12) * m2 * (ancho**2 + alto**2)
        gr = 9.8
        
        tin = 3; tcal = 4
        d_val = -np.pi / 2 if self.c % 2 == 0 else 0
        
        uint = np.linspace(0, 1, 2000)
        sint = 10 * uint**3 - 15 * uint**4 + 6 * uint**5
        inter = 2 * np.pi * sint
        
        Alpha_trebol = np.zeros(len(inter))
        Th2_trebol = np.zeros(len(inter))
        rP_trebol = np.zeros(len(inter))
        
        for k, i in enumerate(inter):
            r = escala * (a + b * np.sin(self.c * i + (d_val + self.c * np.deg2rad(angulo))))
            rP = np.sqrt((r * np.cos(i) + g)**2 + (r * np.sin(i) + f)**2)
            ThetaP = np.arctan2(r * np.sin(i) + f, r * np.cos(i) + g)
            
            th1, th2, th3 = ley_cos(rP, L1, L2)
            alpha = th1 + ThetaP
            
            Alpha_trebol[k] = alpha
            Th2_trebol[k] = th2
            rP_trebol[k] = rP
            
        tstop = 1
        # Calculate exactly as MATLAB
        Nstop = int(np.round(len(Alpha_trebol) * tstop / t_total))
        if Nstop < 1: Nstop = 1
        
        AlphaStop = np.ones(Nstop) * Alpha_trebol[0]
        Th2Stop = np.ones(Nstop) * Th2_trebol[0]
        
        Alphaf = np.concatenate((AlphaStop, Alpha_trebol))
        Th2f = np.concatenate((Th2Stop, Th2_trebol))
        
        # Trajectory from initial
        u_len = int(np.round(len(Alpha_trebol) * tin / t_total))
        if u_len < 2: u_len = 10
        u = np.linspace(0, 1, u_len)
        s = 10 * u**3 - 15 * u**4 + 6 * u**5
        Alphain = np.pi / 2 + (Alpha_trebol[0] - np.pi / 2) * s
        Th2in = np.pi / 6 + (Th2_trebol[0] - np.pi / 6) * s
        
        AlphaStop2 = np.ones(Nstop) * Alphain[0]
        Th2Stop2 = np.ones(Nstop) * Th2in[0]
        
        Alphaf = np.concatenate((AlphaStop2, Alphain, Alphaf))
        Th2f = np.concatenate((Th2Stop2, Th2in, Th2f))
        
        # Trajectory from calibracion
        ucal_len = int(np.round(len(Alpha_trebol) * tcal / t_total))
        if ucal_len < 2: ucal_len = 10
        ucal = np.linspace(0, 1, ucal_len)
        scal = 10 * ucal**3 - 15 * ucal**4 + 6 * ucal**5
        Alphacal = 0 + (np.pi / 2 - 0) * scal
        Th2cal = np.pi + (np.pi / 6 - np.pi) * scal
        
        self.Alphaf = np.concatenate((Alphacal, Alphaf))
        self.Th2f = np.concatenate((Th2cal, Th2f))
        
        self.tiempo = np.linspace(0, t_total + tcal + tin + 2 * tstop, len(self.Alphaf))
        
        DAlphaf = np.gradient(self.Alphaf, self.tiempo)
        D2Alphaf = np.gradient(DAlphaf, self.tiempo)
        DTh2f = np.gradient(self.Th2f, self.tiempo)
        D2Th2f = np.gradient(DTh2f, self.tiempo)
        
        self.Torques = np.zeros((2, len(self.Alphaf)))
        for k in range(len(self.Alphaf)):
            alpha_val = self.Alphaf[k]
            beta_val = np.pi - self.Th2f[k]
            dalpha_val = DAlphaf[k]
            dbeta_val = -DTh2f[k]
            d2alpha_val = D2Alphaf[k]
            d2beta_val = -D2Th2f[k]
            
            M_mat, C_mat, G_mat = MCG(alpha_val, beta_val, dalpha_val, dbeta_val, m1, m2, L1, lc2, lc1, Iz1, Iz2, gr)
            accel = np.array([d2alpha_val, d2beta_val])
            self.Torques[:, k] = np.dot(M_mat, accel) + C_mat + G_mat

        self.T1_max = np.max(np.abs(self.Torques[0, :]))
        self.T2_max = np.max(np.abs(self.Torques[1, :]))
        
        self.Alpha_trebol = Alpha_trebol
        self.Th2_trebol = Th2_trebol

sim_data = SimulationData()

# ----------------------------------------------------
# 2. MANIM HELPERS
# ----------------------------------------------------
def get_robot_arm(alpha, th2, origin=ORIGIN):
    # Alpha = Humero a Base, Th2 = Intero
    # Relativo (beta) del segundo eslabon: beta = pi - th2
    # Ángulo absoluto segundo eslabon: alpha + beta = alpha + pi - th2 = abs_th2
    # Pero segun MATLAB, las coordenadas trazadas en for loop son:
    # x2 = x1 + L2*sin(Th2-(pi/2-Alpha)), y2 = y1 - L2*cos(Th2-(pi/2-Alpha))
    # Para simplificar: Th2 es el ángulo interno del triángulo.
    # El vector P tiene angulo ThetaP.
    # Alpha = th1 + ThetaP
    # La posicion 2 es un vector de magnitud L2 a un ángulo particular.
    # Matemáticamente en MATLAB (su plot directo):
    # angulo_absoluto_L2 = alpha - pi + th2
    
    L1, L2 = 0.3 * VISUAL_SCALE, 0.3 * VISUAL_SCALE
    p0 = origin
    p1 = p0 + np.array([L1 * np.cos(alpha), L1 * np.sin(alpha), 0])
    
    abs_th2 = alpha + (np.pi - th2) # (beta = pi - th2, así que alpha + beta)
    # Sin embargo MATLAB dibuja:
    # x2 = x1 + L2*str... 
    # Validemos la matemática: si el codo dobla hacia adentro (positiva rotacion de beta)
    p2 = p1 + np.array([L2 * np.cos(abs_th2), L2 * np.sin(abs_th2), 0])
    
    link1 = Line(p0, p1, color="#1E88E5", stroke_width=20)
    link2 = Line(p1, p2, color="#E53935", stroke_width=20)
    
    joint0 = Dot(p0, color=TEXT_COLOR, radius=0.2).set_z_index(1)
    joint1 = Dot(p1, color=TEXT_COLOR, radius=0.2).set_z_index(1)
    joint2 = Dot(p2, color=TEXT_COLOR, radius=0.15).set_z_index(1)
    
    return VGroup(link1, link2, joint0, joint1, joint2), p2

# ----------------------------------------------------
# 3. SCENES (Basadas en especificaciones MATLAB)
# ----------------------------------------------------

class Escena1_Introduccion(Scene):
    def construct(self):
        title = Tex(r"\textbf{Avances del Proyecto Académico}", color=TEXT_COLOR, font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP, buff=1))
        
        nombres = [
            "1. Alessandra Quintero Rois",
            "2. Daniel Alejandro Torres Sanabria",
            "3. Nicolas Plata Molano",
            "4. Samuel David Negrete Lancheros",
            "5. Samuel Correales"
        ]
        
        integrantes_group = VGroup(*[Text(name, color=TEXT_COLOR, font_size=28) for name in nombres])
        integrantes_group.arrange(DOWN, aligned_edge=LEFT).next_to(title, DOWN, buff=1.0).to_edge(LEFT, buff=1.5)
        
        self.play(Write(integrantes_group), run_time=4)
        self.wait(1)
        
        logo = Circle(radius=1.5, color="#1E88E5", fill_opacity=0.1, stroke_width=6)
        logo_inner = Circle(radius=1.2, color="#E53935", fill_opacity=0.1, stroke_width=4)
        logo_text = Text("UNAL", color=TEXT_COLOR, font_size=36, weight=BOLD).move_to(logo.get_center())
        logo_group = VGroup(logo, logo_inner, logo_text).to_edge(RIGHT, buff=2)
        
        self.play(FadeIn(logo_group, shift=LEFT))
        self.wait(2)
        
        self.play(FadeOut(VGroup(title, integrantes_group, logo_group)))

class Escena2_Cinematica(Scene):
    def construct(self):
        origin = np.array([-3, -1, 0])
        
        robot_group = VGroup()
        t_index = ValueTracker(0.0)
        
        length_trebol = len(sim_data.Alpha_trebol)
        
        def update_robot(mob):
            idx = int(t_index.get_value())
            if idx >= length_trebol: idx = length_trebol - 1
            alpha = sim_data.Alpha_trebol[idx]
            th2 = sim_data.Th2_trebol[idx]

            new_rob, p2 = get_robot_arm(alpha, th2, origin=origin)
            mob.become(new_rob)
            
        robot_group.add_updater(update_robot)
        
        eq_text = MathTex(r"""
        \begin{aligned}
        &r_P^2 = (r\cos i + g)^2 + (r\sin i + f)^2 \\
        &\theta_{int} = \arccos\left(\frac{r_P^2 - L_1^2 - L_2^2}{-2L_1L_2}\right) \\
        &\theta_2 = \theta_{int} \quad \text{(Matlab)} \\
        &\alpha = \theta_1 + \theta_P
        \end{aligned}
        """, color=TEXT_COLOR, font_size=28).to_corner(UL)
        
        vel_text = MathTex(r"\mathbf{v = \text{Variable (10 cm/s en prom.)}}", color=TEXT_COLOR, font_size=28).to_corner(UR)
        
        self.add(robot_group)
        self.play(FadeIn(eq_text), FadeIn(vel_text))
        
        # Generar path traceado precalculando los puntos de P2
        # (Para ser fieles al MATLAB que usa el for_loop y line drawnow)
        path = TracedPath(lambda: get_robot_arm(sim_data.Alpha_trebol[int(np.clip(t_index.get_value(), 0, length_trebol-1))], sim_data.Th2_trebol[int(np.clip(t_index.get_value(), 0, length_trebol-1))], origin)[1], stroke_color="#2ECC71", stroke_width=5)
        self.add(path)
        
        self.play(t_index.animate.set_value(length_trebol - 1), run_time=8, rate_func=linear)
        self.wait(2)
        self.play(FadeOut(VGroup(robot_group, path, eq_text, vel_text)))

class Escena3_Dinamica(Scene):
    def construct(self):
        eq1 = MathTex(r"\tau = M(q)\ddot{q} + C(q,\dot{q}) + G(q)", color=TEXT_COLOR).to_edge(UP)
        
        eq2 = MathTex(r"C = \begin{bmatrix} D\dot{\alpha}\dot{\beta} + E\dot{\beta}^2 \\ N\dot{\alpha}\dot{\beta} + m_2 L_1 lc_2 \sin(\beta)\dot{\alpha}(\dot{\alpha}+\dot{\beta}) \end{bmatrix}", color=TEXT_COLOR)
        eq3 = MathTex(r"\text{donde } E=D = 2m_2 L_1 lc_2 \sin(\beta_{rel})", color=TEXT_COLOR).next_to(eq2, DOWN, buff=0.5)
        c_group = VGroup(eq2, eq3).scale(0.8).next_to(eq1, DOWN, buff=0.5)

        self.play(Write(eq1))
        self.wait(1)
        self.play(Write(c_group))
        self.wait(2)
        
        origin = np.array([0, -2.5, 0])
        arm_group = VGroup()
        t_index = ValueTracker(0.0)
        length_trebol = len(sim_data.Alpha_trebol)
        
        def update_dyn_arm(mob):
            idx = int(t_index.get_value())
            if idx >= length_trebol: idx = length_trebol - 1
            alpha = sim_data.Alpha_trebol[idx]
            th2 = sim_data.Th2_trebol[idx]
            
            arm, p2 = get_robot_arm(alpha, th2, origin)
            
            p0 = origin
            p1 = p0 + np.array([0.3 * VISUAL_SCALE * np.cos(alpha), 0.3 * VISUAL_SCALE * np.sin(alpha), 0])
            com1 = (p0 + p1) / 2
            com2 = (p1 + p2) / 2
            
            g_arrow1 = Arrow(com1, com1 + DOWN*1.5, color="#2ECC71", buff=0, max_tip_length_to_length_ratio=0.15)
            g_arrow2 = Arrow(com2, com2 + DOWN*1.5, color="#2ECC71", buff=0, max_tip_length_to_length_ratio=0.15)
            
            g_label1 = MathTex("G_1", color="#2ECC71", font_size=24).next_to(g_arrow1.get_end(), DOWN, buff=0.1)
            g_label2 = MathTex("G_2", color="#2ECC71", font_size=24).next_to(g_arrow2.get_end(), DOWN, buff=0.1)
            
            mob.become(VGroup(arm, g_arrow1, g_arrow2, g_label1, g_label2))
            
        arm_group.add_updater(update_dyn_arm)
        self.add(arm_group)
        
        self.play(t_index.animate.set_value(length_trebol - 1), run_time=6, rate_func=linear)
        self.wait(1)
        
        self.play(FadeOut(VGroup(eq1, c_group, arm_group)))

class Escena4_Motor(Scene):
    def construct(self):
        title = Text("Selección de Motor y Relación de Transmisión ( MATLAB )", color=TEXT_COLOR, font_size=32, weight=BOLD).to_edge(UP)
        self.play(Write(title))
        
        # We find exact domain bounds
        max_t = np.max(sim_data.tiempo)
        
        axes = Axes(
            x_range=[0, max_t, max_t/5],
            y_range=[-max(sim_data.T1_max, sim_data.T2_max)*1.2, max(sim_data.T1_max, sim_data.T2_max)*1.2, 0.4],
            x_length=6,
            y_length=4,
            axis_config={"color": TEXT_COLOR},
            tips=False
        ).to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        
        labels = axes.get_axis_labels(x_label="t\\:[s]", y_label=r"\tau\\:[Nm]")
        for label in labels:
            label.set_color(TEXT_COLOR)
            
        # Draw T1 Line dynamically mapped from Torques[0, :]
        # We use a shortcut to draw lines connecting points
        t1_pts = [axes.c2p(sim_data.tiempo[i], sim_data.Torques[0, i]) for i in range(0, len(sim_data.tiempo), 10)]
        curve = VMobject(color="#E53935").set_points_as_corners(t1_pts)
        
        # Buscamos el punto pico
        peak_idx = np.argmax(np.abs(sim_data.Torques[0, :]))
        peak_x = sim_data.tiempo[peak_idx]
        peak_y = sim_data.Torques[0, peak_idx]
        
        peak_pt = axes.c2p(peak_x, peak_y)
        peak_dot = Dot(peak_pt, color="#E53935", radius=0.1)
        peak_label = MathTex(rf"\tau_{{max}} = \mathbf{{{abs(peak_y):.4f}\text{{ N}}\cdot\text{{m}}}}", color="#E53935", font_size=26).next_to(peak_dot, UP)
        
        self.play(Create(axes), Write(labels))
        self.play(Create(curve), run_time=3)
        self.play(FadeIn(peak_dot), Write(peak_label))
        
        t_motor = 0.098
        G1 = abs(peak_y) / t_motor
        
        eq1 = MathTex(r"G = \frac{\tau_{load} \cdot FS}{\tau_{mot} \cdot \eta}", color=TEXT_COLOR).shift(RIGHT * 3 + UP * 1)
        eq2 = MathTex(rf"\tau_{{mot}} = {t_motor}\text{{ N}}\cdot\text{{m}}", r"\text{ (Máx. Efi.)}", color=TEXT_COLOR, font_size=28).next_to(eq1, DOWN, buff=0.8)
        eq3 = Tex(r"\textbf{Resultado (\%100 Real): }", rf"$G \approx {G1:.2f}$", color=TEXT_COLOR, font_size=32).next_to(eq2, DOWN, buff=1)
        eq3[1].set_color("#1E88E5")
        
        self.play(Write(eq1))
        self.wait(1)
        self.play(Write(eq2))
        self.wait(1)
        
        box = SurroundingRectangle(eq3, color="#1E88E5", buff=0.3, corner_radius=0.1)
        self.play(Write(eq3), Create(box))
        
        self.wait(3)
        self.play(FadeOut(VGroup(title, axes, labels, curve, peak_dot, peak_label, eq1, eq2, eq3, box)))

class Escena5_Cierre(Scene):
    def construct(self):
        title = Text("Control Dinámico Verificado con MATLAB", color="#2ECC71", font_size=42, weight=BOLD).to_edge(UP)
        self.play(Write(title))
        
        origin = np.array([0, -1.5, 0])
        robot_group = VGroup()
        t_index = ValueTracker(0.0)
        
        # Usamos toda la trayectoria (Calibracion -> Init -> Path -> Stop) completita de MATLAB
        length_full = len(sim_data.Alphaf)
        
        def update_robot(mob):
            idx = int(t_index.get_value())
            if idx >= length_full: idx = length_full - 1
            alpha = sim_data.Alphaf[idx]
            th2 = sim_data.Th2f[idx]
            new_rob, p2 = get_robot_arm(alpha, th2, origin=origin)
            mob.become(new_rob)
            
        robot_group.add_updater(update_robot)
        self.add(robot_group)
        
        path = TracedPath(lambda: get_robot_arm(sim_data.Alphaf[int(np.clip(t_index.get_value(), 0, length_full-1))], sim_data.Th2f[int(np.clip(t_index.get_value(), 0, length_full-1))], origin)[1], stroke_color="#2ECC71", stroke_width=6)
        self.add(path)
        
        # Movimiento full 
        self.play(t_index.animate.set_value(length_full - 1), run_time=6, rate_func=smooth)
        self.wait(2)


class Escena6_CalculoVelocidades(Scene):
    def construct(self):
        # Colores extraidos de las imagenes
        C_RED = "#E63946"
        C_BLUE = "#457B9D"
        C_ORANGE = "#F4A261"
        C_PINK = "#F15BB5"
        C_BROWN = "#9C6644"
        C_GREEN_BG = "#A7C957"
        C_BLACK = "#333333"

        def color_eq(eq_obj, color_map):
            for i, c in color_map.items():
                if i < len(eq_obj):
                    eq_obj[i].set_color(c)

        # -------------------------------------------------------------------------
        # FOTO 1: Elegir motores y Cinemática Directa
        # Robot con cotas completas como en la imagen de referencia
        # -------------------------------------------------------------------------
        title1 = Text("Elegir motores", color=C_RED, font_size=40, weight=BOLD).to_corner(UL)
        self.play(FadeIn(title1))

        # Posición del robot: más a la izquierda para no solapar las ecuaciones inferiores
        origin = np.array([-5.8, -2.0, 0])
        L1_val, L2_val = 1.9, 1.9
        q1_val = np.radians(20)   # primer eslabón: bajo, casi horizontal
        q2_val = np.radians(50)   # q2 RELATIVO: suma q1+q2 = 70°

        p0 = origin
        p1 = p0 + np.array([L1_val * np.cos(q1_val),        L1_val * np.sin(q1_val),        0])
        p2 = p1 + np.array([L2_val * np.cos(q1_val+q2_val), L2_val * np.sin(q1_val+q2_val), 0])

        # --- Ejes ---
        ax_len_x, ax_len_y = 4.8, 4.5
        ax_x = Arrow(origin, origin + RIGHT*ax_len_x, color=C_BLACK, buff=0, stroke_width=3, tip_length=0.2)
        ax_y = Arrow(origin, origin + UP*ax_len_y,    color=C_BLACK, buff=0, stroke_width=3, tip_length=0.2)

        # --- Eslabones como líneas delgadas (tipo barra mecánica) ---
        link1 = Line(p0, p1, color=C_PINK, stroke_width=8).set_z_index(1)
        link2 = Line(p1, p2, color=C_PINK, stroke_width=8).set_z_index(1)

        # --- Articulaciones ---
        j0 = Dot(p0, color=C_BLUE, radius=0.14).set_z_index(3)
        j1 = Dot(p1, color=C_BLUE, radius=0.14).set_z_index(3)
        j2 = Dot(p2, color=C_RED,  radius=0.20).set_z_index(3)

        # --- Etiquetas L1 y L2 (ENCIMA de los eslabones) ---
        mid1 = (p0 + p1)/2
        mid2 = (p1 + p2)/2
        perp1 = np.array([-np.sin(q1_val), np.cos(q1_val), 0]) * 0.35
        perp2 = np.array([-np.sin(q1_val+q2_val), np.cos(q1_val+q2_val), 0]) * 0.35
        # +perp1 coloca L1 encima de la línea (lado izquierdo del vector de avance = arriba visualmente)
        lbl_L1 = MathTex(r"L_1", color=C_PINK, font_size=30).move_to(mid1 + perp1)
        lbl_L2 = MathTex(r"L_2", color=C_PINK, font_size=30).move_to(mid2 + perp2 + LEFT*0.1)

        # --- Arco y etiqueta q1 (base) ---
        arc_q1 = Arc(radius=0.5, start_angle=0, angle=q1_val,
                     color=C_BROWN, stroke_width=2).shift(p0)
        lbl_q1 = MathTex(r"q_1", color=C_BROWN, font_size=26).move_to(
            p0 + 0.78 * np.array([np.cos(q1_val/2), np.sin(q1_val/2), 0]))

        # --- Arco y etiqueta q2 (codo) ---
        # q2 va desde la dirección de L1 hasta la dirección de L1+L2
        arc_q2 = Arc(radius=0.45, start_angle=q1_val, angle=q2_val,
                     color=C_BROWN, stroke_width=2).shift(p1)
        lbl_q2 = MathTex(r"q_2", color=C_BROWN, font_size=26).move_to(
            p1 + 0.72 * np.array([np.cos(q1_val + q2_val/2), np.sin(q1_val + q2_val/2), 0]))

        # --- Línea gris punteada de referencia en el codo (muestra que q2 es relativo a L1) ---
        # Se extiende desde p1 en la dirección de L1 (continuación del primer eslabón)
        ref_len = 0.7
        dir_L1 = np.array([np.cos(q1_val), np.sin(q1_val), 0])
        ref_end = p1 + dir_L1 * ref_len
        ref_line_q2 = DashedLine(p1, ref_end, color="#888888",
                                  dash_length=0.08, dashed_ratio=0.5, stroke_width=2)

        # --- Proyecciones punteadas ---
        dash_kw = dict(dash_length=0.12, dashed_ratio=0.5, stroke_width=2)

        # x1 = proyección horizontal de p0 a (p1.x, p0.y)
        p1_foot_x = np.array([p1[0], p0[1], 0])
        dash_x1 = DashedLine(p0, p1_foot_x, color=C_BLUE, **dash_kw)

        # y1 = proyección vertical de (p1.x, p0.y) a p1
        dash_y1 = DashedLine(p1_foot_x, p1, color=C_ORANGE, **dash_kw)

        # x2 = proyección horizontal desde p1 a (p2.x, p1.y)
        p2_foot_x = np.array([p2[0], p1[1], 0])
        dash_x2 = DashedLine(p1, p2_foot_x, color=C_BLUE, **dash_kw)

        # y2 = proyección vertical desde (p2.x, p1.y) a p2
        dash_y2 = DashedLine(p2_foot_x, p2, color=C_ORANGE, **dash_kw)

        # Vertical desde p2 al eje X (para cerrar el rectángulo)
        p2_bot = np.array([p2[0], p0[1], 0])
        dash_vert_p2 = DashedLine(p2_bot, p2, color="#AAAAAA", **dash_kw)

        # Horizontal del eje Y hasta p2 para la cota Y
        p2_left = np.array([p0[0], p2[1], 0])
        dash_horiz_p2 = DashedLine(p2_left, p2, color="#AAAAAA", **dash_kw)

        # --- Etiquetas de las cotas intermedias ---
        lbl_x1 = MathTex(r"x_1", color=C_BLUE, font_size=26).next_to(
            (p0 + p1_foot_x)/2, DOWN, buff=0.12)
        lbl_x2 = MathTex(r"x_2", color=C_BLUE, font_size=26).next_to(
            (p1 + p2_foot_x)/2, DOWN, buff=0.12)
        lbl_y1 = MathTex(r"y_1", color=C_ORANGE, font_size=26).next_to(
            (p1_foot_x + p1)/2, RIGHT, buff=0.12)
        lbl_y2 = MathTex(r"y_2", color=C_ORANGE, font_size=26).next_to(
            (p2_foot_x + p2)/2, RIGHT, buff=0.12)

        # --- Cotas maestras X e Y con flechas dobles ---
        offset_top = 0.55   # sobre el dibujo
        offset_right = 0.55  # a la derecha del dibujo

        # Cota X (horizontal, encima)
        x_top_y = p2[1] + offset_top
        brace_x_line = DoubleArrow(
            np.array([p0[0], x_top_y, 0]),
            np.array([p2[0], x_top_y, 0]),
            color=C_BLUE, buff=0, stroke_width=2, tip_length=0.18
        )
        lbl_X = MathTex(r"x", color=C_BLUE, font_size=36).next_to(brace_x_line, UP, buff=0.1)

        # Cota Y (vertical, a la derecha)
        y_right_x = p2[0] + offset_right
        brace_y_line = DoubleArrow(
            np.array([y_right_x, p0[1], 0]),
            np.array([y_right_x, p2[1], 0]),
            color="#8B008B", buff=0, stroke_width=2, tip_length=0.18
        )
        lbl_Y = MathTex(r"y", color="#8B008B", font_size=36).next_to(brace_y_line, RIGHT, buff=0.1)

        # --- Etiqueta Objetivo + flecha ---
        lbl_objetivo = Text("Objetivo", color=C_BLACK, font_size=22)
        lbl_xy = MathTex(r"(x,y)", color=C_RED, font_size=28)
        obj_group = VGroup(lbl_xy, lbl_objetivo).arrange(DOWN, buff=0.05).next_to(p2 + UP*0.2 + RIGHT*0.8, UP)
        arrow_obj = Arrow(lbl_objetivo.get_bottom(), p2 + UP*0.22, color=C_BLACK,
                          buff=0.05, stroke_width=2, tip_length=0.15)

        # --- Composición y animación por etapas ---
        axes_group = VGroup(ax_x, ax_y)
        robot_core = VGroup(link1, link2, j0, j1, j2)
        angle_marks = VGroup(arc_q1, arc_q2, lbl_q1, lbl_q2, ref_line_q2)
        link_labels = VGroup(lbl_L1, lbl_L2)
        dashed_lines = VGroup(dash_x1, dash_x2, dash_y1, dash_y2, dash_vert_p2, dash_horiz_p2)
        dim_labels = VGroup(lbl_x1, lbl_x2, lbl_y1, lbl_y2)
        master_dims = VGroup(brace_x_line, lbl_X, brace_y_line, lbl_Y)
        objetivo_group = VGroup(obj_group, arrow_obj)

        robot_drawing = VGroup(axes_group, robot_core, angle_marks, link_labels,
                               dashed_lines, dim_labels, master_dims, objetivo_group)

        self.play(FadeIn(axes_group), FadeIn(robot_core))
        self.play(FadeIn(link_labels), FadeIn(angle_marks))
        self.play(Create(dashed_lines), FadeIn(dim_labels))
        self.play(FadeIn(master_dims), FadeIn(objetivo_group))

        # Ecuaciones "donde" en la DERECHA
        eq_d1_1 = MathTex(r"\text{donde} \quad", r"x_1", "=", r"L_1", r"\cos(", r"q_1", ")", color=C_BLACK, font_size=36)
        color_eq(eq_d1_1, {1: C_BLUE, 3: C_PINK, 5: C_BROWN})
        eq_d1_2 = MathTex(r"y_1", "=", r"L_1", r"\sin(", r"q_1", ")", color=C_BLACK, font_size=36)
        color_eq(eq_d1_2, {0: C_ORANGE, 2: C_PINK, 4: C_BROWN})
        eq_d1_3 = MathTex(r"x_2", "=", r"L_2", r"\cos(", r"q_1", "+", r"q_2", ")", color=C_BLACK, font_size=36)
        color_eq(eq_d1_3, {0: C_BLUE, 2: C_PINK, 4: C_BROWN, 6: C_BROWN})
        eq_d1_4 = MathTex(r"y_2", "=", r"L_2", r"\sin(", r"q_1", "+", r"q_2", ")", color=C_BLACK, font_size=36)
        color_eq(eq_d1_4, {0: C_ORANGE, 2: C_PINK, 4: C_BROWN, 6: C_BROWN})

        group_donde = VGroup(eq_d1_1, eq_d1_2, eq_d1_3, eq_d1_4)
        group_donde.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        group_donde.move_to(np.array([2.8, 1.2, 0]))
        self.play(Write(group_donde))
        self.wait(0.5)

        # Ecuaciones x(t) y y(t) en la parte inferior
        eq_x = MathTex(r"x(t)", "=", r"x_1", "+", r"x_2", "=",
                       r"L_1", r"\cos(", r"q_1(t)", ")", "+",
                       r"L_2", r"\cos(", r"q_1(t)", "+", r"q_2(t)", ")",
                       color=C_BLACK, font_size=28)
        color_eq(eq_x, {0: C_RED, 2: C_BLUE, 4: C_BLUE, 6: C_PINK, 8: C_BROWN, 11: C_PINK, 13: C_BROWN, 15: C_BROWN})

        eq_y = MathTex(r"y(t)", "=", r"y_1", "+", r"y_2", "=",
                       r"L_1", r"\sin(", r"q_1(t)", ")", "+",
                       r"L_2", r"\sin(", r"q_1(t)", "+", r"q_2(t)", ")",
                       color=C_BLACK, font_size=28)
        color_eq(eq_y, {0: C_RED, 2: C_ORANGE, 4: C_ORANGE, 6: C_PINK, 8: C_BROWN, 11: C_PINK, 13: C_BROWN, 15: C_BROWN})

        group_xy = VGroup(eq_x, eq_y).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        group_xy.to_edge(DOWN, buff=0.5).shift(RIGHT*0.5)

        self.play(Write(group_xy))
        self.wait(2)


        # -------------------------------------------------------------------------
        # FOTO 2: Derivadas Temporales y Jacobiana
        # Fade out TODO lo de foto 1 limpio, luego mostrar nueva info
        # -------------------------------------------------------------------------
        self.play(FadeOut(robot_drawing), FadeOut(title1), FadeOut(group_donde), FadeOut(group_xy))

        # Título completo
        title2 = Text("Velocidades", color=C_ORANGE, font_size=36, weight=BOLD)
        subtitle2 = Text(
            ", al derivar x e y respecto al tiempo usando\nla regla de la cadena, obtenemos las componentes\nde la velocidad lineal.",
            color=C_BLACK, font_size=22
        )
        title_line = VGroup(title2, subtitle2).arrange(RIGHT, aligned_edge=UP).to_corner(UL)
        self.play(Write(title_line))
        self.wait(1)

        # ẋ(t) y ẏ(t) — Colores según imagen manual (Rojo, Rosado, Marrón, Negro)
        eq_dx = MathTex(
            r"\dot{x}(t)", r"=", r"-", 
            r"L_1", r"\sin", r"(q_1(t))", r"\dot{q}_1(t)",
            r"-",
            r"L_2", r"\sin", r"(q_1(t)+q_2(t))", r"(\dot{q}_1(t)+\dot{q}_2(t))",
            font_size=28, color=C_BLACK
        )
        eq_dx[0:3].set_color(C_RED)    # \dot{x}(t), =, -
        eq_dx[3].set_color(C_PINK)     # L_1
        eq_dx[5:7].set_color(C_BROWN)  # (q_1(t)), \dot{q}_1(t)
        eq_dx[8].set_color(C_PINK)     # L_2
        eq_dx[10:12].set_color(C_BROWN) # argumentos y multiplicadores con q

        eq_dy = MathTex(
            r"\dot{y}(t)", r"=", 
            r"L_1", r"\cos", r"(q_1(t))", r"\dot{q}_1(t)",
            r"+",
            r"L_2", r"\cos", r"(q_1(t)+q_2(t))", r"(\dot{q}_1(t)+\dot{q}_2(t))",
            font_size=28, color=C_BLACK
        )
        eq_dy[0:2].set_color(C_RED)     # \dot{y}(t), =
        eq_dy[2].set_color(C_PINK)      # L_1
        eq_dy[4:6].set_color(C_BROWN)   # q_1(t), \dot{q}_1(t)
        eq_dy[7].set_color(C_PINK)      # L_2
        eq_dy[9:11].set_color(C_BROWN)  # q_1(t)+q_2(t), \dot{q}_1(t)+\dot{q}_2(t)

        group_derivs = VGroup(eq_dx, eq_dy).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        group_derivs.next_to(title_line, DOWN, buff=0.7).to_edge(LEFT, buff=0.5)
        self.play(Write(group_derivs))
        self.wait(2)

        # Texto Jacobiana
        jacob_text = Text(
            "Lo organizamos en una matriz que se conoce como Jacobiana (J)",
            color=C_BLACK, font_size=26
        ).next_to(group_derivs, DOWN, buff=0.6).to_edge(LEFT, buff=0.5)
        self.play(Write(jacob_text))

        # Jacobiana completa (escalada para que entre)
        jacob_eq = MathTex(
            r"\begin{bmatrix} \dot{x} \\ \dot{y} \end{bmatrix}", r"=",
            r"\begin{bmatrix}"
            r"-(L_1 \sin q_1 + L_2 \sin(q_1{+}q_2)) & -L_2 \sin(q_1{+}q_2) \\"
            r"L_1 \cos q_1 + L_2 \cos(q_1{+}q_2) & L_2 \cos(q_1{+}q_2)"
            r"\end{bmatrix}",
            r"\begin{bmatrix} \dot{q}_1 \\ \dot{q}_2 \end{bmatrix}",
            color=C_BLACK, font_size=30
        )
        jacob_eq[0].set_color(C_RED)
        jacob_eq[2].set_color(C_BLUE)
        jacob_eq[3].set_color(C_BROWN)
        jacob_eq.next_to(jacob_text, DOWN, buff=0.4).to_edge(LEFT, buff=0.3)

        box_j = SurroundingRectangle(jacob_eq[2], color=C_GREEN_BG, fill_opacity=0.4, buff=0.15)
        j_label = MathTex(r"J(\theta)", color=C_GREEN_BG, font_size=32).next_to(box_j, DOWN, buff=0.15)

        self.play(FadeIn(box_j), Write(jacob_eq), Write(j_label))
        self.wait(2)

        # -------------------------------------------------------------------------
        # FOTO 3: Verificacion del trebol
        # -------------------------------------------------------------------------
        self.play(FadeOut(VGroup(title_line, group_derivs, jacob_text, jacob_eq, box_j, j_label)))

        v_title = Text("¿Y como verificamos que el trebol si dibuje entre 1 a 10 cm/s?",
                       color=C_BLACK, font_size=30).to_edge(UP, buff=1.2)
        v_eq = MathTex(r"V_{\text{Total}}", "=", r"\sqrt{\,\dot{x}(t)^2 + \dot{y}(t)^2\,}", color=C_BLACK, font_size=48)
        v_eq[0].set_color(C_RED)
        v_eq.center()

        self.play(Write(v_title))
        self.play(Write(v_eq))
        self.wait(2)

        # -------------------------------------------------------------------------
        # FOTO 4: Velocidades Inversas
        # -------------------------------------------------------------------------
        self.play(FadeOut(v_title), FadeOut(v_eq))

        inv_jacob = MathTex(
            r"\begin{bmatrix} \dot{q}_1(t) \\ \dot{q}_2(t) \end{bmatrix}",
            "=", r"J^{-1}(\theta)",
            r"\begin{bmatrix} \dot{x} \\ \dot{y} \end{bmatrix}",
            color=C_BLACK, font_size=40
        )
        inv_jacob[0].set_color(C_BROWN)
        inv_jacob[2].set_color(C_GREEN_BG)
        inv_jacob[3].set_color(C_RED)
        inv_jacob.to_edge(UP, buff=1.0)
        self.play(Write(inv_jacob))

        vel_text2 = Text("Velocidades", color=C_ORANGE, font_size=36, weight=BOLD)\
            .next_to(inv_jacob, DOWN, buff=0.7).to_edge(LEFT)
        self.play(Write(vel_text2))

        eq_q1 = MathTex(
            r"\dot{\theta}_1", "=",
            r"\frac{\dot{x}\cos(q_1{+}q_2) + \dot{y}\sin(q_1{+}q_2)}{L_1\sin(q_2)}",
            color=C_BLACK, font_size=36
        )
        eq_q1[0].set_color(C_RED)

        eq_q2 = MathTex(
            r"\dot{\theta}_2", "=",
            r"\frac{-\dot{x}(L_1\cos q_1 + L_2\cos(q_1{+}q_2))"
            r"- \dot{y}(L_1\sin q_1 + L_2\sin(q_1{+}q_2))}{L_1 L_2\sin q_2}",
            r"-\dot{\theta}_1",
            color=C_BLACK, font_size=28
        )
        eq_q2[0].set_color(C_RED)
        eq_q2[3].set_color(C_RED)

        group_vels = VGroup(eq_q1, eq_q2).arrange(DOWN, aligned_edge=LEFT, buff=0.9)
        group_vels.next_to(vel_text2, DOWN, buff=0.6).to_edge(LEFT, buff=0.5)
        self.play(Write(group_vels))
        self.wait(2)

        # -------------------------------------------------------------------------
        # FOTO 5: Postura y Ejemplo Numerico
        # -------------------------------------------------------------------------
        self.play(FadeOut(VGroup(inv_jacob, vel_text2, group_vels)))

        msg_postura = Text("No hay una unica velocidad — depende de la postura",
                           color=C_BLACK, font_size=30).to_edge(UP)
        msg_ejemplo = Text("Ejemplo:", color=C_GREEN_BG, font_size=32, weight=BOLD)\
            .next_to(msg_postura, DOWN, buff=0.8).to_edge(LEFT)
        self.play(Write(msg_postura), Write(msg_ejemplo))

        datos_group = VGroup(
            MathTex(r"L_1 = 0.3\text{ m}", color=C_PINK, font_size=34),
            MathTex(r"L_2 = 0.3\text{ m}", color=C_PINK, font_size=34),
            MathTex(r"q_1 = 45^\circ", color=C_BROWN, font_size=34),
            MathTex(r"q_2 = 90^\circ", color=C_BROWN, font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)\
         .next_to(msg_ejemplo, DOWN, buff=0.5).to_edge(LEFT)

        res_q1 = MathTex(r"\dot{\theta}_1 \simeq 0.235\text{ rad/s}", color=C_BLACK, font_size=34)
        res_q1[0][:2].set_color(C_RED)
        res_q2 = MathTex(r"\dot{\theta}_2 \simeq -0.47\text{ rad/s}", color=C_BLACK, font_size=34)
        res_q2[0][:2].set_color(C_RED)
        res_group = VGroup(res_q1, res_q2).arrange(DOWN, buff=0.8)\
            .next_to(datos_group, RIGHT, buff=1.5)

        self.play(Write(datos_group), Write(res_group))

        rpm1 = Text("Motor 1: 2.24 RPM", color=C_BLACK, font_size=28)
        rpm2 = Text("Motor 2: 4.48 RPM", color=C_BLACK, font_size=28)
        rpm_group = VGroup(rpm1, rpm2).arrange(DOWN, aligned_edge=LEFT, buff=0.3)\
            .next_to(datos_group, DOWN, buff=0.8).to_edge(LEFT)
        self.play(FadeIn(rpm_group))

        self.wait(4)
