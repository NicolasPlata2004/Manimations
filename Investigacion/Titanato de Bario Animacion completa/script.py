from manim import *
import numpy as np
from scipy.spatial.transform import Rotation

config.background_color = "#000000"

def project_iso(x, y, z, phi_deg=65, theta_deg=15, rot_z_deg=0):
    rz1 = Rotation.from_euler('z', np.radians(rot_z_deg)).as_matrix()
    rx = Rotation.from_euler('x', np.radians(phi_deg)).as_matrix()
    rz2 = Rotation.from_euler('z', np.radians(theta_deg)).as_matrix()
    pt = rx.dot(rz2.dot(rz1.dot([x, y, z])))
    return np.array([pt[0], pt[1], 0]), pt[2]

class PerovskiteCell(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ba_atoms = [Dot(radius=0.15, color=BLUE).set_z_index(3) for _ in range(8)]
        self.o_atoms = [Dot(radius=0.1, color=RED).set_z_index(3) for _ in range(6)]
        self.ti_atom = Dot(radius=0.12, color=YELLOW).set_z_index(3)
        self.edges = [Line(ORIGIN, UP, color=WHITE, stroke_width=2).set_z_index(2) for _ in range(12)]
        
        self.dim_a_line = Line(ORIGIN, UP, color=WHITE, stroke_width=2).set_z_index(4)
        self.dim_b_line = Line(ORIGIN, UP, color=WHITE, stroke_width=2).set_z_index(4)
        self.dim_c_line = Line(ORIGIN, UP, color=WHITE, stroke_width=2).set_z_index(4)
        self.lbl_a = MathTex("a", font_size=24, color=WHITE).set_z_index(4)
        self.lbl_b = MathTex("b", font_size=24, color=WHITE).set_z_index(4)
        self.lbl_c = MathTex("c", font_size=24, color=WHITE).set_z_index(4)
        
        self.arc_alpha = Arc(radius=0.3, angle=PI/2, color=WHITE).set_z_index(4)
        self.arc_beta = Arc(radius=0.3, angle=PI/2, color=WHITE).set_z_index(4)
        self.arc_gamma = Arc(radius=0.3, angle=PI/2, color=WHITE).set_z_index(4)
        self.lbl_alpha = MathTex(r"\alpha=90^\circ", font_size=16, color=WHITE).set_z_index(4)
        self.lbl_beta = MathTex(r"\beta=90^\circ", font_size=16, color=WHITE).set_z_index(4)
        self.lbl_gamma = MathTex(r"\gamma=90^\circ", font_size=16, color=WHITE).set_z_index(4)
        
        self.miller_002 = Polygon(ORIGIN, UP, RIGHT, DOWN, color=BLUE, fill_opacity=0.4, stroke_width=0).set_z_index(1)
        self.miller_200 = Polygon(ORIGIN, UP, RIGHT, DOWN, color=RED, fill_opacity=0.4, stroke_width=0).set_z_index(1)
        self.d002_arrow = DoubleArrow(ORIGIN, UP, color=BLUE, buff=0, max_tip_length_to_length_ratio=0.1).set_z_index(4)
        self.d200_arrow = DoubleArrow(ORIGIN, UP, color=RED, buff=0, max_tip_length_to_length_ratio=0.1).set_z_index(4)
        self.lbl_d002 = MathTex(r"d_{002}", font_size=20, color=BLUE).set_z_index(4)
        self.lbl_d200 = MathTex(r"d_{200}", font_size=20, color=RED).set_z_index(4)

        self.add(*self.edges, *self.ba_atoms, *self.o_atoms, self.ti_atom)
        self.show_dimensions = False
        self.show_miller = False

    def update_cell(self, t_val, rot_angle, offset=ORIGIN):
        a = 2.0 - 0.1 * t_val
        b = a
        c = 2.0 + 0.5 * t_val
        
        corners = [
            [-a/2, -b/2, -c/2], [a/2, -b/2, -c/2], [a/2, b/2, -c/2], [-a/2, b/2, -c/2],
            [-a/2, -b/2, c/2],  [a/2, -b/2, c/2],  [a/2, b/2, c/2],  [-a/2, b/2, c/2]
        ]
        faces = [
            [0, 0, c/2], [0, 0, -c/2],
            [a/2, 0, 0], [-a/2, 0, 0],
            [0, b/2, 0], [0, -b/2, 0]
        ]
        ti_coord = [0, 0, 0.4 * t_val]
        
        z_map = {}
        def set_pos(mob, coord):
            pt, z = project_iso(*coord, rot_z_deg=rot_angle)
            mob.move_to(pt + offset)
            z_map[mob] = z
            return pt + offset
            
        points_corners = [set_pos(self.ba_atoms[i], corners[i]) for i in range(8)]
        for i, coord in enumerate(faces): set_pos(self.o_atoms[i], coord)
        set_pos(self.ti_atom, ti_coord)
        
        edge_pairs = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        for i, (i1, i2) in enumerate(edge_pairs):
            self.edges[i].put_start_and_end_on(points_corners[i1], points_corners[i2])
            z_map[self.edges[i]] = (z_map[self.ba_atoms[i1]] + z_map[self.ba_atoms[i2]]) / 2
            
        sortable = self.edges + self.ba_atoms + self.o_atoms + [self.ti_atom]
        extras = []
        
        if self.show_dimensions:
            pa0, _ = project_iso(corners[0][0], corners[0][1], corners[0][2], rot_z_deg=rot_angle)
            pa1, _ = project_iso(corners[1][0], corners[1][1], corners[1][2], rot_z_deg=rot_angle)
            self.dim_a_line.put_start_and_end_on(pa0 + offset, pa1 + offset)
            self.lbl_a.move_to((pa0+pa1)/2 + offset + DOWN*0.3)
            
            pb1, _ = project_iso(corners[3][0], corners[3][1], corners[3][2], rot_z_deg=rot_angle)
            self.dim_b_line.put_start_and_end_on(pa0 + offset, pb1 + offset)
            self.lbl_b.move_to((pa0+pb1)/2 + offset + RIGHT*0.3)
            
            pc4, _ = project_iso(corners[4][0], corners[4][1], corners[4][2], rot_z_deg=rot_angle)
            self.dim_c_line.put_start_and_end_on(pa0 + offset, pc4 + offset)
            self.lbl_c.move_to((pa0+pc4)/2 + offset + LEFT*0.3)
            
            def draw_arc(o, v1, v2, radius=0.4):
                u = v1 - o
                v = v2 - o
                a1 = np.arctan2(u[1], u[0])
                a2 = np.arctan2(v[1], v[0])
                diff = (a2 - a1) % TAU
                if diff > PI: diff -= TAU
                elif diff < -PI: diff += TAU
                return Arc(radius=radius, start_angle=a1, angle=diff, arc_center=o+offset, color=WHITE)
            
            self.arc_gamma.become(draw_arc(pa0, pa1, pb1))
            self.lbl_gamma.move_to(pa0 + offset + (pa1-pa0)*0.3 + (pb1-pa0)*0.3)
            
            self.arc_beta.become(draw_arc(pa0, pa1, pc4))
            self.lbl_beta.move_to(pa0 + offset + (pa1-pa0)*0.3 + (pc4-pa0)*0.3)
            
            self.arc_alpha.become(draw_arc(pa0, pb1, pc4))
            self.lbl_alpha.move_to(pa0 + offset + (pb1-pa0)*0.3 + (pc4-pa0)*0.3)
            
            extras.extend([self.dim_a_line, self.dim_b_line, self.dim_c_line, self.lbl_a, self.lbl_b, self.lbl_c, self.arc_gamma, self.lbl_gamma, self.arc_beta, self.lbl_beta, self.arc_alpha, self.lbl_alpha])
            
        if self.show_miller:
            m002_corn = [[-a/2, -b/2, 0], [a/2, -b/2, 0], [a/2, b/2, 0], [-a/2, b/2, 0]]
            m200_corn = [[0, -b/2, -c/2], [0, b/2, -c/2], [0, b/2, c/2], [0, -b/2, c/2]]
            
            pts_002 = [project_iso(*p, rot_z_deg=rot_angle)[0] + offset for p in m002_corn]
            pts_200 = [project_iso(*p, rot_z_deg=rot_angle)[0] + offset for p in m200_corn]
            
            self.miller_002.set_points_as_corners(pts_002).set_color(BLUE).set_fill(BLUE, 0.4)
            self.miller_200.set_points_as_corners(pts_200).set_color(RED).set_fill(RED, 0.4)
            z_map[self.miller_002] = 0 
            z_map[self.miller_200] = 0
            
            p_center = project_iso(0,0,0, rot_z_deg=rot_angle)[0] + offset
            p_top = project_iso(0,0,c/2, rot_z_deg=rot_angle)[0] + offset
            p_right = project_iso(a/2,0,0, rot_z_deg=rot_angle)[0] + offset
            
            self.d002_arrow.put_start_and_end_on(p_center, p_top)
            self.d200_arrow.put_start_and_end_on(p_center, p_right)
            self.lbl_d002.next_to(self.d002_arrow, RIGHT, buff=0.1)
            self.lbl_d200.next_to(self.d200_arrow, UP, buff=0.1)
            
            extras.extend([self.miller_002, self.miller_200, self.d002_arrow, self.d200_arrow, self.lbl_d002, self.lbl_d200])

        sortable.sort(key=lambda m: z_map.get(m, 0), reverse=True) 
        self.submobjects = sortable + extras


class Scene1_UnitCell(Scene):
    def construct(self):
        txt1 = Tex(r"El Titanato de Bario ($BaTiO_3$) es un material cristalino.", font_size=36).to_edge(UP, buff=1.0)
        self.play(Write(txt1), run_time=2)
        self.wait(2)
        txt2 = Tex(r"Su estructura básica se repite millones de veces.", font_size=36).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt2))
        self.wait(2)

        cell = PerovskiteCell()
        cell.scale(1.5).shift(DOWN*0.5)
        angle_tracker = ValueTracker(20)
        cell.add_updater(lambda m, dt: m.update_cell(0, angle_tracker.get_value(), DOWN*0.5))
        
        self.play(FadeIn(cell))
        self.play(angle_tracker.animate.increment_value(90), run_time=4)
        
        txt_ba = Tex(r"Bario (Ba): Esquinas", font_size=28, color=BLUE).to_edge(LEFT, buff=1.0).shift(UP*1)
        txt_o = Tex(r"Oxígeno (O): Caras", font_size=28, color=RED).next_to(txt_ba, DOWN, aligned_edge=LEFT, buff=0.5)
        txt_ti = Tex(r"Titanio (Ti): Centro", font_size=28, color=YELLOW).next_to(txt_o, DOWN, aligned_edge=LEFT, buff=0.5)
        
        self.play(Write(txt_ba))
        self.play(Write(txt_o))
        self.play(Write(txt_ti))
        self.wait(3)
        
        txt_sym = MathTex(r"\text{Alta simetría perfecta: } a = b = c \text{ y } \alpha = \beta = \gamma = 90^\circ", font_size=36).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt_sym))
        
        cell.show_dimensions = True
        self.wait(5)
        self.play(FadeOut(Group(*self.mobjects)))


