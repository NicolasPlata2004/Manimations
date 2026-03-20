from manim import *  # Importa todas las clases y funciones de Manim para animaciones
import numpy as np  # Importa NumPy para cálculos numéricos y manejo de arreglos
from scipy.spatial.transform import Rotation  # Importa utilidades de rotación 3D de SciPy

config.background_color = "#000000"  # Configura el color de fondo de la animación a negro puro

# Función para proyectar coordenadas 3D a un plano 2D isométrico con manejo de profundidad
def project_iso(x, y, z, phi_deg=65, theta_deg=15, rot_z_deg=0):
    rz1 = Rotation.from_euler('z', np.radians(rot_z_deg)).as_matrix()  # Primera rotación en Z (animación)
    rx = Rotation.from_euler('x', np.radians(phi_deg)).as_matrix()  # Inclinación de cámara en X
    rz2 = Rotation.from_euler('z', np.radians(theta_deg)).as_matrix()  # Angulación de cámara en Z
    pt = rx.dot(rz2.dot(rz1.dot([x, y, z])))  # Aplica las matrices de rotación al punto [x,y,z]
    return np.array([pt[0], pt[1], 0]), pt[2]  # Retorna la posición 2D y el valor de profundidad Z 


class Scene0_Intro(Scene):
    def construct(self):
        # Ruta absoluta al archivo del logo de la empresa KYMA
        logo_path = r"C:\Users\nicao\manimations\Investigacion\Titanato de Bario Animacion completa\media\images\script\Logo_Kyma.png"
        logo = ImageMobject(logo_path).set_height(2.5)  # Crea el objeto de imagen con altura predefinida
        
        # Texto principal con tipografía Sans-Serif y negrita usando LaTeX
        kyma_text = Tex(r"\textbf{\textsf{K Y M A}}", font_size=110, color=WHITE)
        full_logo = Group(logo, kyma_text).arrange(RIGHT, buff=1.0)  # Agrupa logo y texto horizontalmente
        full_logo.move_to(UP*1.0)  # Posiciona el grupo en la parte superior
        
        self.play(FadeIn(logo, shift=LEFT*0.8), run_time=1.5)  # Animación de entrada del logo desde la derecha
        self.play(Write(kyma_text), run_time=1.0)  # Animación de escritura para el nombre de la empresa
        self.wait(0.5)
        
        # Lista de nombres de proyectos para el efecto de "slot machine" (tragamonedas)
        words = ["Apolo", "Coralink", "Ion", "JuliaRTB", "Kyno", "Kytron", "Metis", "Roky", "Simlab", "Turing", "Piezo"]
        slot_texts = VGroup(*[Text(w, font_size=75, color=BLUE, weight=BOLD) for w in words])
        
        for t in slot_texts:
            # Alinea cada palabra debajo del texto de KYMA
            t.next_to(kyma_text, DOWN, buff=0.8).align_to(kyma_text, LEFT)
            
        current_text = slot_texts[0]
        self.play(FadeIn(current_text, shift=DOWN*0.5), run_time=0.4)  # Muestra la primera palabra
        
        # Ciclo para alternar rápidamente entre los nombres de los proyectos
        for next_text in slot_texts[1:-1]:
            self.play(
                FadeOut(current_text, shift=DOWN*0.5),
                FadeIn(next_text, shift=DOWN*0.5),
                run_time=0.15  # Velocidad rápida para el efecto de desfile
            )
            current_text = next_text
            
        piezo_txt = slot_texts[-1]  # La palabra objetivo es "Piezo"
        self.play(
            FadeOut(current_text, shift=DOWN*1.0),
            FadeIn(piezo_txt, shift=DOWN*1.0),
            run_time=0.8,
            rate_func=rate_functions.ease_out_elastic  # Efecto de rebote elástico al frenar
        )
        
        # Resalta la palabra seleccionada con color amarillo y un pulso de escala
        self.play(
            piezo_txt.animate.set_color(YELLOW).scale(1.2), 
            run_time=0.5, 
            rate_func=rate_functions.there_and_back
        )
        self.wait(2)  # Pausa final de la introducción
        self.play(FadeOut(Group(*self.mobjects)))  # Limpia la pantalla para la siguiente escena


