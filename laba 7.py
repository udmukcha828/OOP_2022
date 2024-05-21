import math
import pygame
from random import choice, randint
import time

FPS = 40

# Перенесение цветовой палитры в константы
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

# Установка ширины и высоты экрана
WIDTH = 800
HEIGHT = 600

# Класс Ball
# Класс Ball
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

    # Переименование и оптимизация метода движения
    def move(self):
        gravity = 0.5
        self.vy += gravity

        self.vx *= 0.99
        self.vy *= 0.99

        # Проверка столкновения со стенами
        self.x = max(self.r, min(self.x + self.vx, WIDTH - self.r))
        self.y = max(self.r, min(self.y + self.vy, HEIGHT - self.r))

        # Обработка столкновений с верхней и нижней стеной
        if self.y == self.r or self.y == HEIGHT - self.r:
            self.vy *= -0.8
            self.wall_hits += 1

        # Обработка столкновений с боковыми стенами
        if self.x == self.r or self.x == WIDTH - self.r:
            self.vx *= -0.8
            self.wall_hits += 1

        # Остановка мяча после трех столкновений со стенами
        if self.wall_hits >= 3:
            self.vx = 0
            self.vy = 0

        self.live -= 1

    # Метод отрисовки мяча
    def draw(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)

    
    # Метод проверки столкновения с другим объектом
    def hittest(self, obj):
        # Получаем расстояние между центрами снаряда и цели
        distance = math.sqrt((self.x - obj.x)**2 + (self.y - obj.y)**2)

        # Коэффициент масштабирования
        scale_factor = 0.8

        # Проверяем, находится ли снаряд достаточно близко к цели с учетом масштабирования
        if distance <= scale_factor * (self.r + obj.r):
            return True
        else:
            return False

# Класс SquareBall
class SquareBall(Ball):
    def draw(self):
        pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2))


# Класс Gun
class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = False  # Замена числового значения на булево
        self.an = 1
        self.color = GREY
        self.shots = 0
        self.y_pos = 450  # Начальное положение пушки
        self.y_direction = 1  # Направление движения пушки: 1 - вниз, -1 - вверх

    # Переименование и оптимизация метода запуска выстрела
    def fire2_start(self, event):
        self.f2_on = True

    # Переименование и оптимизация метода окончания выстрела
    def fire2_end(self, event):
        global balls
        new_ball = choice([Ball(self.screen), SquareBall(self.screen)])  # Случайный выбор формы снаряда
        # Изменения в зависимости от направления движения пушки
        new_ball.y = self.y_pos + 20 * self.y_direction
        new_ball.r += 5
        self.an = math.atan2((450 - event.pos[1]), (event.pos[0] - 20))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = -self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = False
        self.f2_power = 10
        self.shots += 1

    # Переименование и оптимизация метода прицеливания
    def targetting(self, event):
        if event:
            self.an = math.atan2((450 - event.pos[1]), (event.pos[0] - 20))
        self.color = RED if self.f2_on else GREY  # Использование тернарного оператора

    # Оптимизация метода отрисовки пушки
    def draw(self):
        pygame.draw.line(self.screen, self.color, [20, self.y_pos], [
                         int(20 + max(self.f2_power, 20) * math.cos(self.an)),
                         int(self.y_pos - max(self.f2_power, 20) * math.sin(self.an))], 7)

    # Переименование и оптимизация метода увеличения мощности выстрела
    def power_up(self):
        if self.f2_on and self.f2_power < 100:  # Условие можно упростить
            self.f2_power += 1
            self.color = RED  # Установка цвета снаряда в процессе зарядки

    # Метод движения пушки
    def move(self):
        self.y_pos += self.y_direction * 5  # Скорость движения пушки
        # Ограничение движения пушки по вертикали
        if self.y_pos >= HEIGHT - 50:
            self.y_direction = -1
        elif self.y_pos <= 150:
            self.y_direction = 1


# Класс Target
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

    # Метод создания новой цели
    def new_target(self):
        self.x = randint(600, 780)
        self.y = randint(300, 550)
        self.r = randint(8, 50)
        self.color = choice(GAME_COLORS)
        self.shots = 0
        self.destroyed = False

    # Метод попадания в цель
    def hit(self, shots):
        self.shots = shots
        self.destroyed = True
        font = pygame.font.Font(None, 36)
        text = font.render(
            f"Вы уничтожили цель за {self.shots} выстрелов", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(20)
        time.sleep(1.5)
        self.new_target()

    # Метод отрисовки цели
    def draw(self):
        if not self.destroyed:
            pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)

    def get_rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)


# Класс MovingTarget, наследующийся от Target
class MovingTarget(Target):
    def __init__(self, screen):
        super().__init__(screen)
        self.vx = randint(1, 3)
        self.vy = randint(1, 3)

    # Переопределение метода движения цели
    def move(self):
        self.x += self.vx
        self.y += self.vy

        if self.x < 0 or self.x > WIDTH:
            self.vx *= -1
        if self.y < 0 or self.y > HEIGHT:
            self.vy *= -1

    # Переопределение метода создания новой цели для учёта скорости
    def new_target(self):
        super().new_target()
        self.vx = randint(1, 3)
        self.vy = randint(1, 3)


# Класс SquareTarget
class SquareTarget(Target):
    def draw(self):
        pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2))


# Инициализация pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
balls = []
clock = pygame.time.Clock()
gun = Gun(screen)
targets = [Target(screen), SquareTarget(screen)]  # Создание двух статичных целей разных форм
moving_target = MovingTarget(screen)  # Создание движущейся цели
finished = False

destroyed_targets = 0
shots_counter = 0

font = pygame.font.Font(None, 36)
destroyed_text = font.render(f"Уничтожено: {destroyed_targets}", True, BLACK)
shots_text = font.render(
    f"Попыток: {shots_counter}", True, BLACK)

# Основной игровой цикл
while not finished:
    screen.fill(WHITE)
    gun.draw()
    gun.move()  # Движение пушки

    # Обновляем и рисуем все цели
    for target in targets:
        target.draw()
    moving_target.draw()

    # Рисуем текст
    screen.blit(destroyed_text, (10, 10))
    screen.blit(shots_text, (WIDTH // 2 - shots_text.get_width() // 2, 10))

    # Обработка снарядов
    for b in balls[:]:
        b.draw()
        b.move()
        if b.live <= 0 or b.wall_hits >= 3:
            balls.remove(b)
        else:
            for t in targets + [moving_target]:
                if b.hittest(t):
                    balls.remove(b)
                    t.hit(gun.shots)
                    destroyed_targets += 1
                    shots_counter += gun.shots
                    gun.shots = 0
                    destroyed_text = font.render(
                        f"Уничтожено: {destroyed_targets}", True, BLACK)
                    shots_text = font.render(
                        f"Попыток в прошлой игре: {shots_counter}", True, BLACK)
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

    # Движение движущейся цели
    moving_target.move()

pygame.quit()