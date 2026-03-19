from manim import *
import numpy as np
from scipy.spatial.transform import Rotation

config.background_color = "#0B0F1A"

def project_iso(x, y, z, phi_deg=65, theta_deg=15, rot_z_deg=0):
    rz1 = Rotation.from_euler('z', np.radians(rot_z_deg)).as_matrix()
    rx = Rotation.from_euler('x', np.radians(phi_deg)).as_matrix()
    rz2 = Rotation.from_euler('z', np.radians(theta_deg)).as_matrix()
    pt = rx.dot(rz2.dot(rz1.dot([x, y, z])))
    return np.array([pt[0], pt[1], 0]), pt[2]

class PerovskiteCell(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ba_atoms = [Dot(radius=0.15, color=BLUE) for _ in range(8)]
        self.o_atoms = [Dot(radius=0.1, color=RED) for _ in range(6)]
        self.ti_atom = Dot(radius=0.12, color=YELLOW)
        self.edges = [Line(ORIGIN, UP, color=WHITE, stroke_width=2) for _ in range(12)]
        
        self.dim_a_line = DoubleArrow(ORIGIN, UP, color=WHITE, stroke_width=3, buff=0, max_tip_length_to_length_ratio=0.2)
        self.dim_c_line = DoubleArrow(ORIGIN, UP, color=WHITE, stroke_width=3, buff=0, max_tip_length_to_length_ratio=0.2)
        self.lbl_a = MathTex("a", font_size=24, color=WHITE)
        self.lbl_c = MathTex("c", font_size=24, color=WHITE)
        
        self.add(*self.edges, *self.ba_atoms, *self.o_atoms, self.ti_atom)
        self.show_dimensions = False
        
    def show_dims(self):
        self.add(self.dim_a_line, self.dim_c_line, self.lbl_a, self.lbl_c)
        self.show_dimensions = True
        
    def hide_dims(self):
        self.remove(self.dim_a_line, self.dim_c_line, self.lbl_a, self.lbl_c)
        self.show_dimensions = False

    def update_cell(self, t_val, rot_angle, offset=ORIGIN):
        a = 2.0 - 0.1 * t_val
        c = 2.0 + 0.5 * t_val
        
        corners = [
            [-a/2, -a/2, -c/2], [a/2, -a/2, -c/2], [a/2, a/2, -c/2], [-a/2, a/2, -c/2],
            [-a/2, -a/2, c/2],  [a/2, -a/2, c/2],  [a/2, a/2, c/2],  [-a/2, a/2, c/2]
        ]
        faces = [[0, 0, c/2], [0, 0, -c/2], [a/2, 0, 0], [-a/2, 0, 0], [0, a/2, 0], [0, -a/2, 0]]
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
        sortable.sort(key=lambda m: z_map.get(m, 0), reverse=True) 
        
        if self.show_dimensions:
            pa0, _ = project_iso(corners[0][0], corners[0][1] - 0.4, corners[0][2], rot_z_deg=rot_angle)
            pa1, _ = project_iso(corners[1][0], corners[1][1] - 0.4, corners[1][2], rot_z_deg=rot_angle)
            self.dim_a_line.put_start_and_end_on(pa0 + offset, pa1 + offset)
            self.lbl_a.move_to((pa0+pa1)/2 + offset + DOWN*0.25)
            
            pc0, _ = project_iso(corners[0][0] - 0.4, corners[0][1], corners[0][2], rot_z_deg=rot_angle)
            pc4, _ = project_iso(corners[4][0] - 0.4, corners[4][1], corners[4][2], rot_z_deg=rot_angle)
            self.dim_c_line.put_start_and_end_on(pc0 + offset, pc4 + offset)
            self.lbl_c.move_to((pc0+pc4)/2 + offset + LEFT*0.35)
            self.submobjects = sortable + [self.dim_a_line, self.dim_c_line, self.lbl_a, self.lbl_c]
        else:
            self.submobjects = sortable


class Scene1_UnitCell(Scene):
    def construct(self):
        txt1 = Text("El Titanato de Bario (BaTiO3) es un material cristalino.", font_size=32).to_edge(UP, buff=1.0)
        self.play(Write(txt1), run_time=2)
        self.wait(3)
        
        txt2 = Text("Su estructura básica se repite millones de veces.", font_size=32).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt2), run_time=1.5)
        self.wait(3)

        grid = VGroup()
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    pt, depth = project_iso((x-1)*1.5, (y-1)*1.5, (z-1)*1.5, rot_z_deg=45)
                    d = Dot(pt, radius=0.08, color=BLUE)
                    d.depth = depth
                    grid.add(d)
        
        grid.submobjects.sort(key=lambda m: m.depth, reverse=True)
        self.play(FadeIn(grid, shift=UP), run_time=2.5)
        self.wait(2.5)

        self.play(grid.animate.scale(2).set_opacity(0), run_time=2.5)
        
        txt3 = Text("Estructura Cúbica (T > 120°C).", font_size=32).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt3))

        cell = PerovskiteCell()
        cell.update_cell(0, 45, ORIGIN)
        
        self.play(*[Create(e) for e in cell.edges], run_time=2)
        
        txt_ba = Text("Bario (Ba): Esquinas", font_size=24, color=BLUE).to_edge(LEFT, buff=1).shift(UP*1)
        self.play(Write(txt_ba), *[FadeIn(a, scale=0) for a in cell.ba_atoms])
        self.wait(2.5)
        
        txt_o = Text("Oxígeno (O): Caras", font_size=24, color=RED).next_to(txt_ba, DOWN, aligned_edge=LEFT, buff=0.5)
        self.play(Write(txt_o), *[FadeIn(a, scale=0) for a in cell.o_atoms])
        self.wait(2.5)

        txt_ti = Text("Titanio (Ti): Centro", font_size=24, color=YELLOW).next_to(txt_o, DOWN, aligned_edge=LEFT, buff=0.5)
        self.play(Write(txt_ti), FadeIn(cell.ti_atom, scale=0))
        self.wait(3.5)

        txt4 = MathTex(r"\text{Alta simetría perfecta: } a=b=c \text{ y } \alpha=\beta=\gamma=90^\circ", font_size=32).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt4))
        
        cell.show_dims()
        cell.update_cell(0, 45, ORIGIN)
        self.play(FadeIn(cell.dim_a_line), FadeIn(cell.dim_c_line), Write(cell.lbl_a), Write(cell.lbl_c))
        self.wait(3)
        
        angle_tracker = ValueTracker(45)
        cell.add_updater(lambda m, dt: m.update_cell(0, angle_tracker.get_value(), ORIGIN))
        self.play(angle_tracker.animate.increment_value(90), run_time=5, rate_func=linear)
        self.wait(3)
        self.play(FadeOut(Group(*self.mobjects)))