# Clase para representar la celda unidad de Perovskita (BaTiO3) con sus átomos y medidas
class PerovskiteCell(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Crea los 8 átomos de Bario (Esquinas - Azul)
        self.ba_atoms = [Dot(radius=0.15, color=BLUE) for _ in range(8)]
        # Crea los 6 átomos de Oxígeno (Caras - Rojo)
        self.o_atoms = [Dot(radius=0.1, color=RED) for _ in range(6)]
        # Crea el átomo central de Titanio (Amarillo)
        self.ti_atom = Dot(radius=0.12, color=YELLOW)
        # Inicializa las 12 aristas del cubo
        self.edges = [Line(ORIGIN, UP, color=WHITE, stroke_width=2) for _ in range(12)]
        
        # Elementos de medición de dimensiones (flechas dobles y etiquetas a, b, c)
        self.dim_a_line = DoubleArrow(ORIGIN, UP, color=WHITE, buff=0, max_tip_length_to_length_ratio=0.15, stroke_width=2).set_opacity(0)
        self.dim_b_line = DoubleArrow(ORIGIN, UP, color=WHITE, buff=0, max_tip_length_to_length_ratio=0.15, stroke_width=2).set_opacity(0)
        self.dim_c_line = DoubleArrow(ORIGIN, UP, color=WHITE, buff=0, max_tip_length_to_length_ratio=0.15, stroke_width=2).set_opacity(0)
        self.lbl_a = MathTex("a", font_size=24, color=WHITE).set_opacity(0)
        self.lbl_b = MathTex("b", font_size=24, color=WHITE).set_opacity(0)
        self.lbl_c = MathTex("c", font_size=24, color=WHITE).set_opacity(0)
        
        # Arcos y etiquetas para ángulos inter-axiales (Alpha, Beta, Gamma)
        self.arc_alpha = Arc(radius=0.4, color=WHITE).set_opacity(0).set_fill(opacity=0)
        self.arc_beta = Arc(radius=0.4, color=WHITE).set_opacity(0).set_fill(opacity=0)
        self.arc_gamma = Arc(radius=0.4, color=WHITE).set_opacity(0).set_fill(opacity=0)
        self.lbl_alpha = MathTex(r"\alpha", font_size=20, color=WHITE).set_opacity(0)
        self.lbl_beta = MathTex(r"\beta", font_size=20, color=WHITE).set_opacity(0)
        self.lbl_gamma = MathTex(r"\gamma", font_size=20, color=WHITE).set_opacity(0)
        
        # Planos de Miller (002 y 200) y sus indicadores de distancia d
        self.miller_002 = Polygon(ORIGIN, UP, RIGHT, DOWN, color=BLUE, stroke_width=0).set_fill(BLUE, 0)
        self.miller_200 = Polygon(ORIGIN, UP, RIGHT, DOWN, color=RED, stroke_width=0).set_fill(RED, 0)
        self.d002_arrow = DoubleArrow(ORIGIN, UP, color=BLUE, buff=0, max_tip_length_to_length_ratio=0.1).set_opacity(0)
        self.d200_arrow = DoubleArrow(ORIGIN, UP, color=RED, buff=0, max_tip_length_to_length_ratio=0.1).set_opacity(0)
        self.lbl_d002 = MathTex(r"d_{002}", font_size=20, color=BLUE).set_opacity(0)
        self.lbl_d200 = MathTex(r"d_{200}", font_size=20, color=RED).set_opacity(0)

        # Añade todos los componentes al grupo principal para el renderizado
        self.add(
            self.miller_002, self.miller_200, 
            *self.edges, *self.ba_atoms, *self.o_atoms, self.ti_atom,
            self.dim_a_line, self.dim_b_line, self.dim_c_line,
            self.lbl_a, self.lbl_b, self.lbl_c,
            self.arc_alpha, self.arc_beta, self.arc_gamma,
            self.lbl_alpha, self.lbl_beta, self.lbl_gamma,
            self.d002_arrow, self.d200_arrow, self.lbl_d002, self.lbl_d200
        )
        # Variables de control para mostrar u ocultar capas de información
        self.show_dimensions = False
        self.show_angles = False
        self.show_miller = False

    # Método para actualizar la geometría de la celda en cada cuadro (updater)
    def update_cell(self, t_val, rot_angle, offset=ORIGIN):
        # Define los parámetros de red (a, b, c) en función de la distorsión cuadrática 't_val'
        a = 2.0 - 0.1 * t_val
        b = a
        c = 2.0 + 0.5 * t_val
        
        # Define las coordenadas 3D de las 8 esquinas (átomos de Bario)
        corners = [
            [-a/2, -b/2, -c/2], [a/2, -b/2, -c/2], [a/2, b/2, -c/2], [-a/2, b/2, -c/2],
            [-a/2, -b/2, c/2],  [a/2, -b/2, c/2],  [a/2, b/2, c/2],  [-a/2, b/2, c/2]
        ]
        # Coordenadas de los centros de las caras (átomos de Oxígeno)
        faces = [
            [0, 0, c/2], [0, 0, -c/2],
            [a/2, 0, 0], [-a/2, 0, 0],
            [0, b/2, 0], [0, -b/2, 0]
        ]
        # Posición desplazada del átomo de Titanio (crea el dipolo piezoeléctrico)
        ti_coord = [0, 0, 0.4 * t_val]
        
        # Función interna para proyectar y posicionar un mobject 3D
        def set_pos(mob, coord):
            pt, z = project_iso(*coord, rot_z_deg=rot_angle)
            mob.move_to(pt + offset)
            mob.set_z_index(z)  # Gestiona la profundidad para que lo de adelante tape a lo de atrás
            return pt + offset
            
        # Actualiza posiciones de átomos de Bario
        points_corners = [set_pos(self.ba_atoms[i], corners[i]) for i in range(8)]
        # Actualiza posiciones de átomos de Oxígeno
        for i, coord in enumerate(faces): set_pos(self.o_atoms[i], coord)
        # Actualiza posición del Titanio
        set_pos(self.ti_atom, ti_coord)
        
        # Define y dibuja las 12 aristas conectando las esquinas correspondientes
        edge_pairs = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        for i, (i1, i2) in enumerate(edge_pairs):
            self.edges[i].put_start_and_end_on(points_corners[i1], points_corners[i2])
            avg_z = (self.ba_atoms[i1].z_index + self.ba_atoms[i2].z_index) / 2.0
            self.edges[i].set_z_index(avg_z)
            
        # Toggles behavior using purely opacity to preserve geometry indices safely
        # Control de visualización de flechas de dimensiones (Parámetros de Red)
        if self.show_dimensions:
            for mob in [self.dim_a_line, self.dim_b_line, self.dim_c_line, self.lbl_a, self.lbl_b, self.lbl_c]:
                mob.set_opacity(1)  # Hace visibles los elementos
                mob.set_z_index(100)
                
            p = [project_iso(*c, rot_z_deg=rot_angle)[0] for c in corners]
            
            # Posiciona la flecha 'a' desplazada de la arista para mayor claridad
            a_off = DOWN*0.6 + RIGHT*0.2
            self.dim_a_line.put_start_and_end_on(p[1] + offset + a_off, p[5] + offset + a_off)
            self.lbl_a.move_to((p[1]+p[5])/2 + offset + a_off + DOWN*0.3)
            
            # Posiciona la flecha 'b' paralela a la profundidad
            b_off = UP*0.4 + RIGHT*0.4
            self.dim_b_line.put_start_and_end_on(p[5] + offset + b_off, p[6] + offset + b_off)
            self.lbl_b.move_to((p[5]+p[6])/2 + offset + b_off + RIGHT*0.3)
            
            # Posiciona la flecha 'c' verticalmente
            c_off = LEFT*0.6
            self.dim_c_line.put_start_and_end_on(p[4] + offset + c_off, p[7] + offset + c_off)
            self.lbl_c.move_to((p[4]+p[7])/2 + offset + c_off + LEFT*0.3)
        else:
            for mob in [self.dim_a_line, self.dim_b_line, self.dim_c_line, self.lbl_a, self.lbl_b, self.lbl_c]:
                mob.set_opacity(0)  # Oculta los elementos si no son requeridos
                
        # Control de visualización de arcos de ángulos (Alpha, Beta, Gamma)
        if self.show_angles:
            for mob in [self.arc_alpha, self.arc_beta, self.arc_gamma, self.lbl_alpha, self.lbl_beta, self.lbl_gamma]:
                mob.set_opacity(1)
                mob.set_z_index(100)
            
            p = [project_iso(*c, rot_z_deg=rot_angle)[0] for c in corners]
            
            # Función para dibujar arcos circulares entre dos vectores isométricos
            def draw_arc(o, v1, v2, radius=0.4):
                u = v1 - o
                v = v2 - o
                a1 = np.arctan2(u[1], u[0])
                a2 = np.arctan2(v[1], v[0])
                diff = (a2 - a1) % TAU
                if diff > PI: diff -= TAU
                elif diff < -PI: diff += TAU
                return Arc(radius=radius, start_angle=a1, angle=diff, arc_center=o+offset, color=WHITE).set_fill(opacity=0).set_z_index(100)
                
            o = p[4]  # Origen en la esquina común de los ejes principales
            self.arc_gamma.become(draw_arc(o, p[5], p[0]))
            self.arc_alpha.become(draw_arc(o, p[7], p[0]))
            self.arc_beta.become(draw_arc(o, p[5], p[7]))
            
            # Posiciona las etiquetas griegas en los cuadrantes correspondientes
            self.lbl_gamma.move_to(o + offset + (p[5]-o)*0.3 + (p[0]-o)*0.3)
            self.lbl_alpha.move_to(o + offset + (p[7]-o)*0.3 + (p[0]-o)*0.3)
            self.lbl_beta.move_to(o + offset + (p[5]-o)*0.3 + (p[7]-o)*0.3)
        else:
            for mob in [self.arc_alpha, self.arc_beta, self.arc_gamma, self.lbl_alpha, self.lbl_beta, self.lbl_gamma]:
                mob.set_opacity(0)
                
        # Control de visualización de planos de Miller y distancias interplanares XRD
        if self.show_miller:
            self.miller_002.set_fill(BLUE, 0.4)
            self.miller_200.set_fill(RED, 0.4)
            # Muestra las flechas de distancia d correspondientes a los planos
            for mob in [self.d002_arrow, self.d200_arrow, self.lbl_d002, self.lbl_d200]: mob.set_opacity(1).set_z_index(100)
            
            # Coordenadas relativas de las esquinas para el plano de Miller (002) y (200)
            m002_corn = [[-a/2, -b/2, 0], [a/2, -b/2, 0], [a/2, b/2, 0], [-a/2, b/2, 0]]
            m200_corn = [[0, -b/2, -c/2], [0, b/2, -c/2], [0, b/2, c/2], [0, -b/2, c/2]]
            
            pts_002 = [project_iso(*pt, rot_z_deg=rot_angle)[0] + offset for pt in m002_corn]
            pts_200 = [project_iso(*pt, rot_z_deg=rot_angle)[0] + offset for pt in m200_corn]
            
            # Actualiza los vértices de los polígonos de Miller
            self.miller_002.set_points_as_corners(pts_002)
            self.miller_200.set_points_as_corners(pts_200)
            self.miller_002.set_z_index(-10) # Dibuja los planos al fondo para no tapar los átomos
            self.miller_200.set_z_index(-10)
            
            # Puntos de referencia para las flechas de distancia d_hkl
            p_center = project_iso(0,0,0, rot_z_deg=rot_angle)[0] + offset
            p_top = project_iso(0,0,c/2, rot_z_deg=rot_angle)[0] + offset
            p_right = project_iso(a/2,0,0, rot_z_deg=rot_angle)[0] + offset
            
            self.d002_arrow.put_start_and_end_on(p_center, p_top)
            self.d200_arrow.put_start_and_end_on(p_center, p_right)
            self.lbl_d002.next_to(self.d002_arrow, RIGHT, buff=0.1)
            self.lbl_d200.next_to(self.d200_arrow, UP, buff=0.1)
        else:
            self.miller_002.set_fill(BLUE, 0)
            self.miller_200.set_fill(RED, 0)
            for mob in [self.d002_arrow, self.d200_arrow, self.lbl_d002, self.lbl_d200]: mob.set_opacity(0)


class Scene1_UnitCell(Scene):
    def construct(self):
        # Muestra el texto introductorio sobre el material
        txt1 = Tex(r"El Titanato de Bario ($BaTiO_3$) es un material cristalino.", font_size=36).to_edge(UP, buff=1.0)
        self.play(Write(txt1), run_time=2)
        self.wait(2)
        txt2 = Tex(r"Su estructura básica se repite millones de veces.", font_size=36).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt2))
        self.wait(2)

        # Crea un arreglo de puntos (grid 3x3x3) para representar la red cristalina macroscópica
        grid = VGroup()
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    pt, depth = project_iso((x-1)*1.5, (y-1)*1.5, (z-1)*1.5, rot_z_deg=45)
                    d = Dot(pt, radius=0.08, color=BLUE)
                    d.depth = depth
                    grid.add(d)
                    
        # Ordena por profundidad antes de desvanecer (FadeIn)
        grid.submobjects.sort(key=lambda m: m.depth, reverse=True)
        self.play(FadeIn(grid, shift=UP), run_time=2.5)
        self.wait(2.5)

        # Animación de zoom hacia un nodo de la red y limpieza de pantalla
        self.play(grid.animate.scale(2), run_time=1.5)
        self.play(FadeOut(grid), run_time=1.0)
        
        # Configura la celda para mostrar la transición a estructura cúbica/tetragonal
        txt3 = Tex(r"Estructura Cúbica ($T > 120^\circ\text{C}$).", font_size=32).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt3))
        self.wait(2)

        # Inicializa la celda de perovskita y su rastreador de ángulo para la rotación
        cell = PerovskiteCell()
        cell.scale(1.5).shift(DOWN*0.5)
        angle_tracker = ValueTracker(20)
        cell.add_updater(lambda m, dt: m.update_cell(0, angle_tracker.get_value(), DOWN*0.5))
        
        self.play(FadeIn(cell))
        self.play(angle_tracker.animate.increment_value(90), run_time=4)
        
        # Muestra la leyenda de colores para cada tipo de átomo
        txt_ba = Tex(r"Bario (Ba): Esquinas", font_size=28, color=BLUE).to_edge(LEFT, buff=1.0).shift(UP*1)
        txt_o = Tex(r"Oxígeno (O): Caras", font_size=28, color=RED).next_to(txt_ba, DOWN, aligned_edge=LEFT, buff=0.5)
        txt_ti = Tex(r"Titanio (Ti): Centro", font_size=28, color=YELLOW).next_to(txt_o, DOWN, aligned_edge=LEFT, buff=0.5)
        
        self.play(Write(txt_ba))
        self.play(Write(txt_o))
        self.play(Write(txt_ti))
        self.wait(3)
        
        # Muestra la condición de alta simetría de la fase cúbica
        txt_sym = MathTex(r"\text{Alta simetría perfecta: } a = b = c \text{ y } \alpha = \beta = \gamma = 90^\circ", font_size=36).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt_sym))
        self.wait(2)
        
        # Crea dos celdas pequeñas para mostrar ángulos y parámetros de red simultáneamente
        cube1 = PerovskiteCell()
        for o in cube1.o_atoms: o.set_opacity(0)
        cube1.ti_atom.set_opacity(0)
        cube1.show_angles = True
        cube1.show_dimensions = False
        cube1.scale(1.2).shift(LEFT*1.5 + DOWN*0.5)
        lbl_cube1 = Tex("Ángulos Inter-axiales", font_size=24).move_to(LEFT*1.5 + DOWN*3.1)
        
        cube2 = PerovskiteCell()
        cube2.show_angles = False
        cube2.show_dimensions = True
        cube2.scale(1.2).shift(RIGHT*3.5 + DOWN*0.5)
        lbl_cube2 = Tex("Parámetros de Red", font_size=24).move_to(RIGHT*3.5 + DOWN*3.1)
        
        txt_subtitle = MathTex(r"a = b = c", font_size=32, color=RED).next_to(txt_sym, DOWN, buff=0.2)
        
        # Actualiza manualmente antes de mostrar para evitar fallas visuales en el primer cuadro
        cube1.update_cell(0, angle_tracker.get_value(), LEFT*1.5 + DOWN*0.5)
        cube2.update_cell(0, angle_tracker.get_value(), RIGHT*3.5 + DOWN*0.5)
        
        cell.clear_updaters()
        self.play(
            FadeOut(cell),
            FadeIn(cube1),
            FadeIn(cube2),
            Write(lbl_cube1),
            Write(lbl_cube2),
            Write(txt_subtitle)
        )
        
        # Asigna updaters para la rotación síncrona de ambas celdas
        cube1.add_updater(lambda m, dt: m.update_cell(0, angle_tracker.get_value(), LEFT*1.5 + DOWN*0.5))
        cube2.add_updater(lambda m, dt: m.update_cell(0, angle_tracker.get_value(), RIGHT*3.5 + DOWN*0.5))
        
        self.play(angle_tracker.animate.increment_value(90), run_time=6, rate_func=smooth)
        self.wait(4)
        
        self.play(FadeOut(Group(*self.mobjects)))


