import random
import sys
import pygame

from game_objects import Player, Bullet, EnemyFactory, save_high_score, load_high_score

pygame.init()

WIDTH, HEIGHT = 1200,800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival OOP")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

player = Player(WIDTH // 2, HEIGHT // 2)
bullets = []
enemies = []

wave = 1
score = 0
high_score = load_high_score()

shoot_timer = 0
game_over = False
choosing_upgrade = False


def spawn_wave(wave_number):
    for _ in range(wave_number * 3):
        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            x, y = random.randint(0, WIDTH), -20
        elif side == "bottom":
            x, y = random.randint(0, WIDTH), HEIGHT + 20
        elif side == "left":
            x, y = -20, random.randint(0, HEIGHT)
        else:
            x, y = WIDTH + 20, random.randint(0, HEIGHT)

        enemies.append(EnemyFactory.create_enemy(x, y))


def restart_game():
    global player, bullets, enemies, wave, score, shoot_timer
    global game_over, choosing_upgrade, high_score

    player = Player(WIDTH // 2, HEIGHT // 2)
    bullets = []
    enemies = []
    wave = 1
    score = 0
    shoot_timer = 0
    game_over = False
    choosing_upgrade = False
    high_score = load_high_score()
    spawn_wave(wave)


spawn_wave(wave)

running = True

while running:
    dt = clock.tick(60) / 1000
    shoot_timer -= dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if choosing_upgrade:
        if keys[pygame.K_1]:
            player.upgrade_hp()
            choosing_upgrade = False
        elif keys[pygame.K_2]:
            player.upgrade_fire_rate()
            choosing_upgrade = False
        elif keys[pygame.K_3]:
            player.upgrade_speed()
            choosing_upgrade = False

    if not game_over and not choosing_upgrade:
        player.move(keys, dt, WIDTH, HEIGHT)

        if pygame.mouse.get_pressed()[0] and shoot_timer <= 0:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            direction = mouse_pos - player.position

            if direction.length() > 0:
                direction = direction.normalize()
                bullets.append(Bullet(player.position.x, player.position.y, direction))
                shoot_timer = player.shoot_cooldown

        for bullet in bullets:
            bullet.update(dt)

        bullets = [
            bullet for bullet in bullets
            if 0 < bullet.position.x < WIDTH and 0 < bullet.position.y < HEIGHT
        ]

        for enemy in enemies:
            enemy.update(player.position, dt)

        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.position.distance_to(enemy.position) < bullet.radius + enemy.radius:
                    bullets.remove(bullet)
                    enemy.hp -= 1

                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                        score += 1
                        leveled_up = player.gain_exp(enemy.exp_reward)

                        if leveled_up:
                            choosing_upgrade = True

                    break

        for enemy in enemies[:]:
            if player.position.distance_to(enemy.position) < player.radius + enemy.radius:
                enemies.remove(enemy)
                player.hp -= enemy.damage

        if len(enemies) == 0:
            wave += 1
            spawn_wave(wave)

        if player.hp <= 0:
            game_over = True
            if score > high_score:
                high_score = score
                save_high_score(high_score)

    elif game_over:
        if keys[pygame.K_r]:
            restart_game()

    screen.fill((30, 30, 30))
    # HP BAR
    hp_ratio = player.hp / player.max_hp
    pygame.draw.rect(screen, (80, 80, 80), (10, 10, 200, 20))
    pygame.draw.rect(screen, (50, 200, 80), (10, 10, 200 * hp_ratio, 20))
    pygame.draw.rect(screen, (255, 255, 255), (10, 10, 200, 20), 2)

    # EXP bar
    bar_x, bar_y = 250, 20
    bar_width, bar_height = 400, 20
    bar_x=WIDTH // 2 - bar_width // 2
    exp_ratio = player.exp / player.exp_to_next

    pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (80, 180, 255), (bar_x, bar_y, bar_width * exp_ratio, bar_height))
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    player.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)
        if enemy.__class__.__name__ == "TankEnemy":
            pygame.draw.circle(screen, (255, 255, 255), enemy.position, enemy.radius, 3)
        elif enemy.__class__.__name__ == "FastEnemy":
            pygame.draw.circle(screen, (255, 255, 255), enemy.position, enemy.radius, 1)

    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    wave_text = font.render(f"Wave: {wave}", True, (255, 255, 255))
    level_text = font.render(f"Level: {player.level}", True, (255, 255, 255))
    exp_text = font.render(f"EXP: {player.exp}/{player.exp_to_next}", True, (255, 255, 255))

    screen.blit(hp_text, (10, 40))
    screen.blit(score_text, (10, 80))
    screen.blit(high_score_text, (10, 120))
    screen.blit(wave_text, (10, 160))

    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 90))
    screen.blit(exp_text, (WIDTH // 2 - exp_text.get_width() // 2, 120))

    

    if choosing_upgrade:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = font.render("LEVEL UP! Choose Upgrade:", True, (255, 255, 255))
        opt1 = font.render("1 - +20 Max HP", True, (200, 255, 200))
        opt2 = font.render("2 - Faster Shooting", True, (200, 200, 255))
        opt3 = font.render("3 - Faster Movement", True, (255, 200, 200))

        screen.blit(title, (320, 200))
        screen.blit(opt1, (350, 260))
        screen.blit(opt2, (350, 300))
        screen.blit(opt3, (350, 340))

    if game_over:
        over_text = font.render("GAME OVER - Press R to restart", True, (255, 0, 0))
        screen.blit(over_text, (280, 300))

    pygame.display.flip()

pygame.quit()
sys.exit()
