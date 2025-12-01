"""
圣诞树粒子动画
使用粒子系统渲染的3D圣诞树，带有心形装饰和飘落的雪花
"""
import sys
import os
import pygame
import math
import random
from typing import Tuple, List

# Windows 高 DPI 支持
if sys.platform == 'win32':
    try:
        import ctypes
        # 告诉 Windows 这个程序是 DPI 感知的
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            # Windows 8.1 及以下版本的兼容方案
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass  # 如果失败就使用默认行为


# ============================================================================
# 配置参数
# ============================================================================

class Config:
    """应用程序配置常量"""
    # 显示设置
    WIDTH = 1440
    HEIGHT = 900
    FPS = 60
    WINDOW_TITLE = "Merry Christmas Tree"
    AUTO_FULLSCREEN = True  # 设置为True可启动时自动全屏

    # 颜色定义
    BG_COLOR = (25, 28, 35)
    WHITE = (255, 255, 255)
    TREE_COLORS = [
        (255, 180, 190),  # 柔粉色
        (255, 100, 150),  # 玫红色
        (255, 215, 0),    # 金色
        (255, 250, 240),  # 亮白色
        (200, 240, 255),  # 冰蓝色
        (220, 20, 60)     # 深红色
    ]
    GROUND_BASE_COLOR = (225, 225, 230)

    # 粒子数量
    TREE_PARTICLES = 6000
    HEART_PARTICLES = 2000
    GROUND_PARTICLES = 12000
    SNOW_PARTICLES = 600

    # 渲染参数
    FOV = 500
    VIEW_DISTANCE = 650
    FOG_START_Z = 50.0
    FOG_END_Z = 700.0

    # 动画参数
    AUTO_ROTATION_SPEED = 0.003
    ROTATION_FRICTION = 0.95
    MOUSE_SENSITIVITY = 0.005
    IDLE_TIMEOUT_MS = 2000
    RESUME_SMOOTHNESS = 0.02

    # 文本配置（列表格式：[(文本, 字号, 颜色), ...]）
    MESSAGE_LINES = [
        ("*Merry Christmas*", 70, (255, 250, 220)),      # 白色
        ("To Beloved Feifei: ", 46, (255, 200, 220)),        # 淡粉色
        ("The grass is bearing its seeds,", 32, (255, 255, 255)),
        ("The wind is swaying its leaves.", 32, (255, 255, 255)),
        ("We stand here, without a word,", 32, (255, 255, 255)),
        ("And it has already melt your heart.", 32, (255, 255, 255))
    ]
    TEXT_POSITION_X_RATIO = 0.15
    TEXT_POSITION_Y = None  # None = 垂直居中
    LINE_SPACING = 15  # 行间距
    SHADOW_OFFSET = (2, 2)


# ============================================================================
# 初始化
# ============================================================================

pygame.init()

# 根据配置决定是否全屏
if Config.AUTO_FULLSCREEN:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    # 更新实际屏幕尺寸
    Config.WIDTH, Config.HEIGHT = screen.get_size()
else:
    screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))

pygame.display.set_caption(Config.WINDOW_TITLE)
clock = pygame.time.Clock()


def load_font(size: int) -> pygame.font.Font:
    """加载最佳可用字体（支持中文）"""
    try:
        # 优先尝试中文字体
        font_candidates = [
            ('times new roman', True),      # 英文
            ('PingFang SC', True),      # macOS 中文
            ('Hiragino Sans GB', True),  # macOS 中文
            ('Microsoft YaHei', True),   # Windows 中文
            ('SimHei', True),            # Windows 中文
            ('STHeiti', True),           # 华文黑体
            ('Arial', True),             # 英文备选
        ]
        
        for font_name, bold in font_candidates:
            font_path = pygame.font.match_font(font_name, bold=bold)
            if font_path:
                return pygame.font.Font(font_path, size)
        
        # 如果都没找到，使用系统默认
        return pygame.font.SysFont(None, size)
    except Exception:
        return pygame.font.SysFont(None, size)

# ============================================================================
# 粒子系统
# ============================================================================