# Escena para explicar la morfología observada en Microscopía Electrónica (SEM)
class Scene2_SEM(Scene):
    def construct(self):
        title = Tex(r"Análisis Microestructural (SEM)", font_size=40).to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Función para generar granos cristalinos aleatorios (Voronoi simplificado)
        def create_grains(scale, offset, seed, is_nano=False):
            np.random.seed(seed)
            polys = VGroup()
            arrows = VGroup()
            points = VGroup()
            for dx in range(3):
                for dy in range(3):
                    # Genera vértices aleatorios para cada grano
                    pts = [
                        [dx+np.random.rand()*0.8, dy+np.random.rand()*0.8, 0],
                        [dx+1+np.random.rand()*0.8, dy+np.random.rand()*0.8, 0],
                        [dx+0.5+np.random.rand()*0.8, dy+1+np.random.rand()*0.8, 0],
                        [dx-0.5+np.random.rand()*0.8, dy+0.5+np.random.rand()*0.8, 0]
                    ]
                    polys.add(Polygon(*pts, stroke_width=2, color=WHITE, fill_opacity=0.1))
                    
                    if not is_nano:
                        # Dibuja dipolos alineados en granos grandes
                        arrows.add(Vector(RIGHT*0.6 + UP*0.2, color=YELLOW).move_to(polys[-1].get_center()))
                    else:
                        # Simula desorden atómico en los bordes para nanogranos
                        for p in pts:
                            for _ in range(3):
                                points.add(Dot(np.array(p) + (np.random.rand(3)-0.5)*0.3, radius=0.03, color=RED))
            return VGroup(polys, arrows, points).scale(scale).move_to(offset)

        # Muestra la microestructura de granos grandes con dipolos ordenados
        large_grains = create_grains(1.2, LEFT*3, 42, is_nano=False)
        txt1 = Tex(r"Granos Grandes ($> 1 \mu m$):\\Dominios piezoeléctricos alineados.", font_size=28).next_to(large_grains, DOWN, buff=0.5)
        
        self.play(FadeIn(large_grains), Write(txt1))
        self.wait(5)
        
        # Compara con nanogranos donde el desorden cancela la piezoelectricidad
        nanograins = create_grains(0.5, RIGHT*3, 43, is_nano=True)
        txt2 = Tex(r"Nanogranos ($< 100$ nm):", font_size=28, color=RED).next_to(nanograins, UP, buff=0.5)
        txt3 = Tex(r"En nanogranos, el desorden atómico\\en los bordes es dominante.\\Esto cancela los dipolos y se pierde\\la propiedad piezoeléctrica.", font_size=24, color=WHITE).next_to(nanograins, DOWN, buff=0.5)
        
        self.play(FadeIn(nanograins), Write(txt2))
        self.play(Write(txt3))
        self.wait(8)
        self.play(FadeOut(Group(*self.mobjects)))