class Scene2_SEM(Scene):
    def construct(self):
        title = Tex(r"Análisis Microestructural (SEM)", font_size=40).to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        def create_grains(scale, offset, seed, is_nano=False):
            np.random.seed(seed)
            polys = VGroup()
            arrows = VGroup()
            points = VGroup()
            for dx in range(3):
                for dy in range(3):
                    pts = [
                        [dx+np.random.rand()*0.8, dy+np.random.rand()*0.8, 0],
                        [dx+1+np.random.rand()*0.8, dy+np.random.rand()*0.8, 0],
                        [dx+0.5+np.random.rand()*0.8, dy+1+np.random.rand()*0.8, 0],
                        [dx-0.5+np.random.rand()*0.8, dy+0.5+np.random.rand()*0.8, 0]
                    ]
                    polys.add(Polygon(*pts, stroke_width=2, color=WHITE, fill_opacity=0.1))
                    
                    if not is_nano:
                        arrows.add(Vector(RIGHT*0.6 + UP*0.2, color=YELLOW).move_to(polys[-1].get_center()))
                    else:
                        for p in pts:
                            for _ in range(3):
                                points.add(Dot(np.array(p) + (np.random.rand(3)-0.5)*0.3, radius=0.03, color=RED))
            return VGroup(polys, arrows, points).scale(scale).move_to(offset)

        large_grains = create_grains(1.2, LEFT*3, 42, is_nano=False)
        txt1 = Tex(r"Granos Grandes ($> 1 \mu m$):\\Dominios piezoeléctricos alineados.", font_size=28).next_to(large_grains, DOWN, buff=0.5)
        
        self.play(FadeIn(large_grains), Write(txt1))
        self.wait(5)
        
        nanograins = create_grains(0.5, RIGHT*3, 43, is_nano=True)
        txt2 = Tex(r"Nanogranos ($< 100$ nm):", font_size=28, color=RED).next_to(nanograins, UP, buff=0.5)
        txt3 = Tex(r"En nanogranos, el desorden atómico\\en los bordes es dominante.\\Esto cancela los dipolos y se pierde\\la propiedad piezoeléctrica.", font_size=24, color=WHITE).next_to(nanograins, DOWN, buff=0.5)
        
        self.play(FadeIn(nanograins), Write(txt2))
        self.play(Write(txt3))
        self.wait(8)
        self.play(FadeOut(Group(*self.mobjects)))