class Particle:
    """3D粒子类，包含位置、颜色和动画属性"""

    def __init__(self, x: float, y: float, z: float, color: Tuple[int, int, int], size_base: float):
        """初始化粒子的3D位置和视觉属性"""
        self.x, self.y, self.z = x, y, z
        self.orig_x, self.orig_y, self.orig_z = x, y, z
        self.color = color
        self.size_base = size_base

        self.flicker_speed = random.uniform(2.0, 5.0)
        self.flicker_offset = random.uniform(0, math.pi * 2)
        self.fall_speed = 0.0

    def rotate_y(self, angle: float) -> None:
        """绕Y轴旋转粒子"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        self.x = self.orig_x * cos_a - self.orig_z * sin_a
        self.z = self.orig_x * sin_a + self.orig_z * cos_a

    def _apply_fog(self, fog_factor: float) -> Tuple[int, int, int]:
        """对粒子颜色应用基于深度的雾化效果"""
        r = int(self.color[0] * (1 - fog_factor) + Config.BG_COLOR[0] * fog_factor)
        g = int(self.color[1] * (1 - fog_factor) + Config.BG_COLOR[1] * fog_factor)
        b = int(self.color[2] * (1 - fog_factor) + Config.BG_COLOR[2] * fog_factor)
        return (r, g, b)

    def _calculate_fog_factor(self) -> float:
        """根据Z轴深度计算雾化强度"""
        fog_factor = (self.z - Config.FOG_START_Z) / (Config.FOG_END_Z - Config.FOG_START_Z)
        return max(0.0, min(1.0, fog_factor))

    def _project_to_2d(self, scale: float) -> Tuple[int, int]:
        """将3D位置投影到2D屏幕坐标"""
        center_offset_x = int(Config.WIDTH * 0.6)
        x_2d = int(self.x * scale + center_offset_x)
        y_2d = int(self.y * scale + Config.HEIGHT // 2 + 100)
        return (x_2d, y_2d)

    def _draw_glow(self, surface: pygame.Surface, x: int, y: int, size: int, fog_factor: float, color: Tuple[int, int, int]) -> None:
        """绘制粒子周围的辉光效果"""
        if size > 3 and self.fall_speed == 0 and fog_factor < 0.5:
            glow_radius = int(size * 1.4)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_alpha = int(30 * (1 - fog_factor))
            pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (x - glow_radius, y - glow_radius), special_flags=pygame.BLEND_ADD)

    def draw(self, surface: pygame.Surface, time_input: float) -> None:
        """将粒子以3D投影方式渲染到屏幕"""
        # 提前剔除在相机后面的粒子
        if Config.VIEW_DISTANCE + self.z <= 20:
            return

        # 计算透视
        scale = Config.FOV / (Config.VIEW_DISTANCE + self.z)
        fog_factor = self._calculate_fog_factor()
        final_color = self._apply_fog(fog_factor)
        x_2d, y_2d = self._project_to_2d(scale)

        # 带闪烁效果的动画大小
        flicker = math.sin(time_input * self.flicker_speed + self.flicker_offset)
        current_size = self.size_base * scale * (0.8 + 0.4 * flicker)

        # 根据大小选择渲染方式
        if current_size <= 1.2:
            if current_size > 0.5 or random.random() < 0.6:
                try:
                    surface.set_at((x_2d, y_2d), final_color)
                except IndexError:
                    pass  # 粒子超出屏幕边界
        else:
            size = int(current_size)
            pygame.draw.circle(surface, final_color, (x_2d, y_2d), size)
            self._draw_glow(surface, x_2d, y_2d, size, fog_factor, final_color)

# ============================================================================
# 粒子生成器
# ============================================================================

def generate_ragged_tree(num_particles: int) -> List[Particle]:
    """生成分层圣诞树的粒子"""
    particles = []
    tree_height = 700
    max_base_radius = 260
    num_layers = 9

    for i in range(num_particles):
        # 垂直分布（从底到顶）
        h_norm = i / num_particles
        h_dist = math.pow(h_norm, 0.75)
        y = -tree_height * 0.58 + h_dist * tree_height
        y += random.uniform(-4, 4)

        # 分层半径计算 - 调整使树更饱满
        cone_boundary_r = max_base_radius * h_dist
        wave_factor = abs(math.sin(h_dist * math.pi * num_layers))
        # 增大layer_profile_scale的基础值：从0.25到0.35，让每层更饱满
        layer_profile_scale = 0.35 + 0.65 * wave_factor
        current_layer_max_r = cone_boundary_r * layer_profile_scale

        # 带扰动的径向分布 - 使用更小的幂次让粒子分布更均匀饱满
        r_scatter = math.pow(random.random(), 0.25)  # 从0.35减小到0.25
        r = current_layer_max_r * r_scatter
        turbulence_scale = random.uniform(0.9, 1.35)  # 稍微增大范围
        if random.random() < 0.08:  # 从5%增加到8%
            turbulence_scale = 1.6  # 从1.5增加到1.6
        r *= turbulence_scale

        # 树顶更窄
        if h_dist < 0.06:
            r = random.uniform(0, 8 * (1 - h_dist))

        # 螺旋角度分布
        theta = random.uniform(0, math.pi * 2) + h_dist * math.pi * 12
        x = r * math.cos(theta)
        z = r * math.sin(theta)

        # 颜色选择
        color = random.choice(Config.TREE_COLORS)
        if h_dist < 0.08:
            color = Config.WHITE  # 明亮的顶部
        elif r_scatter < 0.4:
            color = tuple(max(0, c - 50) for c in color)  # 较暗的内部

        # 大小变化
        size = random.uniform(0.6, 2.0)
        if turbulence_scale > 1.3:
            size = random.uniform(2.0, 3.0)
            color = Config.WHITE  # 高亮异常值

        particles.append(Particle(x, y, z, color, size))

    return particles

def generate_bright_white_ground(num_particles: int) -> List[Particle]:
    """生成波纹地面的粒子"""
    particles = []
    ground_y = 240
    max_dist = 1400  # 从950增加到1400，覆盖更大面积

    for _ in range(num_particles):
        # 径向分布 - 使用更平滑的分布减少边缘锐利感
        angle = random.uniform(0, math.pi * 2)
        # 使用更高的幂次(0.6)让边缘粒子分布更密集，减少锐利边缘
        dist = math.pow(random.random(), 0.6) * max_dist
        x = dist * math.cos(angle)
        z = dist * math.sin(angle)

        # 更柔和的波纹效果
        # 增大波长(从35.0到60.0)，减小振幅(从25到12)
        ripple_val = math.sin(dist / 60.0 - 2.0)
        brightness_offset = int(ripple_val * 12)

        # 应用亮度变化
        base_r, base_g, base_b = Config.GROUND_BASE_COLOR
        r = max(0, min(255, base_r + brightness_offset))
        g = max(0, min(255, base_g + brightness_offset))
        b = max(0, min(255, base_b + brightness_offset + 5))
        color = (r, g, b)

        # 边缘使用稍大的粒子填充空隙
        if dist > max_dist * 0.8:
            size = random.uniform(1.0, 2.0)
        else:
            size = random.uniform(0.5, 1.5)

        particles.append(Particle(x, ground_y, z, color, size))

    return particles


def generate_snow(num_particles: int) -> List[Particle]:
    """生成飘落的雪花粒子"""
    particles = []
    for _ in range(num_particles):
        x = random.uniform(-500, 500)
        y = random.uniform(-500, 300)
        z = random.uniform(-500, 500)
        p = Particle(x, y, z, Config.WHITE, random.uniform(0.8, 1.8))
        p.fall_speed = random.uniform(0.2, 0.6)
        particles.append(p)
    return particles


def generate_pillow_heart(num_particles: int) -> List[Particle]:
    """生成树顶的3D蓬松心形"""
    particles = []
    scale_base = 3.0
    y_offset = -465  # 树顶的位置

    for _ in range(num_particles):
        # 参数化心形曲线
        t = random.uniform(0, math.pi * 2)
        x0 = 16 * math.sin(t)**3
        y0 = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)

        # 更平滑的径向填充以获得更饱满的外观
        # 使用0.2次方代替0.3使其更饱满
        r = math.pow(random.random(), 0.2)

        # 缩放位置
        scale = scale_base * r
        p_x = x0 * scale
        p_y = -y0 * scale + y_offset

        # 3D厚度实现"蓬松"效果 - 增加以获得更圆润的边缘
        max_thickness = 16.0  # 从13.0增加
        # 使用更平滑的衰减以获得更圆润的边缘
        z_thickness = max_thickness * math.pow(math.cos(r * math.pi / 2), 0.7)
        z_side = 1 if random.random() > 0.5 else -1
        # 减少变化以获得更光滑的表面
        p_z = z_thickness * z_side * random.uniform(0.9, 1.1)

        # 添加边缘平滑：边缘附近更多粒子
        if r > 0.85:
            # 在边缘周围创建额外的平滑粒子
            edge_offset = random.uniform(-0.5, 0.5)
            p_x += edge_offset * math.cos(t)
            p_y += edge_offset * math.sin(t)

        # 颜色渐变（明亮的中心，粉色的边缘）+ 金色闪光点
        sparkle_chance = random.random()

        if sparkle_chance < 0.03:  # 3%的金色大亮点
            color = (255, 215, 0)  # 金色
            size = random.uniform(2.5, 3.5)  # 更大
        elif sparkle_chance < 0.08:  # 额外5%的金色小亮点
            color = (255, 223, 100)  # 淡金色
            size = random.uniform(1.8, 2.3)
        elif r < 0.4:
            color = (255, 230, 230)  # 几乎白色的中心
            size = random.uniform(1.0, 1.6)  # 稍大的粒子以获得更饱满的外观
        else:
            color = (255, 80, 110)   # 明亮的粉色边缘
            size = random.uniform(1.0, 1.6)
            if random.random() < 0.15:
                color = Config.WHITE  # 随机亮点

        particles.append(Particle(p_x, p_y, p_z, color, size))

    return particles

# ============================================================================
# 文本渲染
# ============================================================================

class MultiLineText:
    """渲染多行文本，每行可设置不同字号"""

    def __init__(self, lines: List[Tuple[str, int]], position_x: int, position_y: int = None,
                 line_spacing: int = Config.LINE_SPACING, shadow_offset: Tuple[int, int] = Config.SHADOW_OFFSET,
                 align: str = "left"):
        """
        初始化多行文本渲染器

        Args:
            lines: 文本、字号和颜色的元组列表 [(文本, 字号, 颜色), ...] 或 [(文本, 字号), ...]
            position_x: X位置（意义取决于对齐方式："left"时为左边缘，"center"时为中心）
            position_y: 文本块中心的Y位置（None = 屏幕中心）
            line_spacing: 行间距
            shadow_offset: 阴影偏移 (x, y)
            align: 文本对齐方式（"left"、"center"、"right"）
        """
        self.lines = lines
        self.position_x = position_x
        self.line_spacing = line_spacing
        self.shadow_offset = shadow_offset
        self.align = align

        # 预渲染所有文本表面
        self.text_surfaces = []
        self.shadow_surfaces = []

        for line_data in lines:
            if len(line_data) == 2:
                # 旧格式兼容：(文本, 字号)
                text, font_size = line_data
                color = Config.WHITE
            else:
                # 新格式：(文本, 字号, 颜色)
                text, font_size, color = line_data
            
            font = load_font(font_size)
            text_surf = font.render(text, True, color)
            shadow_surf = font.render(text, True, (0, 0, 0))
            self.text_surfaces.append(text_surf)
            self.shadow_surfaces.append(shadow_surf)

        # 计算总高度
        self.total_height = sum(surf.get_height() for surf in self.text_surfaces)
        self.total_height += line_spacing * (len(lines) - 1)

        # 如果未指定则计算position_y
        if position_y is None:
            self.position_y = Config.HEIGHT // 2
        else:
            self.position_y = position_y

    def draw(self, surface: pygame.Surface) -> None:
        """绘制所有文本行及其阴影"""
        # 从文本块顶部开始
        current_y = self.position_y - self.total_height // 2

        for text_surf, shadow_surf in zip(self.text_surfaces, self.shadow_surfaces):
            # 根据对齐方式定位
            if self.align == "left":
                text_rect = text_surf.get_rect(
                    left=self.position_x,
                    centery=current_y + text_surf.get_height() // 2
                )
                shadow_rect = shadow_surf.get_rect(
                    left=self.position_x + self.shadow_offset[0],
                    centery=current_y + text_surf.get_height() // 2 + self.shadow_offset[1]
                )
            elif self.align == "right":
                text_rect = text_surf.get_rect(
                    right=self.position_x,
                    centery=current_y + text_surf.get_height() // 2
                )
                shadow_rect = shadow_surf.get_rect(
                    right=self.position_x + self.shadow_offset[0],
                    centery=current_y + text_surf.get_height() // 2 + self.shadow_offset[1]
                )
            else:  # center
                text_rect = text_surf.get_rect(
                    center=(self.position_x, current_y + text_surf.get_height() // 2)
                )
                shadow_rect = shadow_surf.get_rect(
                    center=(self.position_x + self.shadow_offset[0],
                           current_y + text_surf.get_height() // 2 + self.shadow_offset[1])
                )

            # 先绘制阴影，再绘制文本
            surface.blit(shadow_surf, shadow_rect)
            surface.blit(text_surf, text_rect)

            # 移动到下一行
            current_y += text_surf.get_height() + self.line_spacing


# ============================================================================
# 主应用程序
# ============================================================================

class RotationController:
    """管理鼠标交互旋转和自动旋转"""

    def __init__(self):
        self.angle = 0.0
        self.velocity = 0.0
        self.is_dragging = False
        self.last_mouse_x = 0
        self.last_interaction_time = 0

    def handle_mouse_down(self, mouse_x: int, current_time: int) -> None:
        """开始拖拽交互"""
        self.is_dragging = True
        self.last_mouse_x = mouse_x
        self.last_interaction_time = current_time
        self.velocity = 0

    def handle_mouse_up(self, current_time: int) -> None:
        """结束拖拽交互"""
        self.is_dragging = False
        self.last_interaction_time = current_time

    def update(self, current_time: int) -> None:
        """根据鼠标或自动旋转更新旋转状态"""
        if self.is_dragging:
            mouse_x, _ = pygame.mouse.get_pos()
            delta_x = mouse_x - self.last_mouse_x
            self.velocity = delta_x * Config.MOUSE_SENSITIVITY
            self.last_mouse_x = mouse_x
            self.last_interaction_time = current_time
        else:
            time_since_last_interact = current_time - self.last_interaction_time
            if time_since_last_interact > Config.IDLE_TIMEOUT_MS:
                # 平滑恢复自动旋转
                self.velocity = (self.velocity * (1 - Config.RESUME_SMOOTHNESS) +
                                Config.AUTO_ROTATION_SPEED * Config.RESUME_SMOOTHNESS)
            else:
                # 应用摩擦力
                self.velocity *= Config.ROTATION_FRICTION

        self.angle += self.velocity


def update_snow(snow_particles: List[Particle]) -> None:
    """更新飘落的雪花位置，超出屏幕时重置"""
    for p in snow_particles:
        p.y += p.fall_speed
        if p.y > 250:
            p.y = -500
            p.x = random.uniform(-500, 500)
            p.z = random.uniform(-500, 500)


def main() -> None:
    """主应用程序循环"""
    print("Generating Particles...")
    tree_particles = generate_ragged_tree(Config.TREE_PARTICLES)
    heart_particles = generate_pillow_heart(Config.HEART_PARTICLES)
    ground_particles = generate_bright_white_ground(Config.GROUND_PARTICLES)
    snow_particles = generate_snow(Config.SNOW_PARTICLES)

    rotating_objects = tree_particles + heart_particles + ground_particles
    rotation_controller = RotationController()

    # 创建多行文本渲染器（左对齐）
    text_pos_x = int(Config.WIDTH * Config.TEXT_POSITION_X_RATIO)
    multi_line_text = MultiLineText(
        lines=Config.MESSAGE_LINES,
        position_x=text_pos_x,
        position_y=Config.TEXT_POSITION_Y,
        align="left"
    )

    start_ticks = pygame.time.get_ticks()
    running = True

    while running:
        current_time = pygame.time.get_ticks()

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                rotation_controller.handle_mouse_down(event.pos[0], current_time)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                rotation_controller.handle_mouse_up(current_time)

        # 更新旋转
        rotation_controller.update(current_time)

        # 旋转对象
        for p in rotating_objects:
            p.rotate_y(rotation_controller.angle)

        # 更新雪花
        update_snow(snow_particles)

        # 准备渲染
        time_seconds = (current_time - start_ticks) / 1000.0
        all_particles = rotating_objects + snow_particles
        all_particles.sort(key=lambda p: p.z, reverse=True)

        # 渲染
        screen.fill(Config.BG_COLOR)
        for p in all_particles:
            p.draw(screen, time_seconds)

        # 绘制多行文本
        multi_line_text.draw(screen)

        pygame.display.flip()
        clock.tick(Config.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()