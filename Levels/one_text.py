import pygame, data

intro = "Здравствуйте. Ваша кандидатура на должность системного администратора одобрена. Перед началом работы вам необходимо пройти инструктаж. Для продолжения нажмите соответствующую кнопку на экране вашего ССВ-2."
tutorial0 = "— это клиент. Клиентом может быть компьютер, телефон или программа пользователя. Его задача — отправить запрос на подключение и получение данных. Если клиент долго не получает ответ, пользователь считает, что система не работает. Ваша задача — обеспечить стабильное и своевременное подключение."
tutorial1 = "— это роутер. Роутер отвечает за передачу данных между устройствами и сетями. У него есть ограничение на количество одновременных соединений. Ваша задача — правильно настроить соединения, чтобы клиент мог связаться с сервером без потерь и задержек."
tutorial2 = "— это сервер. Сервер хранит данные и обрабатывает запросы клиентов. Клиенты не подключаются к серверу напрямую — соединение проходит через роутер. Ваша задача — следить за тем, чтобы сервер был доступен, работал стабильно и корректно отвечал на запросы."



class Tutorial:
    def __init__(self):
        self.rect = pygame.Rect(50, data.height - 300, data.width - 100, 250)
        self.alpha = 220
        self.font_size = 40

    def draw(self, surface, step):
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.alpha))

        mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, self.rect.width, self.rect.height),border_radius=30)
        overlay.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        surface.blit(overlay, self.rect)

        pygame.draw.rect(surface, data.white, self.rect, 2, border_radius=30)

        padding = 80
        text_x = self.rect.x + padding + 80

        if step >= 1 and step <= 3:
            shape_x = self.rect.x + 60
            shape_y = self.rect.y + self.rect.height // 2

            if step == 1:
                pygame.draw.circle(surface, data.white, (shape_x, shape_y), 25, 3)
                pygame.draw.circle(surface, data.white, (shape_x, shape_y), 26, 1)
            elif step == 2:
                h = 25
                points = [
                    (shape_x, shape_y - h),
                    (shape_x - h, shape_y + h),
                    (shape_x + h, shape_y + h)
                ]
                pygame.draw.polygon(surface, data.white, points, 3)
                pygame.draw.polygon(surface, data.white,
                                    [(shape_x, shape_y - h - 0.5),
                                     (shape_x - h - 0.5, shape_y + h + 0.5),
                                     (shape_x + h + 0.5, shape_y + h + 0.5)], 1)
            elif step == 3:
                s = 25
                square_rect = pygame.Rect(shape_x - s, shape_y - s, s * 2, s * 2)
                pygame.draw.rect(surface, data.white, square_rect, 3, border_radius=3)
                pygame.draw.rect(surface, data.white, square_rect.inflate(2, 2), 1, border_radius=4)

        if step == 0:
            text = data.intro
        elif step == 1:
            text = data.tutorial0
        elif step == 2:
            text = data.tutorial1
        elif step == 3:
            text = data.tutorial2
        else:
            text = ""

        font = pygame.font.Font(None, self.font_size)
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] < self.rect.width - padding * 2 - 20:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, data.white)
            text_y = self.rect.y + padding + i * 30
            surface.blit(text_surface, (text_x, text_y))

        if step < 3:
            continue_text = "Нажмите любую кнопку для продолжения..."
            continue_surface = font.render(continue_text, True, (200, 200, 200))
            continue_y = self.rect.y + self.rect.height - 40
            surface.blit(continue_surface, (text_x, continue_y))
        else:
            finish_text = "Нажмите любую кнопку для начала игры..."
            finish_surface = font.render(finish_text, True, (200, 200, 200))
            finish_y = self.rect.y + self.rect.height - 40
            surface.blit(finish_surface, (text_x, finish_y))