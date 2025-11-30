import pygame
import math
import random

# --- 初始化 ---
pygame.init()
WIDTH, HEIGHT = 1440, 900 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Final Heart Christmas Tree")
clock = pygame.time.Clock()

# --- 资源加载 ---
try:
    font_path = pygame.font.match_font('times new roman', bold=True)
    if not font_path:
         font_path = pygame.font.match_font('arial', bold=True)
    font = pygame.font.Font(font_path, 45)
except:
    font = pygame.font.SysFont("serif", 45, bold=True)

# --- 颜色定义 ---
BG_COLOR = (25, 28, 35) 
WHITE = (255, 255, 255)

TREE_COLORS = [
    (255, 180, 190), # 柔粉
    (255, 100, 150), # 玫红
    (255, 215, 0),   # 金色
    (255, 250, 240), # 亮白
    (200, 240, 255), # 冰蓝
    (220, 20, 60)    # 深红
]

GROUND_BASE_COLOR = (225, 225, 230) 

# --- 粒子类 ---
class Particle:
    def __init__(self, x, y, z, color, size_base):
        self.x, self.y, self.z = x, y, z
        self.orig_x, self.orig_y, self.orig_z = x, y, z
        self.color = color 
        self.size_base = size_base
        
        self.flicker_speed = random.uniform(2.0, 5.0)
        self.flicker_offset = random.uniform(0, math.pi * 2)
        self.fall_speed = 0 

    def rotate_y(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        self.x = self.orig_x * cos_a - self.orig_z * sin_a
        self.z = self.orig_x * sin_a + self.orig_z * cos_a

    def draw(self, surface, time_input):
        FOV = 500
        VIEW_DIST = 650 
        
        if VIEW_DIST + self.z <= 20: return

        # 景深雾化
        fog_start_z = 50.0  
        fog_end_z = 700.0   
        fog_factor = (self.z - fog_start_z) / (fog_end_z - fog_start_z)
        fog_factor = max(0.0, min(1.0, fog_factor))
        
        # 颜色混合
        r_c = int(self.color[0] * (1 - fog_factor) + BG_COLOR[0] * fog_factor)
        g_c = int(self.color[1] * (1 - fog_factor) + BG_COLOR[1] * fog_factor)
        b_c = int(self.color[2] * (1 - fog_factor) + BG_COLOR[2] * fog_factor)
        final_color = (r_c, g_c, b_c)

        scale = FOV / (VIEW_DIST + self.z)
        center_offset_x = int(WIDTH * 0.6) 
        
        x_2d = int(self.x * scale + center_offset_x)
        y_2d = int(self.y * scale + HEIGHT // 2 + 100) 

        flicker = math.sin(time_input * self.flicker_speed + self.flicker_offset)
        current_size = self.size_base * scale * (0.8 + 0.4 * flicker)
        
        # 优化绘制：即使是小粒子，如果足够亮，也尽量画出来
        if current_size <= 1.2:
             if current_size > 0.5 or random.random() < 0.6:
                surface.set_at((x_2d, y_2d), final_color)
        else:
            r_size = int(current_size)
            pygame.draw.circle(surface, final_color, (x_2d, y_2d), r_size)
            
            # 辉光
            if r_size > 3 and self.fall_speed == 0 and fog_factor < 0.5: 
                 glow_radius = int(r_size * 1.4)
                 glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                 glow_alpha = int(30 * (1 - fog_factor))
                 pygame.draw.circle(glow_surf, (*final_color, glow_alpha), (glow_radius, glow_radius), glow_radius)
                 surface.blit(glow_surf, (x_2d - glow_radius, y_2d - glow_radius), special_flags=pygame.BLEND_ADD)

# --- 生成器函数 ---

def generate_ragged_tree(num_particles):
    particles = []
    tree_height = 580
    max_base_radius = 210
    num_layers = 9
    
    for i in range(num_particles):
        h_norm = i / num_particles
        h_dist = math.pow(h_norm, 0.75)
        y = -tree_height * 0.58 + h_dist * tree_height
        y += random.uniform(-4, 4)
        cone_boundary_r = max_base_radius * h_dist
        wave_factor = abs(math.sin(h_dist * math.pi * num_layers))
        layer_profile_scale = 0.25 + 0.75 * wave_factor
        current_layer_max_r = cone_boundary_r * layer_profile_scale
        r_scatter = math.pow(random.random(), 0.35)
        r = current_layer_max_r * r_scatter
        turbulence_scale = random.uniform(0.85, 1.3) 
        if random.random() < 0.05: turbulence_scale = 1.5 
        r *= turbulence_scale
        if h_dist < 0.06: r = random.uniform(0, 8 * (1-h_dist))
        theta = random.uniform(0, math.pi * 2) + h_dist * math.pi * 12 
        x = r * math.cos(theta)
        z = r * math.sin(theta)
        color = random.choice(TREE_COLORS)
        if h_dist < 0.08: color = WHITE
        elif r_scatter < 0.4: color = tuple(max(0, c - 50) for c in color)
        size = random.uniform(0.6, 2.0)
        if turbulence_scale > 1.3:
            size = random.uniform(2.0, 3.0)
            color = WHITE
        particles.append(Particle(x, y, z, color, size))
    return particles

def generate_bright_white_ground(num_particles):
    particles = []
    ground_y = 240
    max_dist = 950 
    for i in range(num_particles):
        angle = random.uniform(0, math.pi * 2)
        dist = math.sqrt(random.random()) * max_dist 
        x = dist * math.cos(angle)
        z = dist * math.sin(angle)
        ripple_val = math.sin(dist / 35.0 - 2.0)
        brightness_offset = int(ripple_val * 25)
        base_r, base_g, base_b = GROUND_BASE_COLOR
        r = max(0, min(255, base_r + brightness_offset))
        g = max(0, min(255, base_g + brightness_offset))
        b = max(0, min(255, base_b + brightness_offset + 5))
        color = (r, g, b)
        size = random.uniform(0.5, 1.5)
        particles.append(Particle(x, ground_y, z, color, size))
    return particles

def generate_snow(num_particles):
    particles = []
    for i in range(num_particles):
        x = random.uniform(-500, 500)
        y = random.uniform(-500, 300)
        z = random.uniform(-500, 500)
        p = Particle(x, y, z, WHITE, random.uniform(0.8, 1.8))
        p.fall_speed = random.uniform(0.2, 0.6)
        particles.append(p)
    return particles

# 【修改】更鼓、更小、更亮的抱枕心形
def generate_pillow_heart(num_particles):
    particles = []
    # 1. 缩放从 5.2 降到 4.0 (更小)
    scale_base = 4.0
    # 调整位置适配树尖
    y_offset = -415 
    
    for i in range(num_particles):
        t = random.uniform(0, math.pi * 2)
        # 心形曲线
        x0 = 16 * math.sin(t)**3
        y0 = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        
        # r: 0 (中心) -> 1 (边缘)
        r = math.pow(random.random(), 0.3)
        
        scale = scale_base * r
        p_x = x0 * scale
        p_y = -y0 * scale + y_offset
        
        # 2. 更鼓 (Puffier)
        # 增大 Z 轴厚度系数 (相对于较小的scale，这个数值会让它看起来很厚实)
        max_thickness = 13.0 
        z_thickness = max_thickness * math.cos(r * math.pi / 2)
        
        # 随机正负，并强烈推向表面，形成"皮"的感觉
        z_side = 1 if random.random() > 0.5 else -1
        # random.uniform(0.8, 1.2) 让表面有一点点粗糙度，像亮片
        p_z = z_thickness * z_side * random.uniform(0.8, 1.2)
        
        # 3. 更亮 (Brighter)
        if r < 0.4: 
             # 中心几乎纯白发光
             color = (255, 230, 230) 
        else:
             # 边缘也是很亮的亮粉红
             color = (255, 80, 110)
             # 随机加入纯白亮点
             if random.random() < 0.15: color = WHITE

        # 4. 材质控制 (Texture)
        # 粒子大小差异不要太大: 0.9 ~ 1.5
        # 这样看起来像均匀的小灯珠组成的
        size = random.uniform(0.9, 1.5)

        particles.append(Particle(p_x, p_y, p_z, color, size))
    return particles

# --- 主程序 ---
def main():
    running = True
    
    print("Generating Particles...")
    tree_p = generate_ragged_tree(6000) 
    # 保持高密度 2000
    heart_p = generate_pillow_heart(2000)
    ground_p = generate_bright_white_ground(12000)
    snow_p = generate_snow(600)
    
    rotating_objects = tree_p + heart_p + ground_p
    
    rotation_angle = 0.0          
    rotation_velocity = 0.0       
    is_dragging = False           
    last_mouse_x = 0              
    last_interaction_time = 0     
    
    AUTO_SPEED = 0.003            
    FRICTION = 0.95               
    SENSITIVITY = 0.005           
    IDLE_TIMEOUT = 2000           
    RESUME_SMOOTHNESS = 0.02      

    text_surf = font.render("Merry Christmas", True, WHITE)
    text_rect = text_surf.get_rect(center=(WIDTH * 0.25, HEIGHT // 2))
    shadow_surf = font.render("Merry Christmas", True, (0, 0, 0))
    shadow_rect = shadow_surf.get_rect(center=(WIDTH * 0.25 + 2, HEIGHT // 2 + 2))

    start_ticks = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    is_dragging = True
                    last_mouse_x = event.pos[0]
                    last_interaction_time = current_time
                    rotation_velocity = 0 
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False
                    last_interaction_time = current_time
        
        if is_dragging:
            mouse_x, _ = pygame.mouse.get_pos()
            delta_x = mouse_x - last_mouse_x
            rotation_velocity = delta_x * SENSITIVITY
            last_mouse_x = mouse_x
            last_interaction_time = current_time
        else:
            time_since_last_interact = current_time - last_interaction_time
            if time_since_last_interact > IDLE_TIMEOUT:
                rotation_velocity = rotation_velocity * (1 - RESUME_SMOOTHNESS) + AUTO_SPEED * RESUME_SMOOTHNESS
            else:
                rotation_velocity *= FRICTION

        rotation_angle += rotation_velocity
        
        time_now = (current_time - start_ticks) / 1000.0
        
        screen.fill(BG_COLOR)
        
        for p in rotating_objects:
            p.rotate_y(rotation_angle)
            
        for p in snow_p:
            p.y += p.fall_speed
            if p.y > 250: 
                p.y = -500
                p.x = random.uniform(-500, 500)
                p.z = random.uniform(-500, 500)
        
        all_draw_particles = rotating_objects + snow_p
        all_draw_particles.sort(key=lambda p: p.z, reverse=True)
        
        for p in all_draw_particles:
            p.draw(screen, time_now)
            
        screen.blit(shadow_surf, shadow_rect)
        screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()