# Escena para explicar la Difracción de Rayos X (XRD) mediante la Ley de Bragg
class Scene3_XRD_Bragg(Scene):
    def construct(self):
        title = Tex(r"La Física de la Difracción (Ley de Bragg)", font_size=40).to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Representa dos planos atómicos paralelos
        plane1 = VGroup(*[Dot(RIGHT*x + UP*0.5, radius=0.1, color=BLUE) for x in np.linspace(-3.5, 3.5, 12)])
        plane2 = VGroup(*[Dot(RIGHT*x + DOWN*0.5, radius=0.1, color=BLUE) for x in np.linspace(-3.5, 3.5, 12)])
        
        # Muestra la distancia interplanar 'd'
        d_line = DoubleArrow(plane1[5].get_center(), plane2[5].get_center(), buff=0.1, color=WHITE)
        d_lbl = MathTex("d", font_size=28).next_to(d_line, RIGHT, buff=0.1)
        self.play(FadeIn(plane1), FadeIn(plane2), Create(d_line), Write(d_lbl))
        
        # Define el ángulo de incidencia Theta
        theta = 30 * DEGREES
        p_top = plane1[4].get_center()
        p_bot = plane2[4].get_center()
        
        dir_in = np.array([np.cos(theta), -np.sin(theta), 0])
        dir_out = np.array([np.cos(theta), np.sin(theta), 0])
        
        # Dibuja los rayos incidentes y difractados
        ray1_in = Line(p_top - dir_in*4, p_top, color=YELLOW, stroke_width=4)
        ray1_out = Line(p_top, p_top + dir_out*4, color=YELLOW, stroke_width=4)
        
        ray2_in = Line(p_bot - dir_in*4, p_bot, color=RED, stroke_width=4)
        ray2_out = Line(p_bot, p_bot + dir_out*4, color=RED, stroke_width=4)
        
        self.play(Create(ray1_in), Create(ray2_in), run_time=2)
        self.play(Create(ray1_out), Create(ray2_out), run_time=2)
        
        # Calcula y resalta la diferencia de camino óptico (2 * d * sin(theta))
        n_in = np.array([np.sin(theta), np.cos(theta), 0])
        v = p_top - p_bot 
        perp_pt_in = p_bot + (np.dot(v, dir_in) * dir_in)
        perp_pt_out = p_bot + (np.dot(v, dir_out) * dir_out)
        
        line_perp_in = DashedLine(p_top, perp_pt_in, color=WHITE)
        line_perp_out = DashedLine(p_top, perp_pt_out, color=WHITE)
        
        path_in = Line(perp_pt_in, p_bot, color=GREEN, stroke_width=6)
        path_out = Line(p_bot, perp_pt_out, color=GREEN, stroke_width=6)
        lbl_in = MathTex(r"d \sin\theta", font_size=24, color=GREEN).next_to(path_in, DOWN, buff=0.1)
        lbl_out = MathTex(r"d \sin\theta", font_size=24, color=GREEN).next_to(path_out, DOWN, buff=0.1)

        self.play(Create(line_perp_in), Create(line_perp_out))
        self.play(Create(path_in), Create(path_out))
        self.play(Write(lbl_in), Write(lbl_out))
        self.wait(3)
        
        # Enuncia formalmente la Ley de Bragg
        txt_bragg = MathTex(r"\text{Ruta Extra Total } = 2d \sin\theta = n \lambda", font_size=36, color=GREEN).move_to(RIGHT*2 + DOWN*2)
        self.play(Write(txt_bragg))
        
        # Explica el eje 2-Theta usado en los difractogramas
        arc = Arc(radius=3, start_angle=0, angle=theta*2, color=WHITE).move_to(p_top, aligned_edge=LEFT).shift(RIGHT*0.5)
        trans_ray = DashedLine(p_top, p_top + dir_in*3, color=GRAY)
        diff_ray = Line(p_top, p_top + dir_out*3, color=YELLOW)
        arc_2theta = Angle(trans_ray, diff_ray, radius=1.5, color=WHITE)
        lbl_2theta = MathTex(r"2\theta", font_size=24).next_to(arc_2theta, RIGHT, buff=0.1)
        
        self.play(Create(trans_ray), Create(arc_2theta), Write(lbl_2theta))
        
        det_txt = Tex(r"Eje $2\theta = \text{Posición del Detector respecto al haz incidente}$", font_size=28).to_edge(DOWN, buff=0.5)
        self.play(Write(det_txt))
        self.wait(6)
        self.play(FadeOut(Group(*self.mobjects)))