class Scene2_SEM(Scene):
    def construct(self):
        txt1 = Text("SEM valida la microestructura (tamaño de grano).", font_size=32).to_edge(UP, buff=1.0)
        self.play(Write(txt1))
        self.wait(3)
        
        try:
            sem_img = ImageMobject("sem_nano.jpg")
            sem_img.height = 4
            sem_img.to_edge(RIGHT, buff=1).shift(DOWN*0.5)
            self.play(FadeIn(sem_img))
        except:
            sem_img = Rectangle(width=4, height=4, color=GRAY, fill_opacity=0.2).to_edge(RIGHT, buff=1).shift(DOWN*0.5)
            sem_txt = Text("sem_nano.jpg", font_size=20).move_to(sem_img)
            sem_group = VGroup(sem_img, sem_txt)
            self.play(FadeIn(sem_group))
            sem_img = sem_group
        
        axes_sem = Axes(x_range=[0,5,1], y_range=[0,5,1], x_length=4, y_length=4, axis_config={"color":WHITE}, tips=False)
        axes_sem.to_edge(LEFT, buff=1).shift(DOWN*0.5)
        x_lbl = Text("Microscopía e-", font_size=20).next_to(axes_sem.x_axis, DOWN)
        y_lbl = Text("Área analizada", font_size=20).rotate(PI/2).next_to(axes_sem.y_axis, LEFT)
        self.play(Create(axes_sem), Write(x_lbl), Write(y_lbl))
        self.wait(3.5)

        txt2 = Text("Buscamos granos grandes (> 1.2μm)...", font_size=32).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt2), Flash(sem_img, color=YELLOW, flash_radius=2))
        self.wait(4)

        txt3 = Text("...para asegurar el orden atómico de largo alcance.", font_size=32).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt3))
        self.wait(4.5)

        txt4 = Text("Nanogranos (< 100 nm) = Desorden Atómico.", font_size=32, color=RED).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt4))
        
        grid_left = VGroup(*[Dot(axes_sem.c2p(x,y), radius=0.08, color=BLUE) for x in np.linspace(0.5, 2.5, 4) for y in np.linspace(0.5, 4.5, 8)])
        grid_right = VGroup(*[Dot(axes_sem.c2p(x,y), radius=0.08, color=RED) for x in np.linspace(3.0, 4.5, 3) for y in np.linspace(0.5, 4.5, 8)])
        grid_right.rotate(25*DEGREES, about_point=axes_sem.c2p(3, 2.5))
        
        self.play(FadeIn(grid_left, shift=RIGHT), FadeIn(grid_right, shift=LEFT))
        
        border_txt = Text("Átomos en bordes de grano desalineados cancelan el dipolo.", font_size=22, color=YELLOW).next_to(axes_sem, DOWN, buff=0.8)
        self.play(Write(border_txt))
        self.wait(6)
        self.play(FadeOut(Group(*self.mobjects)))


