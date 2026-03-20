from manim import *  # Importar la biblioteca Manim para animaciones matemáticas
import numpy as np  # Importar NumPy para cálculos numéricos y arreglos

config.background_color = "#FFFFFF"  # Configurar el fondo de la animación como blanco
TEXT_COLOR = "#333333"  # Definir el color principal del texto (gris oscuro/negro)
VISUAL_SCALE = 10.0  # Escala visual para ajustar las dimensiones de metros a unidades de pantalla

# ----------------------------------------------------
# 1. TRADUCCIÓN DE LA LÓGICA DE MATLAB
# ----------------------------------------------------
def ley_cos(r, L1, L2):
    # Función para calcular ángulos usando la Ley de Cosenos (basada en MATLAB)
    
    # MATLAB: Th1 = acos((L2^2-L1^2-r^2)/(-2*r*L1))
    # Calcular el primer ángulo del primer eslabón
    val1 = np.clip((L2**2 - L1**2 - r**2) / (-2 * r * L1), -1.0, 1.0)
    th1 = np.arccos(val1)  # Aplicar arcocoseno para obtener el ángulo
    
    # Calcular el ángulo interno del segundo eslabón respecto al primero
    val2 = np.clip((r**2 - L1**2 - L2**2) / (-2 * L2 * L1), -1.0, 1.0)
    th2 = np.arccos(val2)  # Obtener el ángulo interno del codo
    
    # Calcular el tercer ángulo del triángulo formado por los eslabones
    val3 = np.clip((L1**2 - L2**2 - r**2) / (-2 * r * L2), -1.0, 1.0)
    th3 = np.arccos(val3)  # Obtener el ángulo final para completar la cinemática
    
    return th1, th2, th3  # Retornar los tres ángulos calculados

def MCG(alpha, beta, dalpha, dbeta, m1, m2, L1, lc2, lc1, Iz1, Iz2, gr):
    # Función para calcular las matrices de Inercia (M), Coriolis (C) y Gravedad (G)
    
    c1 = np.cos(alpha)  # Coseno del ángulo del primer eslabón (humero)
    c2 = np.cos(beta)   # Coseno del ángulo relativo del segundo eslabón (antebraccio)
    s2 = np.sin(beta)   # Seno del ángulo relativo del segundo eslabón
    c12 = np.cos(alpha + beta)  # Coseno de la suma de ángulos (orientación absoluta)

    E = 2 * m2 * L1 * lc2 * s2  # Término de acoplamiento de Coriolis
    D = E  # Simetría en los términos de la matriz de Coriolis
    N = -m2 * L1 * lc2 * s2     # Término negativo para la componente de aceleración centrípeta

    # Definición de la Matriz de Masa/Inercia (M) basada en Euler-Lagrange
    M = np.array([
        [m1*lc1**2 + Iz1 + m2*L1**2 + m2*lc2**2 + Iz2 + 2*m2*L1*lc2*c2, m2*lc2**2 + Iz2 + m2*L1*lc2*c2],
        [m2*lc2**2 + m2*L1*lc2*c2 + Iz2, m2*lc2**2 + Iz2]
    ])
    
    # Definición del Vector de Fuerzas de Coriolis y Centrífugas (C)
    C = np.array([
        D * dalpha * dbeta + E * dbeta**2,
        N * dalpha * dbeta - (-m2 * L1 * lc2 * s2 * dalpha * (dalpha + dbeta))
    ])
    
    # Definición del Vector de Fuerzas Gravitacionales (G)
    G_vec = gr * np.array([
        (m1*lc1 + m2*L1)*c1 + m2*lc2*c12,
        m2*lc2*c12
    ])
    
    return M, C, G_vec  # Retornar las matrices dinámicas del sistema

