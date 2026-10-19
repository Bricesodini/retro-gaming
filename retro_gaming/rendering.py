"""Small Pygame drawing primitives shared by the games."""

import pygame


def draw_centered_label(surface: pygame.Surface, font: pygame.font.Font,
                        value: str, center: tuple[int, int],
                        color: tuple[int, int, int]) -> None:
    image = font.render(value, True, color)
    surface.blit(image, image.get_rect(center=center))
