import pygame


pygame.init()
WIDTH = 800
HEIGHT = 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Pygame Window")

def draw_window():
    pygame.display.update()

def main():
    clock = pygame.time.Clock()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.K_ESCAPE:
                run = False


        WIN.fill((0, 0, 125))

        draw_window()

        clock.tick(60)


main()

pygame.quit()
