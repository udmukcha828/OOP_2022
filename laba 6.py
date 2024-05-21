import math
import pygame
from random import choice, randint

FPS = 35

RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 201, 31)
GREEN = (0, 255, 0)
MAGENTA = (255, 3, 184)
CYAN = (0, 255, 204)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (125, 125, 125)
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 20
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = 90
        self.wall_hits = 0

    def move(self):

        gravity = 0.5
        self.vy += gravity

        self.vx *= 0.99
        self.vy *= 0.99

        self.x += self.vx
        self.y += self.vy

        if self.x < self.r:
            self.x = self.r
            self.vx *= -0.8
            self.wall_hits += 1
        elif self.x > WIDTH - self.r:
            self.x = WIDTH - self.r
            self.vx *= -0.8
            self.wall_hits += 1
        if self.y < self.r:
            self.y = self.r
            self.vy *= -0.8
            self.wall_hits += 1
        elif self.y > HEIGHT - self.r:
            self.y = HEIGHT - self.r
            self.vy *= -0.8
            self.wall_hits += 1

        if self.wall_hits >= 3:
            self.vx = 0
            self.vy = 0

        self.live -= 1

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, obj):
        return math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2) <= self.r + obj.r


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.shots = 0

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        global balls
        new_ball = Ball(self.screen)
        new_ball.r += 5
        self.an = math.atan2((450 - event.pos[1]), (event.pos[0] - 20))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = -self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10
        self.shots += 1

    def targetting(self, event):
        if event:
            self.an = math.atan2((450 - event.pos[1]), (event.pos[0] - 20))
        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def draw(self):
        pygame.draw.line(self.screen, self.color, [20, 450], [int(20 + max(self.f2_power, 20) * math.cos(self.an)),
                                                              int(450 - max(self.f2_power, 20) * math.sin(self.an))],
                         7)

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY


class Target:
    def __init__(self, screen):
        self.screen = screen
        self.x = 0
        self.y = 0
        self.r = 0
        self.color = RED
        self.shots = 0
        self.destroyed = False
        self.new_target()

    def new_target(self):
        self.x = randint(600, 780)
        self.y = randint(300, 550)
        self.r = randint(8, 50)
        self.color = choice(GAME_COLORS)
        self.shots = 0
        self.destroyed = False

    def hit(self, shots):
        self.shots = shots
        self.destroyed = True
        font = pygame.font.Font(None, 36)
        text = font.render(f"Вы уничтожили цель за {self.shots} выстрелов", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(2000)
        self.new_target()

    def draw(self):
        if not self.destroyed:
            pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen)
target = Target(screen)
finished = False

destroyed_targets = 0
shots_counter = 0

font = pygame.font.Font(None, 36)
destroyed_text = font.render(f"Уничтожено: {destroyed_targets}", True, BLACK)
shots_text = font.render(f"Попыток: {shots_counter}", True, BLACK)

while not finished:
    screen.fill(WHITE)
    gun.draw()
    target.draw()
    screen.blit(destroyed_text, (10, 10))
    screen.blit(shots_text, (WIDTH // 2 - shots_text.get_width() // 2, 10))
    for b in balls[:]:
        b.draw()
        b.move()
        if b.live <= 0 or b.wall_hits >= 3:
            balls.remove(b)
        else:
            for t in [target]:
                if b.hittest(t):
                    balls.remove(b)
                    t.hit(gun.shots)
                    destroyed_targets += 1
                    shots_counter += gun.shots
                    gun.shots = 0
                    destroyed_text = font.render(f"Уничтожено: {destroyed_targets}", True, BLACK)
                    shots_text = font.render(f"Попыток в прошлой игре: {shots_counter}", True, BLACK)
                    shots_counter = 0
    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)

    gun.power_up()

pygame.quit()
