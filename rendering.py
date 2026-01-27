import pygame
import data

class Button:
    def __init__(self, text, center_y):
        self.current_color = data.white
        self.text = text
        self.width = 420
        self.height = 80
        self.rect = pygame.Rect((data.width - self.width) // 2, center_y - self.height // 2, self.width, self.height)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        n = data.delta
        target_color = data.hover if self.rect.collidepoint(mouse_pos) else data.white
        current = self.current_color
        color = tuple(
            current[i] + n if current[i] < target_color[i] else current[i] - n if current[i] > target_color[i] else
            current[i] for i in range(3))
        self.current_color = color
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        label = data.button_font.render(self.text, True, data.black)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)