"""
圣诞树粒子动画
使用粒子系统渲染的3D圣诞树，带有心形装饰和飘落的雪花
"""
import sys
import os
import math
import random
from typing import Tuple, List, Optional, Dict

import pygame


# Windows 特定配置
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

    # 设置唯一的应用ID，让Windows任务栏正确识别图标
    try:
        myappid = 'hexiao.christmas_tree.app.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass  # 如果失败就继续使用默认行为


# ============================================================================
# 配置参数
# ============================================================================

class Config:
    """应用程序配置常量"""
    # 显示设置
    VIRTUAL_WIDTH = 1920   # 虚拟分辨率宽度（设计基准）
    VIRTUAL_HEIGHT = 1080   # 虚拟分辨率高度（设计基准）
    WIDTH = VIRTUAL_WIDTH  # 实际窗口宽度（全屏时会更新）
    HEIGHT = VIRTUAL_HEIGHT  # 实际窗口高度（全屏时会更新）
    FPS = 60
    WINDOW_TITLE = "Merry Christmas Tree"
    AUTO_FULLSCREEN = False  # 设置为True可启动时自动全屏
    MAINTAIN_ASPECT_RATIO = True  # 保持宽高比，避免拉伸变形

    # 颜色定义
    BG_COLOR = (25, 28, 35)
    WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)      # 金色
    LIGHT_GOLD = (255, 230, 100)  # 浅金色
    # 内部深色调色板（深粉紫色系）
    TREE_COLORS_INNER = [
        (115, 50, 95),    # 深粉紫色
        (125, 45, 105),   # 深紫粉色
        (135, 60, 100),   # 暗粉紫色
        (105, 40, 85),    # 很深的紫粉色
        (120, 48, 92),    # 深玫紫色
        (130, 55, 105),   # 中深粉紫色
        (95, 45, 110),    # 深紫色
        (105, 50, 120),   # 深紫罗兰色
        (85, 40, 100),    # 很深的紫色
        (100, 45, 105),   # 暗紫色
        (110, 55, 115),   # 深紫红色
    ]
    # 中间过渡色调色板
    TREE_COLORS_MID = [
        (160, 75, 125),   # 中粉紫色
        (170, 85, 135),   # 玫瑰粉
        (155, 70, 120),   # 柔玫瑰紫
        (180, 80, 140),   # 亮一点的粉紫色
        (190, 95, 145),   # 玫瑰粉红
        (140, 70, 135),   # 中深紫色
        (150, 75, 145),   # 紫罗兰色
        (135, 65, 140),   # 深紫粉色
        (145, 70, 150),   # 中紫色
        (155, 80, 155),   # 紫红色
    ]
    # 外层亮色调色板
    TREE_COLORS_OUTER = [
        (200, 110, 155),  # 柔粉色
        (210, 120, 165),  # 亮粉色
        (220, 130, 170),  # 浅粉色
        (235, 150, 180),  # 很浅的粉色
        (245, 170, 195),  # 淡粉色
    ]
    GROUND_BASE_COLOR = (225, 225, 230)

    # 粒子数量
    TREE_PARTICLES = 10000
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

    # 音乐配置
    MUSIC_FILE = "music.mp3"
    DEFAULT_VOLUME = 0.5  # 默认音量 50%


# ============================================================================
# 初始化
# ============================================================================

pygame.init()
pygame.mixer.init()  # 初始化音频混音器

# 根据配置决定是否全屏
if Config.AUTO_FULLSCREEN:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    # 更新实际屏幕尺寸
    Config.WIDTH, Config.HEIGHT = screen.get_size()
else:
    screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))

pygame.display.set_caption(Config.WINDOW_TITLE)
clock = pygame.time.Clock()

# 加载背景音乐
def get_resource_path(relative_path):
    """获取资源文件的绝对路径（支持打包后的环境）"""
    try:
        # PyInstaller 创建临时文件夹，路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def set_window_icon():
    """设置窗口图标"""
    try:
        icon_path = get_resource_path("icon.png")
        icon_surface = pygame.image.load(icon_path).convert_alpha()
        pygame.display.set_icon(icon_surface)
        print(f"Window icon loaded: {icon_path}")
    except Exception as error:
        print(f"Failed to load window icon: {error}")