class SimulationData:
    # Clase contenedora de todos los datos de simulación y trayectorias
    def __init__(self):
        # Inicialización de parámetros geométricos y físicos (idénticos a MATLAB)
        a = 0.1022; b = a / 4; f = 0.3; g = 0.3  # Parámetros para la forma de la Rosa Polar (trébol)
        self.c = 7  # Número de pétalos del trébol
        L1 = 0.3; L2 = 0.3  # Longitud de los eslabones en metros (20-30cm)
        t_total = 1000; escala = 1.25; angulo = 0  # Tiempo de simulación y factor de escala
        m1 = 0.1; m2 = 0.1  # Masas de los eslabones en kg
        ancho = 0.03; alto = 0.01  # Dimensiones transversales para calcular inercia
        
        lc1 = L1 / 2; lc2 = L2 / 2  # Distancia a los centros de masa (mitad del eslabón)
        Iz1 = (1 / 12) * m1 * (ancho**2 + alto**2)  # Momento de inercia del eslabón 1
        Iz2 = (1 / 12) * m2 * (ancho**2 + alto**2)  # Momento de inercia del eslabón 2
        gr = 9.8  # Constante de gravedad en m/s^2
        
        tin = 3; tcal = 4  # Tiempos de aproximación e inicio de calibración
        d_val = -np.pi / 2 if self.c % 2 == 0 else 0  # Ajuste de desfase según número de pétalos
        
        uint = np.linspace(0, 1, 2000)  # Vector unitario de tiempo para interpolación
        # Perfil de velocidad polinomial de 5to orden para suavizar el arranque y frenado
        sint = 10 * uint**3 - 15 * uint**4 + 6 * uint**5
        inter = 2 * np.pi * sint  # Escalamiento del barrido angular (0 a 360 grados)
        
        # Inicialización de arreglos para almacenar la trayectoria calculada
        Alpha_trebol = np.zeros(len(inter))
        Th2_trebol = np.zeros(len(inter))
        rP_trebol = np.zeros(len(inter))
        
        # Generación de la trayectoria del trébol punto a punto
        for k, i in enumerate(inter):
            # Ecuación de la Rosa Polar desplazada a (g, f)
            r = escala * (a + b * np.sin(self.c * i + (d_val + self.c * np.deg2rad(angulo))))
            rP = np.sqrt((r * np.cos(i) + g)**2 + (r * np.sin(i) + f)**2)
            ThetaP = np.arctan2(r * np.sin(i) + f, r * np.cos(i) + g)
            
            # Cálculo de la cinemática inversa (Inversa de la posición)
            th1, th2, th3 = ley_cos(rP, L1, L2)
            alpha = th1 + ThetaP  # Ángulo absoluto del primer motor
            
            Alpha_trebol[k] = alpha  # Guardar ángulo motor 1
            Th2_trebol[k] = th2      # Guardar ángulo motor 2 (interno)
            rP_trebol[k] = rP        # Guardar radio resultante
            
        tstop = 1  # Tiempo de espera estacionaria al final
        # Cálculo de índices para las fases de la animación basado en frecuencia de muestreo
        Nstop = int(np.round(len(Alpha_trebol) * tstop / t_total))
        if Nstop < 1: Nstop = 1  # Asegurar al menos una trama
        
        # Fases de pausa (segmentos constantes en el tiempo)
        AlphaStop = np.ones(Nstop) * Alpha_trebol[0]
        Th2Stop = np.ones(Nstop) * Th2_trebol[0]
        
        # Mezclar fases de trayectoria de dibujo
        Alphaf = np.concatenate((AlphaStop, Alpha_trebol))
        Th2f = np.concatenate((Th2Stop, Th2_trebol))
        
        # Cálculo de la trayectoria suave desde la posición de HOME
        u_len = int(np.round(len(Alpha_trebol) * tin / t_total))
        if u_len < 2: u_len = 10
        u = np.linspace(0, 1, u_len)
        s = 10 * u**3 - 15 * u**4 + 6 * u**5  # Polinomio de 5to orden
        # Interpolación desde 90/30 grados hasta el inicio del trébol
        Alphain = np.pi / 2 + (Alpha_trebol[0] - np.pi / 2) * s
        Th2in = np.pi / 6 + (Th2_trebol[0] - np.pi / 6) * s
        
        AlphaStop2 = np.ones(Nstop) * Alphain[0]
        Th2Stop2 = np.ones(Nstop) * Th2in[0]
        
        # Combinar fases de aproximación
        Alphaf = np.concatenate((AlphaStop2, Alphain, Alphaf))
        Th2f = np.concatenate((Th2Stop2, Th2in, Th2f))
        
        # Cálculo de la trayectoria desde calibración inicial (posición 0, pi)
        ucal_len = int(np.round(len(Alpha_trebol) * tcal / t_total))
        if ucal_len < 2: ucal_len = 10
        ucal = np.linspace(0, 1, ucal_len)
        scal = 10 * ucal**3 - 15 * ucal**4 + 6 * ucal**5
        Alphacal = 0 + (np.pi / 2 - 0) * scal
        Th2cal = np.pi + (np.pi / 6 - np.pi) * scal
        
        # Trayectorias finales concatenadas (todas las fases unidas)
        self.Alphaf = np.concatenate((Alphacal, Alphaf))
        self.Th2f = np.concatenate((Th2cal, Th2f))
        
        # Definición del vector de tiempo total acumulado
        self.tiempo = np.linspace(0, t_total + tcal + tin + 2 * tstop, len(self.Alphaf))
        
        # Cálculo numérico de derivadas (Velocidad y Aceleración) usando gradient
        DAlphaf = np.gradient(self.Alphaf, self.tiempo)      # Velocidad angular motor 1
        D2Alphaf = np.gradient(DAlphaf, self.tiempo)         # Aceleración angular motor 1
        DTh2f = np.gradient(self.Th2f, self.tiempo)          # Velocidad angular motor 2
        D2Th2f = np.gradient(DTh2f, self.tiempo)             # Aceleración angular motor 2
        
        # Cálculo de los torques necesarios para realizar el dibujo (Inversa de la dinámica)
        self.Torques = np.zeros((2, len(self.Alphaf)))       # Matriz para guardar T1 y T2
        for k in range(len(self.Alphaf)):
            alpha_val = self.Alphaf[k]                      # Ángulo actual humero
            beta_val = np.pi - self.Th2f[k]                 # Ángulo relativo antebrazo
            dalpha_val = DAlphaf[k]                         # Velocidad actual motor 1
            dbeta_val = -DTh2f[k]                           # Velocidad actual motor 2
            d2alpha_val = D2Alphaf[k]                       # Aceleración actual motor 1
            d2beta_val = -D2Th2f[k]                         # Aceleración actual motor 2
            
            # Obtención de matrices dinámicas para el estado actual
            M_mat, C_mat, G_mat = MCG(alpha_val, beta_val, dalpha_val, dbeta_val, m1, m2, L1, lc2, lc1, Iz1, Iz2, gr)
            accel = np.array([d2alpha_val, d2beta_val])      # Vector de aceleraciones articulares
            # Ecuación de Newton-Euler/Lagrange: Torque = M*accel + C + G
            self.Torques[:, k] = np.dot(M_mat, accel) + C_mat + G_mat

        # Selección de picos máximos para dimensionar el motor
        self.T1_max = np.max(np.abs(self.Torques[0, :]))
        self.T2_max = np.max(np.abs(self.Torques[1, :]))
        
        # Atributos accesibles globales para la animación
        self.Alpha_trebol = Alpha_trebol
        self.Th2_trebol = Th2_trebol

sim_data = SimulationData()  # Instanciar y pre-calcular todos los datos (Carga inicial)

