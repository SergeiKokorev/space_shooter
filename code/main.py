import sys
import os
import pygame
from  random import randint, uniform


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, *, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))


class Player(pygame.sprite.Sprite):
    def __init__(self, groups, *, speed=300):
        super().__init__(groups)
        
        self.image = pygame.image.load(os.path.join(IMG, 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        self.__speed = speed
        self.__direction = pygame.math.Vector2()

        # cooldown section
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        # mask
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, speed: int | float):
        if not isinstance(speed, int | float):
            return None
        self.__speed = speed

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # Ship constraints
        self.rect.left = 0 if self.rect.left <= 0 else self.rect.left
        self.rect.right = WINDOW_WIDTH if self.rect.right >= WINDOW_WIDTH else self.rect.right
        self.rect.bottom = WINDOW_HEIGHT if self.rect.bottom >= WINDOW_HEIGHT else self.rect.bottom
        self.rect.top = 0 if self.rect.top <= 0 else self.rect.top

        # Ship movement
        self.__direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.__direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.__direction = self.__direction.normalize() if self.__direction else self.__direction
        self.rect.center += self.__direction * self.__speed * dt

        # Shoot laser
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser((all_sptites, laser_sprites), surf=laser_surf, pos=self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()


class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, /, speed=300,*, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = speed

    def update(self, dt):
        self.rect.centery -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, *, surf, pos):
        super().__init__(groups)
        self.original_surf = surf
        self.image = self.original_surf
        self.rect = self.image.get_frect(bottomleft = pos)
        self.__speed = randint(400, 500)
        self.__direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
        self.__rotation_speed = randint(40 ,50)
        self.__rotation = 0

    @property
    def speed(self):
        return self.__speed

    @property
    def direction(self):
        return self.__direction

    def update(self, dt):
        self.rect.center += self.__direction * self.__speed * dt
        if self.rect.top >= WINDOW_HEIGHT:
            self.kill()
        self.__rotation += self.__rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.__rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)


class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, groups, *, frames, pos):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play()

    def update(self, dt):
        self.frame_index += 10 * dt
        if self.frame_index < len(self.frames):
             self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


def display_score():

    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH /2, WINDOW_HEIGHT - 50))
    rect = pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 16).move(0, -8), 5, 10)
    display_surface.blit(text_surf, text_rect)


# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
IMG = r'images'
AUDIO = r'audio'
display = pygame.display
display.set_caption('Space shooter', '')
display_surface = display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# import
star_surf = pygame.image.load(os.path.join(IMG, 'star.png')).convert_alpha()
laser_surf = pygame.image.load(os.path.join(IMG, 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(os.path.join(IMG, 'meteor.png')).convert_alpha()
font = pygame.font.Font(os.path.join(IMG, 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(os.path.join(IMG, 'explosion', f'{i}.png')).convert_alpha()
                    for i in range(21)]

# Sounds
laser_sound = pygame.mixer.Sound(os.path.join(AUDIO, 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(os.path.join(AUDIO, 'explosion.wav'))
explosion_sound.set_volume(0.5)
game_music = pygame.mixer.Sound(os.path.join(AUDIO, 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops = -1)


# sprites
all_sptites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    Star(all_sptites, surf=star_surf)

player = Player(all_sptites)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while True:

    dt = clock.tick() / 1000
    
    # even loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == meteor_event:
            pos = (randint(0, WINDOW_WIDTH), 0)
            Meteor((all_sptites, meteor_sprites), surf=meteor_surf, pos=pos)

    # update
    all_sptites.update(dt)
    if (collision := pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)):
        pygame.quit()
        sys.exit()

    if (collision := pygame.sprite.groupcollide(laser_sprites, meteor_sprites, True, True)):
        laser = [laser for laser in collision if isinstance(laser, Laser)][0]
        AnimatedExplosion(all_sptites, frames=explosion_frames, pos=laser.rect.midtop)

    # draw the game
    display_surface.fill('#3a2e3f')
    display_score()
    all_sptites.draw(display_surface)

    pygame.display.update()

pygame.quit()
