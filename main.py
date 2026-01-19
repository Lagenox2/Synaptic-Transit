import pygame
from screeninfo import get_monitors
import sys
import math

pygame.init()
pygame.font.init()

# Получение информации о первом мониторе
monitor = get_monitors()[0]
WIDTH, HEIGHT = monitor.width, monitor.height

# Создание полноэкранного окна
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Synaptic Transit")

# Определение цветов
BLACK = (0, 0, 0)  # Черный цвет
WHITE = (250, 250, 250)  # Белый цвет (немного затемненный)
HOVER = (200, 200, 200)  # Цвет для кнопки при наведении

# Создание объектов шрифтов
TITLE_FONT = pygame.font.SysFont("arial", 64, bold=True)  # Шрифт для заголовка
BUTTON_FONT = pygame.font.SysFont("arial", 32)  # Шрифт для кнопок

# Создание объекта для управления FPS
clock = pygame.time.Clock()

class Button:
    def __init__(self, text, center_y):
        # Инициализация кнопки с текстом и вертикальной позицией
        self.current_color = WHITE
        self.text = text
        self.width = 420
        self.height = 80
        # Создание прямоугольника кнопки (для отрисовки и проверки кликов)
        self.rect = pygame.Rect(
            (WIDTH - self.width) // 2,  # Центрирование по горизонтали
            center_y - self.height // 2,  # Центрирование по вертикали
            self.width,  # Ширина
            self.height  # Высота
        )

    def draw(self, surface):
        # Отрисовка кнопки на указанной поверхности
        mouse_pos = pygame.mouse.get_pos()

        n = 10
        target_color = HOVER if self.rect.collidepoint(mouse_pos) else WHITE
        current = getattr(self, 'current_color', WHITE)
        color = tuple(
            current[i] + n if current[i] < target_color[i] else
            current[i] - n if current[i] > target_color[i] else
            current[i]
            for i in range(3)
        )
        self.current_color = color

        pygame.draw.rect(surface, color, self.rect, border_radius=14) # Отрисовка прямоугольника кнопки с закругленными углами

        label = BUTTON_FONT.render(self.text, True, BLACK) # Создание текстовой метки
        label_rect = label.get_rect(center=self.rect.center) # Получение прямоугольника текста и центрирование его в кнопке
        surface.blit(label, label_rect) # Отображение текста на поверхности

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


# Функция для отрисовки логотипа
def draw_logo(surface):
    cx, cy = WIDTH // 2, HEIGHT // 2 - 420 # Определение центра для логотипа (по горизонтали и со смещением вверх)

    # Параметры линий
    LINE = 8
    WHITE = (250, 250, 250)

    # Отрисовка квадрата
    square_size = 135
    square_rect = pygame.Rect(0, 0, square_size, square_size)
    square_rect.center = (cx, cy)  # Центрирование
    pygame.draw.rect(
        surface,
        WHITE,
        square_rect,
        LINE,
        border_radius=10  # Радиус скругления
    )

    # Отрисовка круга
    R = square_size / 2
    pygame.draw.circle(
        surface,
        WHITE,
        (cx, cy),  # Центр
        int(R),
        LINE
    )

    # Отрисовка треугольника
    points = []  # Список для хранения вершин
    for i in range(3):
        angle = math.radians(90 + i * 120)

        x = cx + R * math.cos(angle) * 0.94
        y = cy + R * math.sin(angle) * 0.94
        points.append((x, y))

    # Отрисовка контуа
    pygame.draw.polygon(
        surface,
        WHITE,
        points,
        LINE
    )


# Основная функция программы
def main():
    # Создание кнопок
    new_game_btn = Button("Новая игра", HEIGHT // 2 + 40)
    exit_btn = Button("Выход", HEIGHT // 2 + 150)

    running = True  # Флаг для основного цикла
    while running:  # Главный игровой цикл
        screen.fill(BLACK)  # Очистка экрана черным цветом

        # Отрисовка всех элементов интерфейса
        draw_logo(screen)

        # Отрисовка заголовка
        title = TITLE_FONT.render("SYNAPTIC TRANSIT", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110))
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