# ----------------------------------------------------
# 2. AYUDANTES DE MANIM
# ----------------------------------------------------
def get_robot_arm(alpha, th2, origin=ORIGIN):
    # Función para generar los objetos visuales del brazo robótico (Mobjects)
    
    # Parámetros físicos escalados para visualización (0.3m -> 3 unidades en pantalla)
    L1, L2 = 0.3 * VISUAL_SCALE, 0.3 * VISUAL_SCALE
    p0 = origin  # Punto de base del robot (hombro)
    # Cálculo de la posición del codo (p1) usando el ángulo absoluto de la base (alpha)
    p1 = p0 + np.array([L1 * np.cos(alpha), L1 * np.sin(alpha), 0])
    
    # Cálculo del ángulo absoluto del antebrazo (alpha + beta)
    # Según la lógica definida: beta = pi - th2 (ángulo relativo interno del codo)
    abs_th2 = alpha + (np.pi - th2) 
    
    # Cálculo de la posición de la punta (p2) u Efector Final
    p2 = p1 + np.array([L2 * np.cos(abs_th2), L2 * np.sin(abs_th2), 0])
    
    # Creación visual de los eslabones (Azul para el primer brazo, Rojo para el segundo)
    link1 = Line(p0, p1, color="#1E88E5", stroke_width=20)
    link2 = Line(p1, p2, color="#E53935", stroke_width=20)
    
    # Creación de los puntos (Joints/Articulaciones) para mejorar la estética
    joint0 = Dot(p0, color=TEXT_COLOR, radius=0.2).set_z_index(1)  # Articulación base
    joint1 = Dot(p1, color=TEXT_COLOR, radius=0.2).set_z_index(1)  # Articulación codo
    joint2 = Dot(p2, color=TEXT_COLOR, radius=0.15).set_z_index(1) # Punto final (Lápiz)
    
    # Retornar el grupo de objetos y la posición de la punta para rastrear trayectorias
    return VGroup(link1, link2, joint0, joint1, joint2), p2

# ----------------------------------------------------
# 3. ESCENAS DE LA ANIMACIÓN (Basadas en MATLAB)
# ----------------------------------------------------

class Escena1_Introduccion(Scene):
    # Escena de apertura que muestra el título y los integrantes del proyecto
    def construct(self):
        # Título principal renderizado con LaTeX en negrita
        title = Tex(r"\textbf{Avances del Proyecto Académico}", color=TEXT_COLOR, font_size=48)
        self.play(Write(title))  # Efecto de escritura del título
        self.wait(1)            # Pausa de espera
        self.play(title.animate.to_edge(UP, buff=1))  # Animación del título hacia arriba
        
        # Lista detallada de los cinco integrantes del grupo
        nombres = [
            "1. Alessandra Quintero Rois",
            "2. Daniel Alejandro Torres Sanabria",
            "3. Nicolas Plata Molano",
            "4. Samuel David Negrete Lancheros",
            "5. Samuel Correales"
        ]
        
        # Generar objetos de texto individuales para cada nombre
        integrantes_group = VGroup(*[Text(name, color=TEXT_COLOR, font_size=28) for name in nombres])
        # Alinear nombres verticalmente y ubicarlos a la izquierda
        integrantes_group.arrange(DOWN, aligned_edge=LEFT).next_to(title, DOWN, buff=1.0).to_edge(LEFT, buff=1.5)
        
        self.play(Write(integrantes_group), run_time=4)  # Animación de escritura lenta
        self.wait(1)
        
        # Composición visual del logo representativo de la UNAL
        logo = Circle(radius=1.5, color="#1E88E5", fill_opacity=0.1, stroke_width=6)
        logo_inner = Circle(radius=1.2, color="#E53935", fill_opacity=0.1, stroke_width=4)
        logo_text = Text("UNAL", color=TEXT_COLOR, font_size=36, weight=BOLD).move_to(logo.get_center())
        logo_group = VGroup(logo, logo_inner, logo_text).to_edge(RIGHT, buff=2)
        
        self.play(FadeIn(logo_group, shift=LEFT))  # Aparecer logo desde la derecha
        self.wait(2)
        
        # Transición: Desvanecer todo para limpiar la pantalla
        self.play(FadeOut(VGroup(title, integrantes_group, logo_group)))

class Escena2_Cinematica(Scene):
    # Escena que ilustra la resolución cinemática inversa y el dibujo del trébol
    def construct(self):
        origin = np.array([-3, -1, 0])  # Posición fija de la base del robot
        
        robot_group = VGroup()  # Contenedor para el brazo articulado
        t_index = ValueTracker(0.0)  # Variable de tiempo para controlar la animación
        
        length_trebol = len(sim_data.Alpha_trebol)  # Total de puntos de la trayectoria
        
        def update_robot(mob):
            # Función encargada de actualizar la postura del robot en cada frame
            idx = int(t_index.get_value())  # Obtener el índice actual de la trayectoria
            if idx >= length_trebol: idx = length_trebol - 1  # Evitar desbordamiento
            alpha = sim_data.Alpha_trebol[idx]  # Ángulo de la base según MATLAB
            th2 = sim_data.Th2_trebol[idx]        # Ángulo del codo según MATLAB

            # Generar geometría actualizada y reemplazar el mob anterior
            new_rob, p2 = get_robot_arm(alpha, th2, origin=origin)
            mob.become(new_rob)
            
        robot_group.add_updater(update_robot) # Activar el actualizador dinámico
        
        # Bloque de fórmulas matemáticas que rigen el movimiento (Cinemática Inversa)
        eq_text = MathTex(r"""
        \begin{aligned}
        &r_P^2 = (r\cos i + g)^2 + (r\sin i + f)^2 \\
        &\theta_{int} = \arccos\left(\frac{r_P^2 - L_1^2 - L_2^2}{-2L_1L_2}\right) \\
        &\theta_2 = \theta_{int} \quad \text{(Matlab)} \\
        &\alpha = \theta_1 + \theta_P
        \end{aligned}
        """, color=TEXT_COLOR, font_size=28).to_corner(UL)
        
        # Texto con la velocidad media objetivo planteada
        vel_text = MathTex(r"\mathbf{v = \text{Variable (10 cm/s en prom.)}}", color=TEXT_COLOR, font_size=28).to_corner(UR)
        
        self.add(robot_group) # Renderizar el robot base
        self.play(FadeIn(eq_text), FadeIn(vel_text)) # Mostrar informativos matemáticos
        
        # Crear el trazo persistente (línea verde) que sigue la punta del robot
        path = TracedPath(lambda: get_robot_arm(sim_data.Alpha_trebol[int(np.clip(t_index.get_value(), 0, length_trebol-1))], sim_data.Th2_trebol[int(np.clip(t_index.get_value(), 0, length_trebol-1))], origin)[1], stroke_color="#2ECC71", stroke_width=5)
        self.add(path) # Añadir hilo de dibujo
        
        # Ejecución del movimiento desde el inicio al fin de la trayectoria del trébol
        self.play(t_index.animate.set_value(length_trebol - 1), run_time=8, rate_func=linear)
        self.wait(2)
        # Limpieza de la escena para la siguiente transición
        self.play(FadeOut(VGroup(robot_group, path, eq_text, vel_text)))