set_window_icon()


def load_png_icon(relative_path: str, size: int) -> Optional[pygame.Surface]:
    """加载PNG图标并缩放为指定大小"""
    icon_path = get_resource_path(relative_path)
    try:
        icon = pygame.image.load(icon_path).convert_alpha()
        # 缩放到指定大小
        icon = pygame.transform.smoothscale(icon, (size, size))
        return icon
    except Exception as error:
        print(f"Failed to load PNG icon '{relative_path}': {error}")
        return None

try:
    music_path = get_resource_path(Config.MUSIC_FILE)
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(Config.DEFAULT_VOLUME)
    pygame.mixer.music.play(-1)  # -1 表示循环播放
    print(f"Background music loaded: {music_path}")
except Exception as e:
    print(f"Failed to load music: {e}")

# 创建虚拟渲染表面（固定分辨率）
virtual_surface = pygame.Surface((Config.VIRTUAL_WIDTH, Config.VIRTUAL_HEIGHT))

# 计算缩放和偏移以保持宽高比
def calculate_scaling():
    """计算虚拟表面到实际屏幕的缩放参数"""
    if Config.MAINTAIN_ASPECT_RATIO:
        # 保持宽高比，可能出现黑边
        scale_x = Config.WIDTH / Config.VIRTUAL_WIDTH
        scale_y = Config.HEIGHT / Config.VIRTUAL_HEIGHT
        scale = min(scale_x, scale_y)

        scaled_width = int(Config.VIRTUAL_WIDTH * scale)
        scaled_height = int(Config.VIRTUAL_HEIGHT * scale)

        offset_x = (Config.WIDTH - scaled_width) // 2
        offset_y = (Config.HEIGHT - scaled_height) // 2

        return scaled_width, scaled_height, offset_x, offset_y
    else:
        # 拉伸填充整个屏幕，可能变形
        return Config.WIDTH, Config.HEIGHT, 0, 0