class Scene3_XRD_Bragg(Scene):
    def construct(self):
        txt1 = Text("XRD mide la distancia entre planos atómicos.", font_size=32).to_edge(UP, buff=1.0)
        self.play(Write(txt1))
        
        plane1 = VGroup(*[Dot(color=BLUE, radius=0.15).move_to(RIGHT*x + UP*0.5) for x in np.linspace(-3.5, 3.5, 12)])
        plane2 = VGroup(*[Dot(color=BLUE, radius=0.15).move_to(RIGHT*x + DOWN*0.5) for x in np.linspace(-3.5, 3.5, 12)])
        
        d_arrow = DoubleArrow(plane2[5].get_center(), plane1[5].get_center(), buff=0.1, color=YELLOW)
        d_lbl = MathTex("d", font_size=32, color=YELLOW).next_to(d_arrow, RIGHT)
        
        self.play(FadeIn(plane1), FadeIn(plane2))
        self.play(Create(d_arrow), Write(d_lbl))
        self.wait(3.5)

        txt2 = MathTex(r"\text{Ley de Bragg: } n\lambda = 2d \sin\theta", font_size=36, color=YELLOW).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt2))
        self.wait(2)
        
        r1_start = LEFT*4 + UP*3
        r1_mid = plane1[4].get_center()
        r1_end = RIGHT*4 + UP*3
        
        wave1_in = FunctionGraph(lambda x: 0.15*np.sin(6*x), x_range=[-2.5, 2.5], color=RED)
        wave1_in.rotate(Line(r1_start, r1_mid).get_angle())
        wave1_in.move_to((r1_start+r1_mid)/2)
        
        wave1_out = FunctionGraph(lambda x: 0.15*np.sin(6*x), x_range=[-2.5, 2.5], color=RED)
        wave1_out.rotate(Line(r1_mid, r1_end).get_angle())
        wave1_out.move_to((r1_mid+r1_end)/2)

        self.play(Create(wave1_in), run_time=2)
        self.play(Create(wave1_out), run_time=2)
        self.wait(3)
        
        arc = Arc(radius=3.5, angle=PI/2, start_angle=0, color=WHITE).shift(plane1[5].get_center())
        detector = Rectangle(width=0.4, height=0.6, color=WHITE, fill_opacity=1).move_to(arc.point_from_proportion(0))
        
        txt3 = Text("Detector esférico mide la desviación total.", font_size=32).to_edge(UP, buff=1.0)
        self.play(Transform(txt1, txt3), Create(arc), FadeIn(detector))
        
        self.play(MoveAlongPath(detector, arc), run_time=4, rate_func=there_and_back)
        self.wait(2.5)
        
        txt4 = MathTex(r"\text{Eje } 2\theta = \text{Posición del Detector}", font_size=32, color=YELLOW).next_to(arc, RIGHT)
        self.play(Write(txt4))
        self.wait(5)
        self.play(FadeOut(Group(*self.mobjects)))


