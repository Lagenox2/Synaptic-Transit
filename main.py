import pygame
from screeninfo import get_monitors
import sys
import math

pygame.init()
pygame.font.init()

# Получение информации о первом мониторе
monitor = get_monitors()[0]
width, height = monitor.width, monitor.height

# Создание полноэкранного окна
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("Synaptic Transit")

# Определение цветов КРАТНО ДЕЛЬТЕ ИНАЧЕ ВСЁ СЛОМАЕТСЯ!!!
delta = 10
black = (0 * delta, 0 * delta, 0 * delta)  # Черный цвет
white = (25 * delta, 25 * delta, 25 * delta)  # Белый цвет (немного затемненный)
hover = (19 * delta, 2 * delta, 25 * delta)  # Цвет для кнопки при наведении

# Создание объектов шрифтов
title_font = pygame.font.SysFont("arial", 64, bold=True)  # Шрифт для заголовка
button_font = pygame.font.SysFont("arial", 32)  # Шрифт для кнопок

# Создание объекта для управления FPS
clock = pygame.time.Clock()

class Button:
    def __init__(self, text, center_y):
        # Инициализация кнопки с текстом и вертикальной позицией
        self.current_color = white
        self.text = text
        self.width = 420
        self.height = 80
        # Создание прямоугольника кнопки (для отрисовки и проверки кликов)
        self.rect = pygame.Rect(
            (width - self.width) // 2,  # Центрирование по горизонтали
            center_y - self.height // 2,  # Центрирование по вертикали
            self.width,  # Ширина
            self.height  # Высота
        )

    def draw(self, surface):
        # Отрисовка кнопки на указанной поверхности
        mouse_pos = pygame.mouse.get_pos()

        n = delta
        target_color = hover if self.rect.collidepoint(mouse_pos) else white
        current = getattr(self, 'current_color', white)
        color = tuple(
            current[i] + n if current[i] < target_color[i] else
            current[i] - n if current[i] > target_color[i] else
            current[i]
            for i in range(3)
        )
        self.current_color = color

        pygame.draw.rect(surface, color, self.rect, border_radius=14) # Отрисовка прямоугольника кнопки с закругленными углами

        label = button_font.render(self.text, True, black) # Создание текстовой метки
        label_rect = label.get_rect(center=self.rect.center) # Получение прямоугольника текста и центрирование его в кнопке
        surface.blit(label, label_rect) # Отображение текста на поверхности

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


# Функция для отрисовки логотипа
def draw_logo(surface):
    cx, cy = width // 2, height // 2 - 420 # Определение центра для логотипа (по горизонтали и со смещением вверх)

    # Параметры линий
    line = 8
    white_color = (250, 250, 250)

    # Отрисовка квадрата
    square_size = 135
    square_rect = pygame.Rect(0, 0, square_size, square_size)
    square_rect.center = (cx, cy)  # Центрирование
    pygame.draw.rect(
        surface,
        white_color,
        square_rect,
        line,
        border_radius=10  # Радиус скругления
    )

    # Отрисовка круга
    r = square_size / 2
    pygame.draw.circle(
        surface,
        white_color,
        (cx, cy),  # Центр
        int(r),
        line
    )

    # Отрисовка треугольника
    points = []  # Список для хранения вершин
    for i in range(3):
        angle = math.radians(90 + i * 120)

        x = cx + r * math.cos(angle) * 0.94
        y = cy + r * math.sin(angle) * 0.94
        points.append((x, y))

    # Отрисовка контура
    pygame.draw.polygon(
        surface,
        white_color,
        points,
        line
    )


# Основная функция программы
def main():
    # Создание кнопок
    new_game_btn = Button("Новая игра", height // 2 + 40)
    exit_btn = Button("Выход", height // 2 + 150)

    running = True  # Флаг для основного цикла
    while running:  # Главный игровой цикл
        screen.fill(black)  # Очистка экрана черным цветом

        # Отрисовка всех элементов интерфейса
        draw_logo(screen)

        # Отрисовка заголовка
        title = title_font.render("SYNAPTIC TRANSIT", True, white)
        title_rect = title.get_rect(center=(width // 2, height // 2 - 110))
        screen.blit(title, title_rect)

        # Отрисовка кнопок
        new_game_btn.draw(screen)
        exit_btn.draw(screen)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Обработка нажатий клавиш
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            # Проверка нажатия на кнопку "Новая игра"
            if new_game_btn.clicked(event):
                print("Новая игра. Когда-нибудь тут будет игра.")

            # Проверка нажатия на кнопку "Выход"
            if exit_btn.clicked(event):
                running = False

        # Обновление экрана
        pygame.display.flip()  # Отображение всего
        clock.tick(60)  # Ограничение FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()