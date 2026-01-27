import pygame
from screeninfo import get_monitors
from Levels.one_text import intro, tutorial0, tutorial1, tutorial2

pygame.init()
pygame.font.init()

# Туториал
tutorial_active = False
tutorial_step = 0  # 0 = intro, 1 = tutorial0, 2 = tutorial1, 3 = tutorial2

safe_zone = 75
client_radius = 50
router_size = 100
server_size = 100

all_objects = []
client_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
client_counter = 0
server_counter = 0

monitor = get_monitors()[0]
width, height = monitor.width, monitor.height

# Включаем антиалиасинг через аппаратное ускорение
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('Synaptic Transit')

delta = 10

# цвета кратно дельте иначе код полетит
black = (0 * delta, 0 * delta, 0 * delta)
white = (25 * delta, 25 * delta, 25 * delta)
hover = (19 * delta, 2 * delta, 25 * delta)
bad = (25 * delta, 8 * delta, 8 * delta)
wave_colors = [
    (20 * delta, 20 * delta, 20 * delta),
    (19 * delta, 19 * delta, 19 * delta),
    (18 * delta, 18 * delta, 18 * delta)
]

title_font = pygame.font.SysFont('arial', 64, bold=True)
button_font = pygame.font.SysFont('arial', 32)
object_font = pygame.font.SysFont('arial', 22, bold=True)
small_font = pygame.font.SysFont('arial', 18)

clock = pygame.time.Clock()
network = None  # Инициализируется позже
objects = []
turn = 1
client_counter = 2