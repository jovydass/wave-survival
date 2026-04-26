import random
import pygame


class GameObject:
    def __init__(self, x, y, radius, color):
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)


class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 20, (50, 200, 80))
        self.speed = 300
        self.max_hp = 100
        self.hp = self.max_hp
        self.level = 1
        self.exp = 0
        self.exp_to_next = 5
        self.shoot_cooldown = 0.2

    def move(self, keys, dt, width, height):
        movement = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_s]:
            movement.y += 1
        if keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_d]:
            movement.x += 1

        if movement.length() > 0:
            movement = movement.normalize()

        self.position += movement * self.speed * dt
        self.position.x = max(self.radius, min(width - self.radius, self.position.x))
        self.position.y = max(self.radius, min(height - self.radius, self.position.y))

    def gain_exp(self, amount):
        self.exp += amount

        if self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next += 5
            return True

        return False

    def upgrade_hp(self):
        self.max_hp += 20
        self.hp = min(self.max_hp, self.hp + 20)

    def upgrade_fire_rate(self):
        self.shoot_cooldown = max(0.05, self.shoot_cooldown - 0.03)

    def upgrade_speed(self):
        self.speed += 40


class Bullet(GameObject):
    def __init__(self, x, y, direction):
        super().__init__(x, y, 5, (255, 255, 0))
        self.direction = direction
        self.speed = 600

    def update(self, dt):
        self.position += self.direction * self.speed * dt


class Enemy(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 15, (220, 50, 50))
        self.speed = 120
        self.damage = 10
        self.exp_reward = 1
        self.hp = 1

    def update(self, player_pos, dt):
        direction = player_pos - self.position
        if direction.length() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt


class FastEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 10
        self.color = (255, 180, 40)
        self.speed = 230
        self.damage = 5
        self.exp_reward = 2


class TankEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 28
        self.color = (120, 60, 200)
        self.speed = 75
        self.damage = 20
        self.exp_reward = 4
        self.hp = 3


class EnemyFactory:
    @staticmethod
    def create_enemy(x, y):
        enemy_type = random.choice(["normal", "fast", "tank"])

        if enemy_type == "fast":
            return FastEnemy(x, y)
        if enemy_type == "tank":
            return TankEnemy(x, y)

        return Enemy(x, y)


def save_high_score(score, filename="highscore.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(score))


def load_high_score(filename="highscore.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0