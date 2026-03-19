from manim import *
import numpy as np
from scipy.spatial.transform import Rotation

config.background_color = "#0B0F1A"

class MicroscopyScene(Scene):
    def construct(self):
        title = Text("Microscopía y Tamaño de Grano", font_size=40, weight=BOLD)
        title.to_edge(UP)
        title_line = Line(title.get_left(), title.get_right(), color=BLUE).next_to(title, DOWN, buff=0.1)
        self.play(Write(title), Create(title_line))
        
        def create_grain_cluster(scale_factor=1.0, color=DARK_GRAY):
            polys = VGroup(
                Polygon(LEFT*2+UP, LEFT*0.5+UP*1.5, RIGHT*0.5+UP*0.5, LEFT*0.5+DOWN*0.5, LEFT*2+DOWN*0.2),
                Polygon(LEFT*0.5+UP*1.5, RIGHT*1.5+UP*1.5, RIGHT*2+UP*0.5, RIGHT*0.5+UP*0.5),
                Polygon(RIGHT*0.5+UP*0.5, RIGHT*2+UP*0.5, RIGHT*1.5+DOWN*1.5, RIGHT*0.5+DOWN*0.5),
                Polygon(LEFT*0.5+DOWN*0.5, RIGHT*0.5+UP*0.5, RIGHT*0.5+DOWN*0.5, LEFT*0.5+DOWN*1.5),
                Polygon(LEFT*2+DOWN*0.2, LEFT*0.5+DOWN*0.5, LEFT*0.5+DOWN*1.5, LEFT*1.5+DOWN*2)
            )
            polys.set_fill(color, opacity=0.8)
            polys.set_stroke(WHITE, width=2)
            polys.scale(scale_factor)
            return polys

        # Part 1: Large Grains
        large_grains = create_grain_cluster(scale_factor=1.4).shift(LEFT*3 + DOWN*1.2)
        
        domains = VGroup()
        for poly in large_grains:
            center = poly.get_center()
            for i in range(2):
                d = UP if i==0 else RIGHT
                arr = Arrow(center - d*0.3 + (LEFT*0.2 if i==1 else ORIGIN), 
                            center + d*0.3 + (LEFT*0.2 if i==1 else ORIGIN), 
                            buff=0, color=YELLOW, max_tip_length_to_length_ratio=0.3)
                domains.add(arr)
                
        text_large = VGroup(
            Text("Granos Grandes (> 1 μm)", font_size=24),
            Text("Fuertes dominios piezoeléctricos", font_size=24, color=YELLOW)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(large_grains, UP, buff=0.6)

        self.play(FadeIn(large_grains))
        self.play(Create(domains), run_time=1.5)
        self.play(Write(text_large))
        self.wait(2)
        
        # Part 2: Small Grains (< 100 nm)
        small_grains_group = VGroup()
        for dx in np.linspace(-1, 2, 4):
            for dy in np.linspace(-1.5, 1.5, 4):
                cluster = create_grain_cluster(scale_factor=0.25)
                cluster.move_to(RIGHT*(dx*1.0 + 3.5) + UP*(dy*1.0 - 1.5))
                c_val = np.random.random() * 0.3 + 0.2
                cluster.set_fill(color=rgb_to_color((c_val, c_val, c_val)))
                small_grains_group.add(cluster)
        
        text_small = VGroup(
            Text("Efecto de Tamaño: Granos < 100 nm", font_size=24),
            Text("En este caso se pierde la\npropiedad piezoeléctrica", font_size=24, color=RED)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(small_grains_group, UP, buff=0.6)

        self.play(FadeIn(small_grains_group))
        
        cross = Cross(small_grains_group, stroke_color=RED, stroke_width=6)
        self.play(Create(cross), Write(text_small))
        self.wait(3)


# Manual 2D Projection for Perovskite
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
        self.o_atoms = [Dot(radius=0.1, color=GREEN) for _ in range(6)]
        self.ti_atom = Dot(radius=0.12, color=RED)
        self.edges = [Line(ORIGIN, UP, color=WHITE, stroke_width=2) for _ in range(12)]
        
        self.dim_a_line = DoubleArrow(ORIGIN, UP, color=YELLOW, stroke_width=3, buff=0, max_tip_length_to_length_ratio=0.2)
        self.dim_c_line = DoubleArrow(ORIGIN, UP, color=YELLOW, stroke_width=3, buff=0, max_tip_length_to_length_ratio=0.2)
        self.lbl_a = Text("a", font_size=20, color=YELLOW)
        self.lbl_c = Text("c", font_size=20, color=YELLOW)
        
        self.add(*self.edges, *self.ba_atoms, *self.o_atoms, self.ti_atom)
        self.add(self.dim_a_line, self.dim_c_line, self.lbl_a, self.lbl_c)
        
    def update_cell(self, t_val, rot_angle, offset=ORIGIN):
        a = 2.0 - 0.1 * t_val
        c = 2.0 + 0.5 * t_val
        
        corners = [
            [-a/2, -a/2, -c/2], [a/2, -a/2, -c/2], [a/2, a/2, -c/2], [-a/2, a/2, -c/2],
            [-a/2, -a/2, c/2],  [a/2, -a/2, c/2],  [a/2, a/2, c/2],  [-a/2, a/2, c/2]
        ]
        faces = [
            [0, 0, c/2], [0, 0, -c/2],
            [a/2, 0, 0], [-a/2, 0, 0],
            [0, a/2, 0], [0, -a/2, 0]
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
        sortable.sort(key=lambda m: z_map.get(m, 0), reverse=True) 
        
        pa0, _ = project_iso(corners[0][0], corners[0][1] - 0.4, corners[0][2], rot_z_deg=rot_angle)
        pa1, _ = project_iso(corners[1][0], corners[1][1] - 0.4, corners[1][2], rot_z_deg=rot_angle)
        self.dim_a_line.put_start_and_end_on(pa0 + offset, pa1 + offset)
        self.lbl_a.move_to((pa0+pa1)/2 + offset + DOWN*0.25)
        
        pc0, _ = project_iso(corners[0][0] - 0.4, corners[0][1], corners[0][2], rot_z_deg=rot_angle)
        pc4, _ = project_iso(corners[4][0] - 0.4, corners[4][1], corners[4][2], rot_z_deg=rot_angle)
        self.dim_c_line.put_start_and_end_on(pc0 + offset, pc4 + offset)
        self.lbl_c.move_to((pc0+pc4)/2 + offset + LEFT*0.35)
        
        self.submobjects = sortable + [self.dim_a_line, self.dim_c_line, self.lbl_a, self.lbl_c]

class XRDPhaseScene(Scene):
    def construct(self):
        title = Text("Difracción (XRD) y Fases", font_size=36, weight=BOLD)
        title.to_edge(UP)
        title_line = Line(title.get_left(), title.get_right(), color=BLUE).next_to(title, DOWN, buff=0.1)
        self.add(title, title_line)

        axes = Axes(
            x_range=[44, 46, 0.5], 
            y_range=[0, 1.6, 0.5], 
            x_length=4.0, 
            y_length=3.3, 
            axis_config={"color": WHITE, "include_numbers":True}, 
            tips=False
        )
        axes.to_edge(LEFT, buff=0.8).shift(DOWN*0.8)
        
        y_label = Text("Intensidad", font_size=18).rotate(PI/2).next_to(axes.y_axis, LEFT, buff=0.2)
        x_label = Text("2-Theta", font_size=18).next_to(axes.x_axis, DOWN, buff=0.2)
        self.add(axes, x_label, y_label)

        t_tracker = ValueTracker(0)

        def xrd_profile(x, t):
            mu1 = 45.15 - 0.25 * t
            mu2 = 45.15 + 0.25 * t
            amp1 = 1.0 - 0.3 * t 
            amp2 = 0.0 + 1.1 * t  
            sig = 0.06 + 0.02*t
            p1 = amp1 * np.exp(-0.5 * ((x - mu1) / sig)**2)
            p2 = amp2 * np.exp(-0.5 * ((x - mu2) / sig)**2)
            return p1 + p2
            
        curve = always_redraw(lambda: axes.plot(lambda x: xrd_profile(x, t_tracker.get_value()), color=YELLOW))
        self.add(curve)

        peak_002_line = always_redraw(lambda: DashedLine(
            axes.c2p(45.15 - 0.25 * t_tracker.get_value(), 0), axes.c2p(45.15 - 0.25 * t_tracker.get_value(), 1.0), color=WHITE
        ).set_opacity(t_tracker.get_value()))
        peak_200_line = always_redraw(lambda: DashedLine(
            axes.c2p(45.15 + 0.25 * t_tracker.get_value(), 0), axes.c2p(45.15 + 0.25 * t_tracker.get_value(), 1.2), color=WHITE
        ).set_opacity(t_tracker.get_value()))
        
        lbl_002 = always_redraw(lambda: Text("(002)", font_size=16, color=WHITE).next_to(peak_002_line, UP).set_opacity(t_tracker.get_value()))
        lbl_200 = always_redraw(lambda: Text("(200)", font_size=16, color=WHITE).next_to(peak_200_line, UP).set_opacity(t_tracker.get_value()))

        phase_lbl = always_redraw(lambda: Text(
            "Tetragonal (Piezoeléctrico)" if t_tracker.get_value() > 0.5 else "Cúbico (No piezoeléctrico)",
            font_size=22, color=RED if t_tracker.get_value() > 0.5 else BLUE
        ).next_to(axes, UP, buff=0.6).align_to(axes, LEFT))

        self.add(peak_002_line, peak_200_line, lbl_002, lbl_200, phase_lbl)

        cell = PerovskiteCell()
        angle_tracker = ValueTracker(0)
        
        OFFSET = RIGHT*3.5 + DOWN*0.5
        
        def cell_updater(mob, dt):
            angle_tracker.increment_value(dt * 30)
            mob.update_cell(t_tracker.get_value(), angle_tracker.get_value(), offset=OFFSET)
            
        cell.add_updater(cell_updater)
        self.add(cell)

        self.wait(1)
        self.play(t_tracker.animate.set_value(1), run_time=5, rate_func=smooth)
        self.wait(3)

class PhaseTransitionsScene(Scene):
    def construct(self):
        title = Text("Transiciones de Fase y Estabilidad", font_size=40, weight=BOLD)
        title.to_edge(UP)
        title_line = Line(title.get_left(), title.get_right(), color=BLUE).next_to(title, DOWN, buff=0.1)
        self.add(title, title_line)

        axes = Axes(x_range=[20, 160, 20], y_range=[0, 10000, 2000], x_length=4.0, y_length=3.3, axis_config={"color": WHITE, "include_numbers":True}, tips=False)
        axes.to_edge(LEFT, buff=0.8).shift(DOWN*0.5)

        x_label = Text("Temperatura (°C)", font_size=18).next_to(axes.x_axis, DOWN, buff=0.3)
        y_label = Text("Permitividad (ε')", font_size=18).rotate(PI/2).next_to(axes.y_axis, LEFT, buff=0.2)
        self.add(axes, x_label, y_label)

        def permittivity(T):
            return 1500 + 8500 / (1.0 + 0.15 * abs(T - 120)**1.5)

        curve = axes.plot(permittivity, color=BLUE)
        self.add(curve)

        T_tracker = ValueTracker(25)
        
        dot = always_redraw(lambda: Dot(axes.c2p(T_tracker.get_value(), permittivity(T_tracker.get_value())), color=YELLOW).scale(1.5))
        T_label = always_redraw(lambda: Text(f"{T_tracker.get_value():.0f} °C", font_size=20, color=YELLOW).next_to(dot, UP+RIGHT, buff=0.15))
        self.add(dot, T_label)

        cell = PerovskiteCell()
        angle_tracker = ValueTracker(0)
        OFFSET = RIGHT*3.5 + DOWN*0.5

        def param_from_T(T):
            if T < 115: return 1.0
            elif T > 125: return 0.0
            else: return 1.0 - (T-115)/10.0 

        def cell_updater(mob, dt):
            angle_tracker.increment_value(dt * 30)
            t_val = param_from_T(T_tracker.get_value())
            mob.update_cell(t_val, angle_tracker.get_value(), offset=OFFSET)
            
        cell.add_updater(cell_updater)
        self.add(cell)

        self.wait(1)
        self.play(T_tracker.animate.set_value(120), run_time=5, rate_func=linear)

        alert = VGroup(
            Text("Transición a fase cúbica:", font_size=24, color=RED),
            Text("Pérdida de piezoelectricidad", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(axes, UP, buff=0.4).align_to(axes, LEFT)

        self.add(alert)
        self.play(Flash(dot, color=RED, line_length=0.4, num_lines=12, flash_radius=0.4))
        self.wait(1.5)

        self.play(T_tracker.animate.set_value(150), run_time=3, rate_func=linear)
        self.wait(2)