class Scene3_XRD_Bragg(Scene):
    def construct(self):
        title = Tex(r"La Física de la Difracción (Ley de Bragg)", font_size=40).to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        plane1 = VGroup(*[Dot(RIGHT*x + UP*0.5, radius=0.1, color=BLUE) for x in np.linspace(-3.5, 3.5, 12)])
        plane2 = VGroup(*[Dot(RIGHT*x + DOWN*0.5, radius=0.1, color=BLUE) for x in np.linspace(-3.5, 3.5, 12)])
        
        d_line = DoubleArrow(plane1[5].get_center(), plane2[5].get_center(), buff=0.1, color=WHITE)
        d_lbl = MathTex("d", font_size=28).next_to(d_line, RIGHT, buff=0.1)
        self.play(FadeIn(plane1), FadeIn(plane2), Create(d_line), Write(d_lbl))
        
        theta = 30 * DEGREES
        p_top = plane1[4].get_center()
        p_bot = plane2[4].get_center()
        
        dir_in = np.array([np.cos(theta), -np.sin(theta), 0])
        dir_out = np.array([np.cos(theta), np.sin(theta), 0])
        
        ray1_in = Line(p_top - dir_in*4, p_top, color=YELLOW, stroke_width=4)
        ray1_out = Line(p_top, p_top + dir_out*4, color=YELLOW, stroke_width=4)
        
        ray2_in = Line(p_bot - dir_in*4, p_bot, color=RED, stroke_width=4)
        ray2_out = Line(p_bot, p_bot + dir_out*4, color=RED, stroke_width=4)
        
        self.play(Create(ray1_in), Create(ray2_in), run_time=2)
        self.play(Create(ray1_out), Create(ray2_out), run_time=2)
        
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
        
        txt_bragg = MathTex(r"\text{Ruta Extra Total } = 2d \sin\theta = n \lambda", font_size=36, color=GREEN).move_to(RIGHT*2 + DOWN*2)
        self.play(Write(txt_bragg))
        
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


