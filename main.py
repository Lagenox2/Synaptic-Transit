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
# Установка заголовка окна
pygame.display.set_caption("Synaptic Transit")

# Определение цветов
BLACK = (0, 0, 0)  # Черный цвет
WHITE = (250, 250, 250)  # Белый цвет (немного затемненный)
HOVER = (200, 200, 200)  # Цвет для кнопки при наведении

# Создание объектов шрифтов
TITLE_FONT = pygame.font.SysFont("arial", 64, bold=True)  # Шрифт для заголовка
BUTTON_FONT = pygame.font.SysFont("arial", 32)  # Шрифт для кнопок

# Создание объекта для управления FPS (частота кадров)
clock = pygame.time.Clock()


# Класс для создания кнопок
class Button:
    def __init__(self, text, center_y):
        # Инициализация кнопки с текстом и вертикальной позицией
        self.current_color = WHITE
        self.text = text  # Текст кнопки
        self.width = 420  # Ширина кнопки
        self.height = 80  # Высота кнопки
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

        # Отрисовка прямоугольника кнопки с закругленными углами
        pygame.draw.rect(surface, color, self.rect, border_radius=14)

        # Создание текстовой метки
        label = BUTTON_FONT.render(self.text, True, BLACK)
        # Получение прямоугольника текста и центрирование его в кнопке
        label_rect = label.get_rect(center=self.rect.center)
        # Отображение текста на поверхности
        surface.blit(label, label_rect)

    def clicked(self, event):
        # Проверка, была ли кнопка нажата
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверка, находится ли точка клика внутри прямоугольника кнопки
            return self.rect.collidepoint(event.pos)
        return False


# Функция для отрисовки логотипа
def draw_logo(surface):
    # Определение центра для логотипа (по горизонтали и со смещением вверх)
    cx, cy = WIDTH // 2, HEIGHT // 2 - 420

    # Параметры линий
    LINE = 6  # Толщина линий
    WHITE = (240, 240, 240)  # Цвет линий (локальная переменная, переопределяет глобальную)

    # Отрисовка квадрата
    square_size = 135  # Размер квадрата
    square_rect = pygame.Rect(0, 0, square_size, square_size)  # Создание прямоугольника
    square_rect.center = (cx, cy)  # Центрирование квадрата
    # Отрисовка квадрата с закругленными углами
    pygame.draw.rect(
        surface,
        WHITE,
        square_rect,
        LINE,  # Толщина линии (только контур)
        border_radius=10  # Радиус скругления углов
    )

    # Отрисовка круга
    R = square_size / 2  # Радиус круга (половина размера квадрата)
    pygame.draw.circle(
        surface,
        WHITE,
        (cx, cy),  # Центр круга
        int(R),  # Радиус круга
        LINE  # Толщина линии (только контур)
    )

    # Отрисовка треугольника
    points = []  # Список для хранения вершин треугольника
    for i in range(3):
        # Расчет углов для равностороннего треугольника (120 градусов между вершинами)
        angle = math.radians(90 + i * 120)  # Преобразование градусов в радианы
        # Расчет координат вершины
        x = cx + R * math.cos(angle) * 0.95
        y = cy + R * math.sin(angle) * 0.95
        points.append((x, y))  # Добавление вершины в список

    # Отрисовка треугольника (контур)
    pygame.draw.polygon(
        surface,
        WHITE,
        points,  # Список вершин
        LINE  # Толщина линии
    )


# Основная функция программы
def main():
    # Создание кнопок
    new_game_btn = Button("Новая игра", HEIGHT // 2 + 40)  # Кнопка "Новая игра"
    exit_btn = Button("Выход", HEIGHT // 2 + 150)  # Кнопка "Выход"

    running = True  # Флаг для основного цикла
    while running:  # Главный игровой цикл
        screen.fill(BLACK)  # Очистка экрана черным цветом

        # Отрисовка всех элементов интерфейса
        draw_logo(screen)  # Отрисовка логотипа

        # Отрисовка заголовка
        title = TITLE_FONT.render("SYNAPTIC TRANSIT", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110))
        screen.blit(title, title_rect)

        # Отрисовка кнопок
        new_game_btn.draw(screen)
        exit_btn.draw(screen)

        # Обработка событий
        for event in pygame.event.get():  # Получение всех событий из очереди
            # Обработка закрытия окна (крестик в углу)
            if event.type == pygame.QUIT:
                running = False

            # Обработка нажатий клавиш
            if event.type == pygame.KEYDOWN:
                # Закрытие программы при нажатии ESC
                if event.key == pygame.K_ESCAPE:
                    running = False

            # Проверка нажатия на кнопку "Новая игра"
            if new_game_btn.clicked(event):
                print("Новая игра. Когда-нибудь тут будет игра.")

            # Проверка нажатия на кнопку "Выход"
            if exit_btn.clicked(event):
                running = False

        # Обновление экрана
        pygame.display.flip()  # Отображение всего, что было нарисовано
        clock.tick(60)  # Ограничение до 60 кадров в секунду

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()