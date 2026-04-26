import pygame
import sys
import random

pygame.init()

# --- SETTINGS ---
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival")

clock = pygame.time.Clock()

# --- PLAYER ---
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 300
player_radius = 20
max_hp = 100
player_hp = max_hp

# --- LEVEL SYSTEM ---
level = 1
exp = 0
exp_to_next = 5
level_up_text_timer = 0
last_upgrade_text = ""

# --- BULLETS ---
bullets = []
bullet_speed = 600
bullet_radius = 5

# --- ENEMIES ---
enemies = []

# --- GAME ---
wave = 1
score = 0

shoot_cooldown = 0.2
shoot_timer = 0

font = pygame.font.SysFont(None, 36)

# --- ENEMY TYPES ---
def create_enemy(pos):
    enemy_type = random.choice(["normal", "fast", "tank"])

    if enemy_type == "normal":
        return {
            "type": "normal",
            "pos": pos,
            "speed": 120,
            "radius": 15,
            "color": (220, 50, 50),
            "damage": 10,
            "exp": 1,
            "hp": 1
        }

    elif enemy_type == "fast":
        return {
            "type": "fast",
            "pos": pos,
            "speed": 230,
            "radius": 10,
            "color": (255, 180, 40),
            "damage": 5,
            "exp": 2,
            "hp": 1
        }

    else:  # tank
        return {
            "type": "tank",
            "pos": pos,
            "speed": 75,
            "radius": 28,
            "color": (120, 60, 200),
            "damage": 20,
            "exp": 4,
            "hp": 3
        }

# --- SPAWN ---
def spawn_wave(wave):
    for _ in range(wave * 3):
        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            pos = pygame.Vector2(random.randint(0, WIDTH), -20)
        elif side == "bottom":
            pos = pygame.Vector2(random.randint(0, WIDTH), HEIGHT + 20)
        elif side == "left":
            pos = pygame.Vector2(-20, random.randint(0, HEIGHT))
        else:
            pos = pygame.Vector2(WIDTH + 20, random.randint(0, HEIGHT))

        enemies.append(create_enemy(pos))

spawn_wave(wave)

# --- EXP SYSTEM ---
def gain_exp(amount):
    global exp, level, exp_to_next, max_hp, player_hp
    global shoot_cooldown, player_speed, level_up_text_timer, last_upgrade_text

    exp += amount

    while exp >= exp_to_next:
        exp -= exp_to_next
        level += 1
        exp_to_next += 5

        max_hp += 10
        player_hp = min(max_hp, player_hp + 20)

        shoot_cooldown = max(0.08, shoot_cooldown - 0.02)
        player_speed += 10

        last_upgrade_text = "+10 Max HP, +Speed, +Fire Rate"
        level_up_text_timer = 2.0

running = True
game_over = False

while running:
    dt = clock.tick(60) / 1000
    shoot_timer -= dt
    if level_up_text_timer > 0:
        level_up_text_timer -= dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        # --- MOVEMENT ---
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1

        if move.length() > 0:
            move = move.normalize()

        player_pos += move * player_speed * dt

        # bounds
        player_pos.x = max(player_radius, min(WIDTH - player_radius, player_pos.x))
        player_pos.y = max(player_radius, min(HEIGHT - player_radius, player_pos.y))

        # --- SHOOTING ---
        if pygame.mouse.get_pressed()[0] and shoot_timer <= 0:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            direction_vector = mouse_pos - player_pos

            if direction_vector.length() > 0:
                direction = direction_vector.normalize()
                bullets.append([player_pos.copy(), direction])
                shoot_timer = shoot_cooldown

        # --- BULLETS ---
        for bullet in bullets:
            bullet[0] += bullet[1] * bullet_speed * dt

        bullets[:] = [b for b in bullets if 0 < b[0].x < WIDTH and 0 < b[0].y < HEIGHT]

        # --- ENEMY MOVE ---
        for enemy in enemies:
            direction = (player_pos - enemy["pos"]).normalize()
            enemy["pos"] += direction * enemy["speed"] * dt

        # --- COLLISIONS ---
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet[0].distance_to(enemy["pos"]) < bullet_radius + enemy["radius"]:
                    bullets.remove(bullet)
                    enemy["hp"] -= 1

                    if enemy["hp"] <= 0:
                        enemies.remove(enemy)
                        score += 1
                        gain_exp(enemy["exp"])

                    break

        for enemy in enemies[:]:
            if player_pos.distance_to(enemy["pos"]) < player_radius + enemy["radius"]:
                enemies.remove(enemy)
                player_hp -= enemy["damage"]

        # --- NEXT WAVE ---
        if len(enemies) == 0:
            wave += 1
            spawn_wave(wave)

        # --- GAME OVER ---
        if player_hp <= 0:
            game_over = True

    else:
        if keys[pygame.K_r]:
            player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)

            bullets.clear()
            enemies.clear()

            max_hp = 100
            player_hp = max_hp

            level = 1
            exp = 0
            exp_to_next = 5

            wave = 1
            score = 0

            shoot_cooldown = 0.2
            shoot_timer = 0
            player_speed = 300

            spawn_wave(wave)
            game_over = False

    # --- DRAW ---
    screen.fill((30, 30, 30))

    # EXP BAR
    bar_x = 250
    bar_y = 20
    bar_width = 500
    bar_height = 20

    exp_ratio = exp / exp_to_next
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (80, 180, 255), (bar_x, bar_y, bar_width * exp_ratio, bar_height))
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    bar_text = font.render(f"Level {level}  EXP {exp}/{exp_to_next}", True, (255, 255, 255))
    screen.blit(bar_text, (bar_x + 130, bar_y + 25))

    pygame.draw.circle(screen, (50, 200, 80), player_pos, player_radius)

    for bullet in bullets:
        pygame.draw.circle(screen, (255, 255, 0), bullet[0], bullet_radius)

    for enemy in enemies:
        pygame.draw.circle(screen, enemy["color"], enemy["pos"], enemy["radius"])

    # UI
    hp_text = font.render(f"HP: {player_hp}/{max_hp}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    wave_text = font.render(f"Wave: {wave}", True, (255, 255, 255))
    

    screen.blit(hp_text, (10, 10))
    screen.blit(score_text, (10, 40))
    screen.blit(wave_text, (10, 70))
  

    if level_up_text_timer > 0:
        upgrade_text = font.render(f"LEVEL UP! {last_upgrade_text}", True, (80, 220, 255))
        screen.blit(upgrade_text, (330, 80))

    if game_over:
        over_text = font.render("GAME OVER - Press R to restart", True, (255, 0, 0))
        screen.blit(over_text, (250, 300))

    pygame.display.flip()

pygame.quit()
sys.exit()