class Escena3_Dinamica(Scene):
    # Escena que describe el modelo dinámico y fuerzas aplicadas (Lagrange)
    def construct(self):
        # Ecuación clásica del modelo dinámico de un manipulador de 2 GDL
        eq1 = MathTex(r"\tau = M(q)\ddot{q} + C(q,\dot{q}) + G(q)", color=TEXT_COLOR).to_edge(UP)
        
        # Detalle de la matriz de Coriolis y parámetros auxiliares
        eq2 = MathTex(r"C = \begin{bmatrix} D\dot{\alpha}\dot{\beta} + E\dot{\beta}^2 \\ N\dot{\alpha}\dot{\beta} + m_2 L_1 lc_2 \sin(\beta)\dot{\alpha}(\dot{\alpha}+\dot{\beta}) \end{bmatrix}", color=TEXT_COLOR)
        eq3 = MathTex(r"\text{donde } E=D = 2m_2 L_1 lc_2 \sin(\beta_{rel})", color=TEXT_COLOR).next_to(eq2, DOWN, buff=0.5)
        c_group = VGroup(eq2, eq3).scale(0.8).next_to(eq1, DOWN, buff=0.5)

        self.play(Write(eq1)) # Animación del modelo general
        self.wait(1)
        self.play(Write(c_group)) # Animación de componentes de Coriolis
        self.wait(2)
        
        origin = np.array([0, -2.5, 0]) # Posición centrada para el análisis de fuerzas
        arm_group = VGroup()
        t_index = ValueTracker(0.0)
        length_trebol = len(sim_data.Alpha_trebol)
        
        def update_dyn_arm(mob):
            # Generador dinámico del brazo con visualización de vectores Gravitacionales
            idx = int(t_index.get_value())
            if idx >= length_trebol: idx = length_trebol - 1
            alpha = sim_data.Alpha_trebol[idx]
            th2 = sim_data.Th2_trebol[idx]
            
            arm, p2 = get_robot_arm(alpha, th2, origin) # Dibujo del brazo actual
            
            # Cálculo de los centros de masa (COM) para posicionar las flechas de gravedad
            p0 = origin
            p1 = p0 + np.array([0.3 * VISUAL_SCALE * np.cos(alpha), 0.3 * VISUAL_SCALE * np.sin(alpha), 0])
            com1 = (p0 + p1) / 2 # Centroide del eslabón 1
            com2 = (p1 + p2) / 2 # Centroide del eslabón 2
            
            # Flechas indicadoras de la dirección de la gravedad (Vector G)
            g_arrow1 = Arrow(com1, com1 + DOWN*1.5, color="#2ECC71", buff=0, max_tip_length_to_length_ratio=0.15)
            g_arrow2 = Arrow(com2, com2 + DOWN*1.5, color="#2ECC71", buff=0, max_tip_length_to_length_ratio=0.15)
            
            # Etiquetas informativas para representar las componentes G1 y G2
            g_label1 = MathTex("G_1", color="#2ECC71", font_size=24).next_to(g_arrow1.get_end(), DOWN, buff=0.1)
            g_label2 = MathTex("G_2", color="#2ECC71", font_size=24).next_to(g_arrow2.get_end(), DOWN, buff=0.1)
            
            # Combinar todos los elementos dinámicos
            mob.become(VGroup(arm, g_arrow1, g_arrow2, g_label1, g_label2))
            
        arm_group.add_updater(update_dyn_arm)
        self.add(arm_group) # Añadir simulación dinámica a la pantalla
        
        # Animación del recorrido para mostrar la variabilidad de las fuerzas G
        self.play(t_index.animate.set_value(length_trebol - 1), run_time=6, rate_func=linear)
        self.wait(1)
        
        # Eliminar elementos para la próxima diapositiva
        self.play(FadeOut(VGroup(eq1, c_group, arm_group)))