class Scene4_CubicVsTetragonal(Scene):
    def construct(self):
        txt1 = Text("Fase Cúbica (a=c): Planos (200) y (002) son idénticos.", font_size=30).to_edge(UP, buff=0.6)
        txt2 = Text("Resultado XRD: Pico Único (200).", font_size=30, color=YELLOW).next_to(txt1, DOWN)
        self.play(Write(txt1), Write(txt2))
        self.wait(3.5)
        
        axes = Axes(x_range=[44, 46, 0.5], y_range=[0, 1.6, 0.5], x_length=4.0, y_length=3.3, axis_config={"color":WHITE}, tips=False)
        axes.to_edge(RIGHT, buff=0.8).shift(DOWN*0.5)
        
        x_label = Text("2-Theta", font_size=18).next_to(axes.x_axis, DOWN)
        y_label = Text("Intensidad", font_size=18).rotate(PI/2).next_to(axes.y_axis, LEFT)
        self.add(x_label, y_label)
        
        t_tracker = ValueTracker(0)
        
        def xrd_profile(x, t):
            mu1 = 45.15 - 0.25 * t
            mu2 = 45.15 + 0.25 * t
            amp1 = 1.0 - 0.3 * t 
            amp2 = 0.0 + 1.1 * t  
            sig = 0.06 + 0.02*t
            return amp1 * np.exp(-0.5 * ((x - mu1) / sig)**2) + amp2 * np.exp(-0.5 * ((x - mu2) / sig)**2)
            
        curve = always_redraw(lambda: axes.plot(lambda x: xrd_profile(x, t_tracker.get_value()), color=WHITE))
        
        cell = PerovskiteCell()
        cell.show_dims()
        angle_tracker = ValueTracker(20) 
        cell.add_updater(lambda m, dt: m.update_cell(t_tracker.get_value(), angle_tracker.get_value(), offset=LEFT*3 + DOWN))
        
        self.add(axes, curve, cell)
        self.wait(5)
        
        txt3 = VGroup(
            Text("Transformación al enfriar (<120°C).", font_size=28),
            Text("Fase Tetragonal: Celda se estira (c > a).", font_size=28, color=YELLOW)
        ).arrange(DOWN).move_to(txt1.get_center())
        
        self.play(FadeOut(txt1), FadeOut(txt2), FadeIn(txt3))
        
        self.play(
            t_tracker.animate.set_value(1), 
            angle_tracker.animate.increment_value(90), 
            run_time=8, rate_func=smooth
        )
        self.wait(4)
        
        txt4 = VGroup(
            Text("Planos (002) se hacen más distantes (d_002 ↑).", font_size=26),
            MathTex(r"\text{Distancia mayor } (d \uparrow) \rightarrow \text{ Ángulo en gráfica menor } (2\theta \downarrow)", font_size=26, color=RED)
        ).arrange(DOWN).move_to(txt3.get_center())
        
        self.play(FadeOut(txt3), FadeIn(txt4))
        
        peak_002_line = DashedLine(axes.c2p(44.9, 0), axes.c2p(44.9, 0.7), color=YELLOW)
        peak_200_line = DashedLine(axes.c2p(45.4, 0), axes.c2p(45.4, 1.1), color=YELLOW)
        lbl_002 = Text("(002)", font_size=16, color=YELLOW).next_to(peak_002_line, UP)
        lbl_200 = Text("(200)", font_size=16, color=YELLOW).next_to(peak_200_line, UP)
        
        self.play(Create(peak_002_line), Create(peak_200_line), Write(lbl_002), Write(lbl_200))
        self.wait(5.5)
        
        txt_final = Text("El 'Splitting' de picos confirma la distorsión tetragonal estructural.", font_size=28, color=GREEN).next_to(txt4, DOWN, buff=0.5)
        self.play(Write(txt_final))
        self.wait(7)
        self.play(FadeOut(Group(*self.mobjects)))


class Scene5_Conclusion(Scene):
    def construct(self):
        title = Text("Titanato de Bario: Estructura → Función", font_size=36, weight=BOLD).to_edge(UP, buff=1.0)
        self.play(Write(title))
        self.wait(2)
        
        cell = PerovskiteCell()
        cell.show_dims()
        angle_tracker = ValueTracker(0)
        cell.add_updater(lambda m, dt: m.update_cell(1.0, angle_tracker.get_value(), offset=LEFT*3 + DOWN*0.5))
        
        def cell_updater(m, dt):
            angle_tracker.increment_value(dt * 30)
            m.update_cell(1.0, angle_tracker.get_value(), offset=LEFT*3 + DOWN*0.5)
            
        cell.add_updater(cell_updater)
        self.add(cell)
        
        text1 = Text("1. Titanio desplazado crea un Dipolo Eléctrico local.", font_size=26, color=YELLOW)
        text2 = Text("2. SEM: Valida granos grandes para evitar caos.", font_size=26, color=WHITE)
        text3 = Text("3. XRD: Confirma formación de simetría tetragonal.", font_size=26, color=RED)
        
        group = VGroup(text1, text2, text3).arrange(DOWN, aligned_edge=LEFT, buff=1.0).to_edge(RIGHT, buff=1.0).shift(DOWN*0.5+LEFT*0.5)
        
        self.play(FadeIn(text1, shift=UP))
        self.wait(5)
        self.play(FadeIn(text2, shift=UP))
        self.wait(5)
        self.play(FadeIn(text3, shift=UP))
        self.wait(8)