# Escena para demostrar el cambio de fase Cúbica a Tetragonal y su impacto en XRD
class Scene4_CubicVsTetragonal(Scene):
    def construct(self):
        title = Tex(r"Índices de Miller y Splitting Tetragonal", font_size=40).to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Muestra la celda unitaria con los planos de Miller resaltados
        cell = PerovskiteCell()
        cell.show_miller = True
        cell.scale(1.2).shift(LEFT*3.5 + DOWN*0.5)
        
        t_tracker = ValueTracker(0) # 0 = Cúbico, 1 = Tetragonal
        angle_tracker = ValueTracker(30)
        cell.add_updater(lambda m, dt: m.update_cell(t_tracker.get_value(), angle_tracker.get_value(), offset=LEFT*3.5+DOWN*0.5))
        self.add(cell)
        
        # Crea los ejes para el difractograma (XRD pattern)
        axes = Axes(x_range=[44.5, 45.7, 0.3], y_range=[0, 1.2, 0.5], x_length=4.0, y_length=3.3, axis_config={"color":WHITE}, tips=False)
        axes.to_edge(RIGHT, buff=0.5).shift(DOWN*0.5)
        
        x_lbl = Tex(r"$2\theta$ ($^\circ$)", font_size=20).next_to(axes.x_axis, DOWN)
        y_lbl = Tex(r"Intensidad", font_size=20).rotate(PI/2).next_to(axes.y_axis, LEFT)
        lbl_448 = MathTex("44.8^\circ", font_size=16).next_to(axes.c2p(44.8, 0), DOWN)
        lbl_454 = MathTex("45.4^\circ", font_size=16).next_to(axes.c2p(45.4, 0), DOWN)
        
        self.play(Create(axes), Write(x_lbl), Write(y_lbl), Write(lbl_448), Write(lbl_454))
        
        # Función para simular el perfil de XRD con picos Gaussianos
        def xrd_profile(x, t):
            mu1 = 45.1 - 0.3 * t  # Posición del pico (002)
            mu2 = 45.1 + 0.3 * t  # Posición del pico (200)
            amp1 = 1.0 - 0.3 * t 
            amp2 = 0.0 + 1.1 * t  
            sig = 0.04 + 0.01*t   # Ancho del pico (FWHM)
            return amp1 * np.exp(-0.5 * ((x - mu1) / sig)**2) + amp2 * np.exp(-0.5 * ((x - mu2) / sig)**2)
            
        # Dibuja la curva de difracción dinámicamente
        curve = always_redraw(lambda: axes.plot(lambda x: xrd_profile(x, t_tracker.get_value()), color=YELLOW))
        self.add(curve)
        
        # Anima la transición de fase (distorsión estructural y desdoblamiento de picos)
        self.play(t_tracker.animate.set_value(1), angle_tracker.animate.increment_value(90), run_time=6, rate_func=smooth)
        self.wait(3)
        
        # Explica la relación física entre la distancia interplanar y el ángulo de difracción
        txt_bragg = Tex(r"Como $d_{002}$ es más grande, su ángulo $\theta$ es menor (Ley de Bragg).\\Por eso el pico (002) aparece a la izquierda.", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(Write(txt_bragg))
        
        # Identifica los picos resultantes en el espectro
        lbl_002 = Tex("(002)", font_size=18, color=BLUE).next_to(axes.c2p(44.8, 0.7), UP)
        lbl_200 = Tex("(200)", font_size=18, color=RED).next_to(axes.c2p(45.4, 1.1), UP)
        self.play(Write(lbl_002), Write(lbl_200))
        self.wait(8)
        self.play(FadeOut(Group(*self.mobjects)))


# Escena final de cierre con el resumen de la relación estructura-propiedad
class Scene5_Conclusion(Scene):
    def construct(self):
        title = Tex(r"Estructura $\rightarrow$ Función", font_size=42).to_edge(UP, buff=1.0)
        self.play(Write(title))
        
        # Muestra la celda tetragonal rotando
        cell = PerovskiteCell()
        angle_tracker = ValueTracker(0)
        cell.add_updater(lambda m, dt: m.update_cell(1.0, angle_tracker.get_value(), offset=LEFT*3 + DOWN*0.5))
        cell.add_updater(lambda m, dt: angle_tracker.increment_value(dt * 30))
        self.add(cell)
        
        # Lista los puntos clave de la investigación
        points = VGroup(
            Tex(r"Titanio desplazado crea un Dipolo Eléctrico local.", font_size=32, color=YELLOW),
            Tex(r"SEM: Valida granos grandes para evitar caos estructural.", font_size=32, color=WHITE),
            Tex(r"XRD: Confirma formación de simetría tetragonal.", font_size=32, color=BLUE)
        ).arrange(DOWN, aligned_edge=LEFT, buff=1.0).next_to(cell, RIGHT, buff=2.0)
        
        for pt in points:
            self.play(FadeIn(pt, shift=LEFT))
            self.wait(4)
            
        self.wait(6)
        # Fin de la animación