class Escena4_Motor(Scene):
    # Escena que muestra el análisis de torque para la selección del motor comercial
    def construct(self):
        # Título de la escena indicando la validación contra MATLAB
        title = Text("Selección de Motor y Relación de Transmisión ( MATLAB )", color=TEXT_COLOR, font_size=32, weight=BOLD).to_edge(UP)
        self.play(Write(title))
        
        # Obtención del tiempo máximo de la simulación para escalar el eje X
        max_t = np.max(sim_data.tiempo)
        
        # Configuración de los ejes cartesianos para la gráfica de Torque vs Tiempo
        axes = Axes(
            x_range=[0, max_t, max_t/5], # Rango de tiempo
            y_range=[-max(sim_data.T1_max, sim_data.T2_max)*1.2, max(sim_data.T1_max, sim_data.T2_max)*1.2, 0.4], # Rango de torque con margen
            x_length=6,
            y_length=4,
            axis_config={"color": TEXT_COLOR},
            tips=False # Sin puntas de flecha en los ejes para un look más limpio
        ).to_edge(LEFT, buff=0.5).shift(DOWN * 0.5)
        
        # Etiquetas de los ejes con formato LaTeX
        labels = axes.get_axis_labels(x_label="t\\:[s]", y_label=r"\tau\\:[Nm]")
        for label in labels:
            label.set_color(TEXT_COLOR)
            
        # Generar los puntos de la curva de Torque del motor 1 (T1) a partir de los datos precalculados
        t1_pts = [axes.c2p(sim_data.tiempo[i], sim_data.Torques[0, i]) for i in range(0, len(sim_data.tiempo), 10)]
        curve = VMobject(color="#E53935").set_points_as_corners(t1_pts) # Línea roja para el torque
        
        # Identificar el punto de torque máximo/pico para el dimensionamiento
        peak_idx = np.argmax(np.abs(sim_data.Torques[0, :]))
        peak_x = sim_data.tiempo[peak_idx]
        peak_y = sim_data.Torques[0, peak_idx]
        
        # Crear marcador visual (punto y etiqueta) en el valor máximo de torque
        peak_pt = axes.c2p(peak_x, peak_y)
        peak_dot = Dot(peak_pt, color="#E53935", radius=0.1)
        peak_label = MathTex(rf"\tau_{{max}} = \mathbf{{{abs(peak_y):.4f}\text{{ N}}\cdot\text{{m}}}}", color="#E53935", font_size=26).next_to(peak_dot, UP)
        
        self.play(Create(axes), Write(labels)) # Dibujar ejes y etiquetas
        self.play(Create(curve), run_time=3)  # Dibujar la curva de torque en 3 segundos
        self.play(FadeIn(peak_dot), Write(peak_label)) # Resaltar el valor máximo
        
        # Parámetros del motor propuesto y cálculo de la relación de transmisión G
        t_motor = 0.098  # Torque nominal del motor seleccionado (ej: 0.098 Nm)
        G1 = abs(peak_y) / t_motor  # Relación mínima necesaria G = T_carga / T_motor
        
        # Formulación matemática del cálculo de transmisión
        eq1 = MathTex(r"G = \frac{\tau_{load} \cdot FS}{\tau_{mot} \cdot \eta}", color=TEXT_COLOR).shift(RIGHT * 3 + UP * 1)
        # Especificación del motor elegido
        eq2 = MathTex(rf"\tau_{{mot}} = {t_motor}\text{{ N}}\cdot\text{{m}}", r"\text{ (Máx. Efi.)}", color=TEXT_COLOR, font_size=28).next_to(eq1, DOWN, buff=0.8)
        # Resultado final de la relación de engranajes recomendada
        eq3 = Tex(r"\textbf{Resultado (\%100 Real): }", rf"$G \approx {G1:.2f}$", color=TEXT_COLOR, font_size=32).next_to(eq2, DOWN, buff=1)
        eq3[1].set_color("#1E88E5") # Resaltar el valor de G en azul
        
        self.play(Write(eq1)) # Mostrar fórmula de diseño
        self.wait(1)
        self.play(Write(eq2)) # Mostrar dato del motor
        self.wait(1)
        
        # Recuadro de resaltado para el resultado final de diseño mecánico
        box = SurroundingRectangle(eq3, color="#1E88E5", buff=0.3, corner_radius=0.1)
        self.play(Write(eq3), Create(box))
        
        self.wait(3)
        # Salida de la escena
        self.play(FadeOut(VGroup(title, axes, labels, curve, peak_dot, peak_label, eq1, eq2, eq3, box)))

class Escena5_Cierre(Scene):
    # Escena final que muestra el recorrido completo verificado con éxito
    def construct(self):
        # Título de confirmación final del control dinámico
        title = Text("Control Dinámico Verificado con MATLAB", color="#2ECC71", font_size=42, weight=BOLD).to_edge(UP)
        self.play(Write(title))
        
        origin = np.array([0, -1.5, 0]) # Posición de la base del robot centrada
        robot_group = VGroup() # Contenedor para la cinemática
        t_index = ValueTracker(0.0) # Controlador del flujo de tiempo
        
        # Carga de la trayectoria completa (incluyendo calibración e inicio suave)
        length_full = len(sim_data.Alphaf)
        
        def update_robot(mob):
            # Actualizador para mostrar cada paso de la trayectoria final
            idx = int(t_index.get_value())
            if idx >= length_full: idx = length_full - 1
            alpha = sim_data.Alphaf[idx]
            th2 = sim_data.Th2f[idx]
            new_rob, p2 = get_robot_arm(alpha, th2, origin=origin)
            mob.become(new_rob)
            
        robot_group.add_updater(update_robot)
        self.add(robot_group) # Añadir robot a la escena
        
        # Trazo persistente para visualizar el dibujo final completo (el trébol)
        path = TracedPath(lambda: get_robot_arm(sim_data.Alphaf[int(np.clip(t_index.get_value(), 0, length_full-1))], sim_data.Th2f[int(np.clip(t_index.get_value(), 0, length_full-1))], origin)[1], stroke_color="#2ECC71", stroke_width=6)
        self.add(path)
        
        # Ejecutar la animación a velocidad suave recorriendo toda la secuencia de datos
        self.play(t_index.animate.set_value(length_full - 1), run_time=6, rate_func=smooth)
        self.wait(2)