class Scene4_CubicVsTetragonal(Scene):
    def construct(self):
        title = Tex(r"Índices de Miller y Splitting Tetragonal", font_size=40).to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        cell = PerovskiteCell()
        cell.show_miller = True
        cell.scale(1.2).shift(LEFT*3.5 + DOWN*0.5)
        
        t_tracker = ValueTracker(0)
        angle_tracker = ValueTracker(30)
        cell.add_updater(lambda m, dt: m.update_cell(t_tracker.get_value(), angle_tracker.get_value(), offset=LEFT*3.5+DOWN*0.5))
        self.add(cell)
        
        axes = Axes(x_range=[44.5, 45.7, 0.3], y_range=[0, 1.2, 0.5], x_length=4.0, y_length=3.3, axis_config={"color":WHITE}, tips=False)
        axes.to_edge(RIGHT, buff=0.5).shift(DOWN*0.5)
        
        x_lbl = Tex(r"$2\theta$ ($^\circ$)", font_size=20).next_to(axes.x_axis, DOWN)
        y_lbl = Tex(r"Intensidad", font_size=20).rotate(PI/2).next_to(axes.y_axis, LEFT)
        lbl_448 = MathTex("44.8^\circ", font_size=16).next_to(axes.c2p(44.8, 0), DOWN)
        lbl_454 = MathTex("45.4^\circ", font_size=16).next_to(axes.c2p(45.4, 0), DOWN)
        
        self.play(Create(axes), Write(x_lbl), Write(y_lbl), Write(lbl_448), Write(lbl_454))
        
        def xrd_profile(x, t):
            mu1 = 45.1 - 0.3 * t
            mu2 = 45.1 + 0.3 * t
            amp1 = 1.0 - 0.3 * t 
            amp2 = 0.0 + 1.1 * t  
            sig = 0.04 + 0.01*t
            return amp1 * np.exp(-0.5 * ((x - mu1) / sig)**2) + amp2 * np.exp(-0.5 * ((x - mu2) / sig)**2)
            
        curve = always_redraw(lambda: axes.plot(lambda x: xrd_profile(x, t_tracker.get_value()), color=YELLOW))
        self.add(curve)
        
        self.play(t_tracker.animate.set_value(1), angle_tracker.animate.increment_value(90), run_time=6, rate_func=smooth)
        self.wait(3)
        
        txt_bragg = Tex(r"Como $d_{002}$ es más grande, su ángulo $\theta$ es menor (Ley de Bragg).\\Por eso el pico (002) aparece a la izquierda.", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(Write(txt_bragg))
        
        lbl_002 = Tex("(002)", font_size=18, color=BLUE).next_to(axes.c2p(44.8, 0.7), UP)
        lbl_200 = Tex("(200)", font_size=18, color=RED).next_to(axes.c2p(45.4, 1.1), UP)
        self.play(Write(lbl_002), Write(lbl_200))
        self.wait(8)
        self.play(FadeOut(Group(*self.mobjects)))


class Scene5_Conclusion(Scene):
    def construct(self):
        title = Tex(r"Estructura $\rightarrow$ Función", font_size=42).to_edge(UP, buff=1.0)
        self.play(Write(title))
        
        cell = PerovskiteCell()
        angle_tracker = ValueTracker(0)
        cell.add_updater(lambda m, dt: m.update_cell(1.0, angle_tracker.get_value(), offset=LEFT*3 + DOWN*0.5))
        cell.add_updater(lambda m, dt: angle_tracker.increment_value(dt * 30))
        self.add(cell)
        
        points = VGroup(
            Tex(r"Titanio desplazado crea un Dipolo Eléctrico local.", font_size=32, color=YELLOW),
            Tex(r"SEM: Valida granos grandes para evitar caos estructural.", font_size=32, color=WHITE),
            Tex(r"XRD: Confirma formación de simetría tetragonal.", font_size=32, color=BLUE)
        ).arrange(DOWN, aligned_edge=LEFT, buff=1.0).next_to(cell, RIGHT, buff=2.0)
        
        for pt in points:
            self.play(FadeIn(pt, shift=LEFT))
            self.wait(4)
            
        self.wait(6)