scaled_width, scaled_height, offset_x, offset_y = calculate_scaling()


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

    def __init__(self, x: float, y: float, z: float, color: Tuple[int, int, int], size_base: float, is_snow: bool = False):
        """初始化粒子的3D位置和视觉属性"""
        self.x, self.y, self.z = x, y, z
        self.orig_x, self.orig_y, self.orig_z = x, y, z
        self.color = color
        self.size_base = size_base
        self.is_snow = is_snow  # 标记是否为雪花粒子

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
        center_offset_x = int(Config.VIRTUAL_WIDTH * 0.6)
        x_2d = int(self.x * scale + center_offset_x)
        y_2d = int(self.y * scale + Config.VIRTUAL_HEIGHT // 2 + 100)
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
        # 雪花粒子闪烁不明显（0.05），其他粒子正常闪烁（0.4）
        flicker_amplitude = 0.05 if self.is_snow else 0.4
        current_size = self.size_base * scale * (0.8 + flicker_amplitude * flicker)

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

        # 带扰动的径向分布 - 使用更小的幂次让内部粒子更密集
        # 降低幂次让更多粒子聚集在内部
        r_scatter = math.pow(random.random(), 0.15)  # 从0.25减小到0.15，让内部更密集
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

        # 添加树枝状的径向扰动
        # 在特定角度方向上添加线性延伸，模拟树枝效果
        num_branches = 8  # 每层的主要分支数
        branch_angle = (theta % (math.pi * 2 / num_branches))
        branch_proximity = abs(branch_angle - math.pi / num_branches)

        # 如果粒子靠近某个分支方向，则向外延伸
        if branch_proximity < 0.4:  # 在分支方向的容差范围内
            branch_strength = 1.0 - (branch_proximity / 0.4)  # 越靠近分支中心，强度越大
            # 沿径向添加延伸扰动
            branch_extension = branch_strength * random.uniform(0, 25) * (1 - h_dist * 0.3)
            r += branch_extension

            # 添加一些垂直方向的微小偏移，让树枝更自然
            if random.random() < 0.3:
                y += random.uniform(-8, 8) * branch_strength

        x = r * math.cos(theta)
        z = r * math.sin(theta)

        # 颜色选择 - 从内到外由深到浅（粉紫→粉色→白色雪花+金色）
        is_snow_particle = False  # 标记是否为雪花粒子
        is_gold_particle = False  # 标记是否为金色粒子

        # 树顶的雪花
        if h_dist < 0.06:
            color = Config.WHITE
            is_snow_particle = True
            size = random.uniform(0.5, 1.2)  # 小雪花
        # 内部深色（粉紫色系）
        elif r_scatter < 0.45:
            color = random.choice(Config.TREE_COLORS_INNER)
            # 最内部进一步加深
            if r_scatter < 0.25:
                color = tuple(max(0, int(c * 0.75)) for c in color)
            elif r_scatter < 0.35:
                color = tuple(max(0, int(c * 0.85)) for c in color)
            # 在深色区域添加少量金色点缀
            if random.random() < 0.015:
                color = Config.LIGHT_GOLD
                is_gold_particle = True
            # 在深色区域添加少量白色雪花
            elif random.random() < 0.03:
                color = Config.WHITE
                is_snow_particle = True
                size = random.uniform(0.5, 1.0)  # 小雪花
        # 中间层过渡色
        elif r_scatter < 0.72:
            color = random.choice(Config.TREE_COLORS_MID)
            # 在中间层添加金色点缀
            if random.random() < 0.03:
                color = Config.GOLD if random.random() < 0.6 else Config.LIGHT_GOLD
                is_gold_particle = True
            # 在中间层添加白色雪花
            elif random.random() < 0.06:
                color = Config.WHITE
                is_snow_particle = True
                size = random.uniform(0.5, 1.2)  # 小雪花
        # 外层亮色
        else:
            # 外层白色雪花效果
            if random.random() < 0.58:
                color = Config.WHITE
                is_snow_particle = True
                size = random.uniform(0.4, 1.0)
            # 外层金色装饰
            elif random.random() < 0.04:
                color = Config.GOLD
                is_gold_particle = True
            else:
                color = random.choice(Config.TREE_COLORS_OUTER)
                # 最外层稍微提亮
                if r_scatter > 0.88:
                    color = tuple(min(255, int(c * 1.12)) for c in color)

        # 大小变化
        if not is_snow_particle and not is_gold_particle:
            size = random.uniform(0.6, 2.0)  # 默认大小

        # 最外层突出的雪花效果
        if turbulence_scale > 2.8:
            if random.random() < 0.88:  # 88%是白色雪花
                color = Config.WHITE
                is_snow_particle = True
                size = random.uniform(0.5, 1.1)
            else:  # 12%是金色点缀
                color = Config.GOLD
                is_gold_particle = True
                size = random.uniform(1.2, 2.5)

        # 根据粒子类型调整大小
        if is_gold_particle:
            # 金色粒子偏大，作为装饰亮点
            if random.random() < 0.3:  # 30%是大金色粒子
                size = random.uniform(2.8, 4.2)
            else:
                size = random.uniform(1.8, 3.0)
        elif not is_snow_particle:
            # 其他彩色粒子根据亮度调整大小
            brightness = (color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114)

            if brightness > 180:  # 偏亮的彩色粒子
                # 20%概率变成大粒子
                if random.random() < 0.2:
                    size = random.uniform(2.5, 4.0)
                else:
                    size = random.uniform(1.2, 2.5)
            elif brightness > 120:  # 中等亮度
                size = random.uniform(0.8, 2.2)
            else:  # 深色粒子
                size = random.uniform(0.6, 1.8)

        particles.append(Particle(x, y, z, color, size, is_snow=is_snow_particle))

    # 在最外层增加额外的白色雪花层，模拟落在树上的雪
    num_snow_layer = int(num_particles * 0.4)  # 额外增加40%的雪花粒子
    for i in range(num_snow_layer):
        # 垂直分布
        h_norm = random.random()
        h_dist = math.pow(h_norm, 0.25)
        y = -tree_height * 0.58 + h_dist * tree_height
        y += random.uniform(-6, 6)

        # 在树的最外层轮廓处生成雪花
        cone_boundary_r = max_base_radius * h_dist
        wave_factor = abs(math.sin(h_dist * math.pi * num_layers))
        layer_profile_scale = 0.35 + 0.65 * wave_factor
        current_layer_max_r = cone_boundary_r * layer_profile_scale

        # 雪花在最外层表面
        r_position = random.uniform(0.95, 1.15)
        r = current_layer_max_r * r_position

        # 树顶更窄
        if h_dist < 0.06:
            r = random.uniform(7, 12 * (1 - h_dist))

        # 角度分布
        theta = random.uniform(0, math.pi * 2) + h_dist * math.pi * 12

        # 添加树枝状扰动
        branch_angle = (theta % (math.pi * 2 / num_branches))
        branch_proximity = abs(branch_angle - math.pi / num_branches)
        if branch_proximity < 0.4:
            branch_strength = 1.0 - (branch_proximity / 0.4)
            branch_extension = branch_strength * random.uniform(0, 30) * (1 - h_dist * 0.3)
            r += branch_extension
            if random.random() < 0.4:
                y += random.uniform(-10, 10) * branch_strength

        x = r * math.cos(theta)
        z = r * math.sin(theta)

        # 白色雪花粒子
        snow_size = random.uniform(0.8, 2.0)
        particles.append(Particle(x, y, z, Config.WHITE, snow_size, is_snow=True))

    return particles

def generate_bright_white_ground(num_particles: int) -> List[Particle]:
    """生成波纹地面的粒子"""
    particles = []
    ground_y = 240
    max_dist = 1400

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
        x = random.uniform(-500, 1200)
        y = random.uniform(-500, 500)
        z = random.uniform(-500, 1200)
        p = Particle(x, y, z, Config.WHITE, random.uniform(0.8, 1.8))
        p.fall_speed = random.uniform(0.2, 1.8)
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

        # 径向填充
        r = math.pow(random.random(), 0.2)

        # 缩放位置
        scale = scale_base * r
        p_x = x0 * scale
        p_y = -y0 * scale + y_offset

        # 3D厚度实现蓬松效果
        max_thickness = 16.0
        z_thickness = max_thickness * math.pow(math.cos(r * math.pi / 2), 0.7)
        z_side = 1 if random.random() > 0.5 else -1
        p_z = z_thickness * z_side * random.uniform(0.9, 1.1)

        # 边缘平滑处理
        if r > 0.85:
            edge_offset = random.uniform(-0.5, 0.5)
            p_x += edge_offset * math.cos(t)
            p_y += edge_offset * math.sin(t)

        # 颜色渐变（明亮的中心，粉色的边缘）+ 金色闪光点
        sparkle_chance = random.random()

        is_snow_heart = False

        if sparkle_chance < 0.02:  # 金色大亮点
            color = Config.GOLD
            size = random.uniform(2.5, 3.8)
        elif sparkle_chance < 0.03:  # 金色小亮点
            color = Config.LIGHT_GOLD
            size = random.uniform(1.8, 2.5)
        elif r < 0.35:
            color = (255, 230, 230)  # 白色中心
            size = random.uniform(1.0, 1.6)
            is_snow_heart = True
        else:
            color = (255, 80, 110)  # 粉色边缘
            # 白色亮点
            if random.random() < 0.25:
                color = Config.WHITE  # 随机亮点
                size = random.uniform(0.6, 1.2)  # 更小的白色粒子
                is_snow_heart = True
            else:
                size = random.uniform(1.0, 1.6)

        particles.append(Particle(p_x, p_y, p_z, color, size, is_snow=is_snow_heart))

    return particles

# ============================================================================
# 音量控制UI
# ============================================================================

class VolumeControl:
    """科技感音量控制滑块"""

    def __init__(self, x: int, y: int, width: int = 150, height: int = 40):
        """
        初始化音量控制器

        Args:
            x: 控件左上角X坐标
            y: 控件左上角Y坐标
            width: 滑块总宽度
            height: 控件总高度
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # 音量状态
        self.volume = Config.DEFAULT_VOLUME
        self.is_muted = False
        self.pre_mute_volume = self.volume

        # 滑块参数
        self.slider_height = 4
        self.slider_y = y + height // 2
        self.knob_radius = 8
        self.track_left_padding = 10   # 缩短轨道左侧长度，避免靠近图标
        self.track_right_padding = 18  # 缩短轨道右侧长度
        self.track_width = max(10, self.width - self.track_left_padding - self.track_right_padding)

        # 交互状态
        self.is_dragging = False
        self.is_hovering = False

        # 图标区域（静音按钮）
        self.icon_size = 20
        self.icon_x = x - self.icon_size - 10
        self.icon_y = y + (height - self.icon_size) // 2
        self.icon_variants = self._load_icon_variants()

        # 颜色配置（半透明浅灰风格）
        self.color_active = (235, 235, 235)
        self.color_inactive = (110, 115, 125)
        self.color_hover = (255, 255, 255)
        self.color_bg = (15, 18, 25)
        self.color_border = (205, 205, 205)

    def _get_knob_x(self) -> int:
        """计算滑块旋钮的X坐标"""
        track_start = self.x + self.track_left_padding
        return int(track_start + self.volume * self.track_width)

    def _is_point_on_knob(self, px: int, py: int) -> bool:
        """检查点是否在旋钮上"""
        knob_x = self._get_knob_x()
        dist = math.sqrt((px - knob_x)**2 + (py - self.slider_y)**2)
        return dist <= self.knob_radius + 5

    def _is_point_on_icon(self, px: int, py: int) -> bool:
        """检查点是否在图标上"""
        return (self.icon_x <= px <= self.icon_x + self.icon_size and
                self.icon_y <= py <= self.icon_y + self.icon_size)

    def handle_mouse_down(self, pos: Tuple[int, int]) -> bool:
        """处理鼠标按下事件，返回是否处理了事件"""
        px, py = pos

        # 点击静音图标
        if self._is_point_on_icon(px, py):
            self.toggle_mute()
            return True

        # 点击滑块或旋钮
        track_start = self.x + self.track_left_padding
        if self._is_point_on_knob(px, py) or (
            track_start <= px <= track_start + self.track_width and
            abs(py - self.slider_y) <= 10
        ):
            self.is_dragging = True
            self._update_volume_from_mouse(px)
            return True

        return False

    def handle_mouse_up(self) -> None:
        """处理鼠标释放事件"""
        self.is_dragging = False

    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """处理鼠标移动事件"""
        px, py = pos

        # 更新悬停状态
        self.is_hovering = (
            self._is_point_on_knob(px, py) or
            self._is_point_on_icon(px, py)
        )

        # 拖拽时更新音量
        if self.is_dragging:
            self._update_volume_from_mouse(px)

    def _update_volume_from_mouse(self, mouse_x: int) -> None:
        """根据鼠标X坐标更新音量"""
        # 计算新音量
        track_start = self.x + self.track_left_padding
        track_end = track_start + self.track_width
        clamped_x = max(track_start, min(mouse_x, track_end))
        new_volume = (clamped_x - track_start) / self.track_width
        new_volume = max(0.0, min(1.0, new_volume))

        previous_volume = self.volume
        self.volume = new_volume

        if new_volume <= 0.001:
            self.volume = 0.0
            if previous_volume > 0:
                self.pre_mute_volume = previous_volume
            self.is_muted = True
        else:
            self.is_muted = False
            self.pre_mute_volume = self.volume

        # 应用音量
        self._apply_volume()

    def toggle_mute(self) -> None:
        """切换静音状态"""
        if self.is_muted:
            # 取消静音，恢复之前的音量
            self.is_muted = False
            self.volume = self.pre_mute_volume if self.pre_mute_volume > 0 else 0.5
        else:
            # 静音，保存当前音量
            self.is_muted = True
            self.pre_mute_volume = self.volume

        self._apply_volume()

    def _apply_volume(self) -> None:
        """应用音量设置到pygame混音器"""
        actual_volume = 0.0 if self.is_muted else self.volume
        pygame.mixer.music.set_volume(actual_volume)

    def draw(self, surface: pygame.Surface) -> None:
        """绘制音量控制UI"""
        container_width = self.width + self.icon_size + 30
        container_surface = pygame.Surface((container_width, self.height), pygame.SRCALPHA)
        container_rect = pygame.Rect(0, 0, container_width, self.height)
        pygame.draw.rect(container_surface, (*self.color_bg, 100), container_rect, border_radius=12)
        pygame.draw.rect(container_surface, (*self.color_border, 110), container_rect, width=1, border_radius=12)
        surface.blit(container_surface, (self.icon_x - 15, self.y))

        self._draw_icon(surface)

        track_surface = pygame.Surface((self.track_width, self.slider_height + 10), pygame.SRCALPHA)
        track_top = (track_surface.get_height() - self.slider_height) // 2
        track_rect = pygame.Rect(0, track_top, self.track_width, self.slider_height)
        pygame.draw.rect(track_surface, (255, 255, 255, 25), track_rect, border_radius=4)
        pygame.draw.rect(track_surface, (*self.color_border, 120), track_rect, width=1, border_radius=4)

        if not self.is_muted and self.volume > 0:
            filled_width = max(2, int(self.track_width * self.volume))
            fill_rect = pygame.Rect(0, track_top, filled_width, self.slider_height)
            pygame.draw.rect(track_surface, (255, 255, 255, 70), fill_rect, border_radius=4)

        track_start = self.x + self.track_left_padding
        surface.blit(track_surface, (track_start, self.slider_y - track_surface.get_height() // 2))

        knob_x = self._get_knob_x()
        knob_surface_size = self.knob_radius * 4
        knob_surface = pygame.Surface((knob_surface_size, knob_surface_size), pygame.SRCALPHA)
        knob_center = (knob_surface_size // 2, knob_surface_size // 2)
        glow_alpha = 70 if (self.is_hovering or self.is_dragging or not self.is_muted) else 35
        pygame.draw.circle(knob_surface, (255, 255, 255, glow_alpha),
                           knob_center, self.knob_radius + 4)

        knob_fill = (255, 255, 255, 85) if not self.is_muted else (180, 180, 180, 40)
        knob_border = (255, 255, 255, 140) if (self.is_hovering or self.is_dragging) else (*self.color_border, 140)
        if self.is_muted:
            knob_border = (*self.color_inactive, 120)

        pygame.draw.circle(knob_surface, knob_fill, knob_center, self.knob_radius)
        pygame.draw.circle(knob_surface, knob_border, knob_center, self.knob_radius, width=2)
        surface.blit(knob_surface, (knob_x - knob_surface_size // 2, self.slider_y - knob_surface_size // 2))

    def _draw_icon(self, surface: pygame.Surface) -> None:
        """绘制音量/静音图标"""
        png_icon = self._get_png_icon_surface()
        if png_icon:
            surface.blit(png_icon, (self.icon_x, self.icon_y))

    def _get_png_icon_surface(self) -> Optional[pygame.Surface]:
        """根据音量状态返回着色后的PNG图标"""
        if not self.icon_variants:
            return None

        state = self._get_icon_state()
        base_surface = self.icon_variants.get(state) or self.icon_variants.get('low')
        if base_surface is None:
            return None

        tint_color = self.color_inactive if self.is_muted else self.color_active
        alpha = 110 if self.is_muted else 200
        if self.is_hovering or self.is_dragging:
            alpha = min(255, alpha + 40)

        return self._tint_icon_surface(base_surface, tint_color, alpha)

    def _get_icon_state(self) -> str:
        """根据当前音量状态选择图标"""
        if self.is_muted:
            return 'muted'
        if self.volume < 0.35:
            return 'low'
        if self.volume < 0.75:
            return 'medium'
        return 'high'

    def _tint_icon_surface(self, base_surface: pygame.Surface,
                           tint_color: Tuple[int, int, int], alpha: int) -> pygame.Surface:
        """对PNG图标进行着色和透明度调整"""
        icon = base_surface.copy()
        icon.fill((*tint_color, 255), special_flags=pygame.BLEND_RGBA_MULT)

        # 使用乘法混合缩放 alpha，避免 set_alpha 导致整个图块变成纯色方块
        alpha_surface = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, alpha))
        icon.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return icon

    def _load_icon_variants(self) -> Dict[str, pygame.Surface]:
        """尝试加载不同状态的PNG音量图标"""
        variant_files = {
            'muted': 'icons/volume-x.png',
            'low': 'icons/volume.png',
            'medium': 'icons/volume-1.png',
            'high': 'icons/volume-2.png',
        }
        variants: Dict[str, pygame.Surface] = {}

        for state, file_path in variant_files.items():
            icon_surface = load_png_icon(file_path, self.icon_size)
            if icon_surface:
                variants[state] = icon_surface

        return variants


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
            self.position_y = Config.VIRTUAL_HEIGHT // 2
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
    # 使用虚拟分辨率进行布局
    text_pos_x = int(Config.VIRTUAL_WIDTH * Config.TEXT_POSITION_X_RATIO)
    multi_line_text = MultiLineText(
        lines=Config.MESSAGE_LINES,
        position_x=text_pos_x,
        position_y=Config.TEXT_POSITION_Y,
        align="left"
    )

    # 创建音量控制（右上角位置）
    volume_control = VolumeControl(
        x=Config.VIRTUAL_WIDTH - 180,
        y=20,
        width=150,
        height=40
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
                # 将实际屏幕坐标转换为虚拟坐标
                virtual_x = int((event.pos[0] - offset_x) / (scaled_width / Config.VIRTUAL_WIDTH))
                virtual_y = int((event.pos[1] - offset_y) / (scaled_height / Config.VIRTUAL_HEIGHT))
                virtual_pos = (virtual_x, virtual_y)

                # 先检查是否点击了音量控制
                if not volume_control.handle_mouse_down(virtual_pos):
                    # 如果没有点击音量控制，则处理旋转
                    rotation_controller.handle_mouse_down(event.pos[0], current_time)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                volume_control.handle_mouse_up()
                rotation_controller.handle_mouse_up(current_time)
            elif event.type == pygame.MOUSEMOTION:
                # 将实际屏幕坐标转换为虚拟坐标
                virtual_x = int((event.pos[0] - offset_x) / (scaled_width / Config.VIRTUAL_WIDTH))
                virtual_y = int((event.pos[1] - offset_y) / (scaled_height / Config.VIRTUAL_HEIGHT))
                virtual_pos = (virtual_x, virtual_y)
                volume_control.handle_mouse_motion(virtual_pos)

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

        # 渲染到虚拟表面（固定1920x1080）
        virtual_surface.fill(Config.BG_COLOR)
        for p in all_particles:
            p.draw(virtual_surface, time_seconds)

        # 绘制多行文本
        multi_line_text.draw(virtual_surface)

        # 绘制音量控制
        volume_control.draw(virtual_surface)

        # 缩放虚拟表面到实际屏幕
        screen.fill((0, 0, 0))  # 黑色背景（letterbox）
        scaled_surface = pygame.transform.scale(virtual_surface, (scaled_width, scaled_height))
        screen.blit(scaled_surface, (offset_x, offset_y))

        pygame.display.flip()
        clock.tick(Config.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