class Escena6_CalculoVelocidades(Scene):
    # Escena técnica detallada sobre el cálculo de velocidades y la matriz Jacobiana
    def construct(self):
        # Definición de la paleta de colores personalizada extraída de los requerimientos visuales
        C_RED = "#E63946"      # Rojo para variables de salida (puntas, derivadas temporales)
        C_BLUE = "#457B9D"     # Azul para dimensiones en X y articulaciones
        C_ORANGE = "#F4A261"   # Naranja para dimensiones en Y
        C_PINK = "#F15BB5"     # Rosa para eslabones físicos (L1, L2)
        C_BROWN = "#9C6644"    # Marrón para ángulos (q1, q2)
        C_GREEN_BG = "#A7C957" # Verde para resaltar la matriz Jacobiana
        C_BLACK = "#333333"    # Negro para ejes y texto base

        def color_eq(eq_obj, color_map):
            # Función utilitaria para aplicar colores a sub-índices específicos de una ecuación MathTex
            for i, c in color_map.items():
                if i < len(eq_obj):
                    eq_obj[i].set_color(c)

        # -------------------------------------------------------------------------
        # FOTO 1: Cinemática Directa de Posición
        # Presentación del robot con todas sus cotas y etiquetas técnicas
        # -------------------------------------------------------------------------
        title1 = Text("Elegir motores", color=C_RED, font_size=40, weight=BOLD).to_corner(UL)
        self.play(FadeIn(title1))

        # Configuración de la base del robot (esquina inferior izquierda)
        origin = np.array([-5.8, -2.0, 0])
        L1_val, L2_val = 1.9, 1.9 # Longitudes visuales de los eslabones en la animación

        # Trackers para permitir animar el movimiento de los ángulos en tiempo real
        q1_t = ValueTracker(np.radians(20))
        q2_t = ValueTracker(np.radians(50))

        def get_robot_pieces():
            # Función interna que construye todos los componentes del robot dinámicamente
            q1_val = q1_t.get_value()
            q2_val = q2_t.get_value()
            
            p0 = origin # Hombro
            # Posición del codo (p1)
            p1 = p0 + np.array([L1_val * np.cos(q1_val),        L1_val * np.sin(q1_val),        0])
            # Posición de la punta/objetivo (p2)
            p2 = p1 + np.array([L2_val * np.cos(q1_val+q2_val), L2_val * np.sin(q1_val+q2_val), 0])
            
            # --- Ejes Cartesianos de Referencia ---
            ax_len_x, ax_len_y = 5.2, 4.5
            ax_x = Arrow(origin, origin + RIGHT*ax_len_x, color=C_BLACK, buff=0, stroke_width=3, tip_length=0.2)
            ax_y = Arrow(origin, origin + UP*ax_len_y,    color=C_BLACK, buff=0, stroke_width=3, tip_length=0.2)
            
            # --- Dibujo de los Eslabones (Barras mecánicas) ---
            link1 = Line(p0, p1, color=C_PINK, stroke_width=8).set_z_index(1)
            link2 = Line(p1, p2, color=C_PINK, stroke_width=8).set_z_index(1)
            
            # --- Puntos de las Articulaciones ---
            j0 = Dot(p0, color=C_BLUE, radius=0.14).set_z_index(3)
            j1 = Dot(p1, color=C_BLUE, radius=0.14).set_z_index(3)
            j2 = Dot(p2, color=C_RED,  radius=0.20).set_z_index(3) # Punto objetivo resaltado
            
            # --- Etiquetas de Longitud (L1 y L2) ---
            mid1 = (p0 + p1)/2
            mid2 = (p1 + p2)/2
            perp1 = np.array([-np.sin(q1_val), np.cos(q1_val), 0]) * 0.35 # Vector perpendicular para separar etiqueta
            perp2 = np.array([-np.sin(q1_val+q2_val), np.cos(q1_val+q2_val), 0]) * 0.35
            lbl_L1 = MathTex(r"L_1", color=C_PINK, font_size=30).move_to(mid1 + perp1)
            lbl_L2 = MathTex(r"L_2", color=C_PINK, font_size=30).move_to(mid2 + perp2 + LEFT*0.1)
            
            # --- Arcos de Ángulo y Etiquetas q1, q2 ---
            arc_q1 = Arc(radius=0.5, start_angle=0, angle=q1_val, color=C_BROWN, stroke_width=2).shift(p0)
            lbl_q1 = MathTex(r"q_1", color=C_BROWN, font_size=26).move_to(p0 + 0.78 * np.array([np.cos(q1_val/2), np.sin(q1_val/2), 0]))
            
            arc_q2 = Arc(radius=0.45, start_angle=q1_val, angle=q2_val, color=C_BROWN, stroke_width=2).shift(p1)
            lbl_q2 = MathTex(r"q_2", color=C_BROWN, font_size=26).move_to(p1 + 0.72 * np.array([np.cos(q1_val + q2_val/2), np.sin(q1_val + q2_val/2), 0]))
            
            # --- Guía visual punteada para el ángulo q2 relativo ---
            ref_len = 0.7
            dir_L1 = np.array([np.cos(q1_val), np.sin(q1_val), 0])
            ref_end = p1 + dir_L1 * ref_len
            ref_line_q2 = DashedLine(p1, ref_end, color="#888888", dash_length=0.08, dashed_ratio=0.5, stroke_width=2)
            
            # --- Líneas de Proyección Geométrica (Dashed Lines) ---
            dash_kw = dict(dash_length=0.12, dashed_ratio=0.5, stroke_width=2) # Configuración de punteado
            
            p1_foot_x = np.array([p1[0], p0[1], 0])
            dash_x1 = DashedLine(p0, p1_foot_x, color=C_BLUE, **dash_kw) # Proyección X1
            dash_y1 = DashedLine(p1_foot_x, p1, color=C_ORANGE, **dash_kw) # Proyección Y1
            
            p2_foot_x = np.array([p2[0], p1[1], 0])
            dash_x2 = DashedLine(p1, p2_foot_x, color=C_BLUE, **dash_kw) # Proyección X2
            dash_y2 = DashedLine(p2_foot_x, p2, color=C_ORANGE, **dash_kw) # Proyección Y2
            
            p2_bot = np.array([p2[0], p0[1], 0])
            dash_vert_p2 = DashedLine(p2_bot, p2, color="#AAAAAA", **dash_kw) # Línea vertical total a P2
            p2_left = np.array([p0[0], p2[1], 0])
            dash_horiz_p2 = DashedLine(p2_left, p2, color="#AAAAAA", **dash_kw) # Línea horizontal total a P2
            
            # Etiquetas de las proyecciones (x1, x2, y1, y2)
            lbl_x1 = MathTex(r"x_1", color=C_BLUE, font_size=26).next_to((p0 + p1_foot_x)/2, DOWN, buff=0.12)
            lbl_x2 = MathTex(r"x_2", color=C_BLUE, font_size=26).next_to((p1 + p2_foot_x)/2, DOWN, buff=0.12)
            lbl_y1 = MathTex(r"y_1", color=C_ORANGE, font_size=26).next_to((p1_foot_x + p1)/2, RIGHT, buff=0.12)
            lbl_y2 = MathTex(r"y_2", color=C_ORANGE, font_size=26).next_to((p2_foot_x + p2)/2, RIGHT, buff=0.12)
            
            # --- Cotas maestras (Flechas dobles para X total e Y total) ---
            offset_top = 0.55
            offset_right = 0.55
            x_top_y = p2[1] + offset_top
            brace_x_line = DoubleArrow(np.array([p0[0], x_top_y, 0]), np.array([p2[0], x_top_y, 0]), color=C_BLUE, buff=0, stroke_width=2, tip_length=0.18)
            lbl_X = MathTex(r"x", color=C_BLUE, font_size=36).next_to(brace_x_line, UP, buff=0.1)
            
            y_right_x = p2[0] + offset_right
            brace_y_line = DoubleArrow(np.array([y_right_x, p0[1], 0]), np.array([y_right_x, p2[1], 0]), color="#8B008B", buff=0, stroke_width=2, tip_length=0.18)
            lbl_Y = MathTex(r"y", color="#8B008B", font_size=36).next_to(brace_y_line, RIGHT, buff=0.1)
            
            # --- Indicador visual del "Punto Objetivo" (x,y) ---
            lbl_objetivo = Text("Objetivo", color=C_BLACK, font_size=22)
            lbl_xy = MathTex(r"(x,y)", color=C_RED, font_size=28)
            obj_group = VGroup(lbl_xy, lbl_objetivo).arrange(DOWN, buff=0.05).next_to(p2 + UP*0.2 + RIGHT*0.8, UP)
            arrow_obj = Arrow(lbl_objetivo.get_bottom(), p2 + UP*0.22, color=C_BLACK, buff=0.05, stroke_width=2, tip_length=0.15)
            
            # Empaquetado de todos los elementos para retorno organizado
            axes_group = VGroup(ax_x, ax_y)
            robot_core = VGroup(link1, link2, j0, j1, j2)
            angle_marks = VGroup(arc_q1, arc_q2, lbl_q1, lbl_q2, ref_line_q2)
            link_labels = VGroup(lbl_L1, lbl_L2)
            dashed_lines = VGroup(dash_x1, dash_x2, dash_y1, dash_y2, dash_vert_p2, dash_horiz_p2)
            dim_labels = VGroup(lbl_x1, lbl_x2, lbl_y1, lbl_y2)
            master_dims = VGroup(brace_x_line, lbl_X, brace_y_line, lbl_Y)
            objetivo_group = VGroup(obj_group, arrow_obj)
            
            return axes_group, robot_core, angle_marks, link_labels, dashed_lines, dim_labels, master_dims, objetivo_group

        # Ejecución secuencial de la aparición de piezas del diagrama
        static_pieces = get_robot_pieces()
        self.play(FadeIn(static_pieces[0]), FadeIn(static_pieces[1])) # Ejes y brazo
        self.play(FadeIn(static_pieces[3]), FadeIn(static_pieces[2])) # Etiquetas L y ángulos
        self.play(Create(static_pieces[4]), FadeIn(static_pieces[5])) # Proyecciones punteadas
        self.play(FadeIn(static_pieces[6]), FadeIn(static_pieces[7])) # Cotas maestras y Objetivo

        # Definición de la cinemática directa por componentes (Derecha de la pantalla)
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
        group_donde.move_to(np.array([2.8, 1.2, 0])) # Ubicación ala derecha
        self.play(Write(group_donde))
        self.wait(0.5)

        # Ecuaciones finales x(t) y y(t) que suman las componentes
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
        group_xy.to_edge(DOWN, buff=0.5).shift(RIGHT*0.5) # Ubicación inferior

        self.play(Write(group_xy))
        self.wait(1)

        # --- ANIMACIÓN DINÁMICA DE LOS ÁNGULOS (DEMOSTRACIÓN DE MOVIMIENTO) ---
        # Transformar las piezas estáticas en un objeto que se redibuja en cada paso
        dyn_robot = always_redraw(lambda: VGroup(*get_robot_pieces()))
        
        self.remove(*static_pieces) # Quitar lo estático
        self.add(dyn_robot)         # Añadir lo dinámico
        
        robot_drawing = dyn_robot # Referencia para el desvanecimiento posterior
        
        # Realizar un movimiento de ida y vuelta para mostrar la reacción del diagrama
        self.play(
            q1_t.animate.set_value(np.radians(40)),
            q2_t.animate.set_value(np.radians(20)),
            run_time=6,
            rate_func=there_and_back
        )
        self.wait(2)

        # -------------------------------------------------------------------------
        # FOTO 2: Cinemática de Velocidades (Jacobiana)
        # Cambio de tema: Del dominio de la posición al dominio de la velocidad
        # -------------------------------------------------------------------------
        self.play(FadeOut(robot_drawing), FadeOut(title1), FadeOut(group_donde), FadeOut(group_xy))

        # Título explicativo de la derivación temporal
        title2 = Text("Velocidades", color=C_ORANGE, font_size=36, weight=BOLD)
        subtitle2 = Text(
            ", al derivar x e y respecto al tiempo usando\nla regla de la cadena, obtenemos las componentes\nde la velocidad lineal.",
            color=C_BLACK, font_size=22
        )
        title_line = VGroup(title2, subtitle2).arrange(RIGHT, aligned_edge=UP).to_corner(UL)
        self.play(Write(title_line))
        self.wait(1)

        # Expresiones de las derivadas temporales ẋ(t) y ẏ(t)
        eq_dx = MathTex(
            r"\dot{x}(t)", r"=", r"-", 
            r"L_1", r"\sin", r"(q_1(t))", r"\dot{q}_1(t)",
            r"-",
            r"L_2", r"\sin", r"(q_1(t)+q_2(t))", r"(\dot{q}_1(t)+\dot{q}_2(t))",
            font_size=28, color=C_BLACK
        )
        # Aplicamos la paleta de colores técnica
        eq_dx[0:3].set_color(C_RED)    # Salida y signos
        eq_dx[3].set_color(C_PINK)     # Longitud física
        eq_dx[5:7].set_color(C_BROWN)  # Variables articulares
        eq_dx[8].set_color(C_PINK)     # Longitud física
        eq_dx[10:12].set_color(C_BROWN)

        eq_dy = MathTex(
            r"\dot{y}(t)", r"=", 
            r"L_1", r"\cos", r"(q_1(t))", r"\dot{q}_1(t)",
            r"+",
            r"L_2", r"\cos", r"(q_1(t)+q_2(t))", r"(\dot{q}_1(t)+\dot{q}_2(t))",
            font_size=28, color=C_BLACK
        )
        eq_dy[0:2].set_color(C_RED)     # Salida
        eq_dy[2].set_color(C_PINK)      
        eq_dy[4:6].set_color(C_BROWN)   
        eq_dy[7].set_color(C_PINK)      
        eq_dy[9:11].set_color(C_BROWN)  

        # Agrupar y mostrar las derivadas
        group_derivs = VGroup(eq_dx, eq_dy).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        group_derivs.next_to(title_line, DOWN, buff=0.7).to_edge(LEFT, buff=0.5)
        self.play(Write(group_derivs))
        self.wait(2)

        # Introducción al concepto de Matriz Jacobiana
        jacob_text = Text(
            "Lo organizamos en una matriz que se conoce como Jacobiana (J)",
            color=C_BLACK, font_size=26
        ).next_to(group_derivs, DOWN, buff=0.6).to_edge(LEFT, buff=0.5)
        self.play(Write(jacob_text))

        # Representación matricial compacta: V = J * dQ
        jacob_eq = MathTex(
            r"\begin{bmatrix} \dot{x} \\ \dot{y} \end{bmatrix}", r"=",
            r"\begin{bmatrix}"
            r"-(L_1 \sin q_1 + L_2 \sin(q_1{+}q_2)) & -L_2 \sin(q_1{+}q_2) \\"
            r"L_1 \cos q_1 + L_2 \cos(q_1{+}q_2) & L_2 \cos(q_1{+}q_2)"
            r"\end{bmatrix}",
            r"\begin{bmatrix} \dot{q}_1 \\ \dot{q}_2 \end{bmatrix}",
            color=C_BLACK, font_size=30
        )
        jacob_eq[0].set_color(C_RED)   # Velocidad lineal
        jacob_eq[2].set_color(C_BLUE)  # Matriz J
        jacob_eq[3].set_color(C_BROWN) # Velocidad articular
        jacob_eq.next_to(jacob_text, DOWN, buff=0.4).to_edge(LEFT, buff=0.3)

        # Resaltado visual de la matriz J con un fondo verde
        box_j = SurroundingRectangle(jacob_eq[2], color=C_GREEN_BG, fill_opacity=0.4, buff=0.15)
        j_label = MathTex(r"J(\theta)", color=C_GREEN_BG, font_size=32).next_to(box_j, DOWN, buff=0.15)

        self.play(FadeIn(box_j), Write(jacob_eq), Write(j_label))
        self.wait(2)

        # -------------------------------------------------------------------------
        # FOTO 3: Verificación de Velocidad del Trébol
        # Cuestionamiento sobre si la velocidad en la punta cumple los requisitos
        # -------------------------------------------------------------------------
        self.play(FadeOut(VGroup(title_line, group_derivs, jacob_text, jacob_eq, box_j, j_label)))

        v_title = Text("¿Y como verificamos que el trebol si dibuje entre 1 a 10 cm/s?",
                       color=C_BLACK, font_size=30).to_edge(UP, buff=1.2)
        # Fórmula de la norma Euclidiana para la velocidad total
        v_eq = MathTex(r"V_{\text{Total}}", "=", r"\sqrt{\,\dot{x}(t)^2 + \dot{y}(t)^2\,}", color=C_BLACK, font_size=48)
        v_eq[0].set_color(C_RED)
        v_eq.center()

        self.play(Write(v_title))
        self.play(Write(v_eq))
        self.wait(2)

        # -------------------------------------------------------------------------
        # FOTO 4: Cinemática Inversa de Velocidades
        # Uso de la Jacobiana Inversa para hallar velocidades de los motores
        # -------------------------------------------------------------------------
        self.play(FadeOut(v_title), FadeOut(v_eq))

        # Ecuación fundamental inversa: dQ = Jinv * V
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

        # Despeje detallado para cada motor (basado en la inversión analítica de J)
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

        # Agrupación de los resultados de velocidad inversa
        group_vels = VGroup(eq_q1, eq_q2).arrange(DOWN, aligned_edge=LEFT, buff=0.9)
        group_vels.next_to(vel_text2, DOWN, buff=0.6).to_edge(LEFT, buff=0.5)
        self.play(Write(group_vels))
        self.wait(2)

        # -------------------------------------------------------------------------
        # FOTO 5: Postura y Ejemplo Numérico Final
        # Conclusión práctica para el dimensionamiento de RPM de los motores
        # -------------------------------------------------------------------------
        self.play(FadeOut(VGroup(inv_jacob, vel_text2, group_vels)))

        # Nota importante sobre la singularidad y dependencia de la postura
        msg_postura = Text("No hay una unica velocidad — depende de la postura",
                           color=C_BLACK, font_size=30).to_edge(UP)
        msg_ejemplo = Text("Ejemplo:", color=C_GREEN_BG, font_size=32, weight=BOLD)\
            .next_to(msg_postura, DOWN, buff=0.8).to_edge(LEFT)
        self.play(Write(msg_postura), Write(msg_ejemplo))

        # Datos de entrada para el caso de prueba numérico
        datos_group = VGroup(
            MathTex(r"L_1 = 0.3\text{ m}", color=C_PINK, font_size=34),
            MathTex(r"L_2 = 0.3\text{ m}", color=C_PINK, font_size=34),
            MathTex(r"q_1 = 45^\circ", color=C_BROWN, font_size=34),
            MathTex(r"q_2 = 90^\circ", color=C_BROWN, font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)\
         .next_to(msg_ejemplo, DOWN, buff=0.5).to_edge(LEFT)

        # Resultados del cálculo para las velocidades articulares en rad/s
        res_q1 = MathTex(r"\dot{\theta}_1 \simeq 0.235\text{ rad/s}", color=C_BLACK, font_size=34)
        res_q1[0][:2].set_color(C_RED)
        res_q2 = MathTex(r"\dot{\theta}_2 \simeq -0.47\text{ rad/s}", color=C_BLACK, font_size=34)
        res_q2[0][:2].set_color(C_RED)
        res_group = VGroup(res_q1, res_q2).arrange(DOWN, buff=0.8)\
            .next_to(datos_group, RIGHT, buff=1.5)

        self.play(Write(datos_group), Write(res_group))

        # Conversión a RPM para facilitar la compra de motores industriales
        rpm1 = Text("Motor 1: 2.24 RPM", color=C_BLACK, font_size=28)
        rpm2 = Text("Motor 2: 4.48 RPM", color=C_BLACK, font_size=28)
        rpm_group = VGroup(rpm1, rpm2).arrange(DOWN, aligned_edge=LEFT, buff=0.3)\
            .next_to(datos_group, DOWN, buff=0.8).to_edge(LEFT)
        self.play(FadeIn(rpm_group))

        self.wait(4) # Espera final antes de terminar la escena
