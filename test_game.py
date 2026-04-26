import unittest
import pygame

from game_objects import Player, Enemy, FastEnemy, TankEnemy, EnemyFactory


class TestGameLogic(unittest.TestCase):
    def test_player_level_up(self):
        player = Player(100, 100)
        result = player.gain_exp(5)

        self.assertTrue(result)
        self.assertEqual(player.level, 2)

    def test_player_hp_upgrade(self):
        player = Player(100, 100)
        player.upgrade_hp()

        self.assertEqual(player.max_hp, 120)

    def test_enemy_inheritance(self):
        fast_enemy = FastEnemy(100, 100)
        tank_enemy = TankEnemy(100, 100)

        self.assertIsInstance(fast_enemy, Enemy)
        self.assertIsInstance(tank_enemy, Enemy)

    def test_factory_creates_enemy(self):
        enemy = EnemyFactory.create_enemy(100, 100)

        self.assertIsInstance(enemy, Enemy)


if __name__ == "__main__":
    pygame.init()
    unittest.main()