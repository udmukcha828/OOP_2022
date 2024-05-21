import pygame
from pygame.draw import *
from random import randint
import time

pygame.init()

FPS = 144
WIDTH = 1080
HEIGHT = 700
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 0), (255, 0, 255), (0, 255, 255)]
DURATION = 2
SPEED = 3

def new_ball():
    x = randint(100, WIDTH - 100)
    y = randint(100, HEIGHT - 100)
    r = randint(30, 50)
    color = COLORS[randint(0, 5)]
    speed_x = randint(-SPEED, SPEED)
    speed_y = randint(-SPEED, SPEED)
    return {'x': x, 'y': y, 'r': r, 'color': color, 'creation_time': time.time(), 'speed_x': speed_x, 'speed_y': speed_y}

def draw(ball):
    circle(screen, ball['color'], (ball['x'], ball['y']), ball['r'])

def alive(ball):
    return time.time() - ball['creation_time'] <= DURATION

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Ball")

balls = []
score = 0

font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()
finished = False
while not finished:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for ball in balls:
                if (ball['x'] - event.pos[0])**2 + (ball['y'] - event.pos[1])**2 <= ball['r']**2:
                    balls.remove(ball)
                    score += 1
                    break

    if len(balls) < 5 and randint(0, 100) < 10:
        balls.append(new_ball())

    balls = [ball for ball in balls if alive(ball)]

    screen.fill(BLACK)
    for ball in balls:
        draw(ball)
        ball['x'] += ball['speed_x']
        ball['y'] += ball['speed_y']
        if ball['x'] - ball['r'] < 0 or ball['x'] + ball['r'] > WIDTH:
            ball['speed_x'] *= -1
        if ball['y'] - ball['r'] < 0 or ball['y'] + ball['r'] > HEIGHT:
            ball['speed_y'] *= -1

    text = font.render(f'Счёт: {score}', True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()