import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SPEED = 5
PLAYER_HEALTH = 3
BULLET_SPEED = 10
BULLET_COOLDOWN = 500  # Time in milliseconds between bullets
ENEMY_SPEED = 1
ENEMY_BULLET_SPEED = 5
ENEMY_SHOOT_DELAY = 2000  # Time in milliseconds between enemy shots
POWER_UP_DURATION = 5000  # Duration power-ups last
POWER_UP_COOLDOWN = 30000  # Time in milliseconds between power-ups
INITIAL_CURRENCY = 100
UPGRADE_COST = 50

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load assets
def load_asset(file):
    try:
        return pygame.image.load(file)
    except pygame.error as e:
        print(f"Error loading asset {file}: {e}")
        sys.exit(1)

player_img = load_asset('player.png')
bullet_img = load_asset('bullet.png')
enemy_img = load_asset('enemy1.png')
enemy_bullet_img = load_asset('enemy_bullet.png')
background_img = load_asset('background.png')
powerup_img = load_asset('powerup.png')
mute_music_img = load_asset('mute_music.png')
mute_sound_img = load_asset('mute_sound.png')

# Load sounds
def load_sound(file):
    try:
        return pygame.mixer.Sound(file)
    except pygame.error as e:
        print(f"Error loading sound {file}: {e}")
        return None

shoot_sound = load_sound("shoot.mp3")
explosion_sound = load_sound("explosion.mp3")
try:
    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Error loading background music: {e}")

# Flags for muting
music_muted = False
sound_muted = False

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(400, 550))
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.font = pygame.font.Font(None, 36)
        self.last_shot_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE] and pygame.time.get_ticks() - self.last_shot_time > BULLET_COOLDOWN:
            bullet = Bullet(self.rect.midtop)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.last_shot_time = pygame.time.get_ticks()
            if not sound_muted and shoot_sound:
                shoot_sound.play()

    def draw_health(self, surface):
        health_text = self.font.render(f'Health: {self.health}', True, (255, 255, 255))
        surface.blit(health_text, (10, 10))


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(midbottom=position)
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH-20), -20))
        self.speed = ENEMY_SPEED
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        # Enemy shooting
        if pygame.time.get_ticks() - self.last_shot_time > ENEMY_SHOOT_DELAY:
            enemy_bullet = EnemyBullet(self.rect.midbottom)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
            self.last_shot_time = pygame.time.get_ticks()

# Enemy Bullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect(midtop=position)
        self.speed = ENEMY_BULLET_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = powerup_img
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH-20), -20))
        self.speed = ENEMY_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Game Manager class
class GameManager:
    def __init__(self):
        self.currency = INITIAL_CURRENCY
        self.last_powerup_time = 0

    def start_game(self):
        self.new_level()
        self.main_loop()

    def new_level(self):
        for _ in range(5):
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

    # other methods...
    def main_loop(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            all_sprites.update()
            self.check_collisions()
            self.check_power_ups()
            self.update_power_ups()
            self.draw()
            clock.tick(60)

    def handle_events(self):
        global music_muted, sound_muted
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.open_shop()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 700 <= event.pos[0] <= 760 and 20 <= event.pos[1] <= 80:
                    music_muted = not music_muted
                    if music_muted:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif 700 <= event.pos[0] <= 760 and 80 <= event.pos[1] <= 140:
                    sound_muted = not sound_muted

    def check_collisions(self):
        global player
        if pygame.sprite.spritecollide(player, enemies, True):
            player.health -= 1
            if player.health <= 0:
                self.game_over()
            if not sound_muted and explosion_sound:
                explosion_sound.play()

        if pygame.sprite.groupcollide(bullets, enemies, True, True):
            self.currency += 10
            if not sound_muted and explosion_sound:
                explosion_sound.play()

        if pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.health -= 1
            if player.health <= 0:
                self.game_over()

            if pygame.sprite.spritecollide(player, power_ups, True):
                player.health += 1


    def check_power_ups(self):
        if pygame.time.get_ticks() - self.last_powerup_time > POWER_UP_COOLDOWN:
            power_up = PowerUp()
            all_sprites.add(power_up)
            power_ups.add(power_up)
            self.last_powerup_time = pygame.time.get_ticks()

    def update_power_ups(self):
        pass  # Implement power-up effects here

    def draw(self):
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        player.draw_health(screen)
        self.draw_ui(screen)
        pygame.display.flip()

    def draw_ui(self, surface):
        font = pygame.font.Font(None, 36)
        currency_text = font.render(f'Currency: {self.currency}', True, (255, 255, 255))
        surface.blit(currency_text, (10, 50))

    def game_over(self):
        print("Game Over")
        pygame.quit()
        sys.exit()

    def open_shop(self):
        shop_open = True
        while shop_open:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1 and self.currency >= UPGRADE_COST:
                        player.health += 1
                        self.currency -= UPGRADE_COST
                    elif event.key == pygame.K_2 and self.currency >= UPGRADE_COST:
                        player.speed += 1
                        self.currency -= UPGRADE_COST
                    elif event.key == pygame.K_3 and self.currency >= UPGRADE_COST:
                        # Implement bullet power upgrade
                        self.currency -= UPGRADE_COST
                    elif event.key == pygame.K_q:
                        shop_open = False

# Initialize player, sprites, and groups
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
power_ups = pygame.sprite.Group()

game_manager = GameManager()
game_manager.start_game()

