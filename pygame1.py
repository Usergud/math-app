import pygame

pygame.init()

# Fenster
breite, höhe = 800, 600
fenster = pygame.display.set_mode((breite, höhe))
clock = pygame.time.Clock()

# Spieler
x = 200
y = 300
geschwindigkeit = 5
# Boden
boden_y = 500
boden=pygame.Rect(0,boden_y,800,100)


#block
block_y=450
block_x=500
block2_y=400
block2_x=550
#gravity
vy=0
gravity=0.5

läuft = True

while läuft:
    clock.tick(60)
    fenster.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            läuft = False

    tasten = pygame.key.get_pressed()

    # links / rechts bewegen

    x -= geschwindigkeit if tasten[pygame.K_a] else 0

    x += geschwindigkeit if tasten[pygame.K_d] else 0

    blöcke = [
        pygame.Rect(block_x, block_y, 50, 50),
        pygame.Rect(block2_x, block2_y, 50, 50)
    ]
    blöcke2=[boden]

    spieler = pygame.Rect(x, y, 50, 50)

    vy += gravity
    y += vy

    spieler.y = y
    on_block=False

    for block in blöcke2:
        if spieler.colliderect(block):
            if vy > 0 and spieler.bottom-vy<=block.top:
                y = block.top - 50
                vy = 0
                on_block=True

    for block in blöcke:
        if spieler.colliderect(block):
            if vy > 0 and spieler.bottom-vy<=block.top:
                y = block.top - 50
                vy = 0
                on_block=True

            elif vy < 0 and spieler.top - vy >= block.bottom:
                y = block.bottom
                vy = 0


            if tasten[pygame.K_a]:
                x= block.right

            if tasten[pygame.K_d]:
                x= block.left-50



    if tasten[pygame.K_w] and on_block:
        vy = -10

    # Spieler zeichnen
    pygame.draw.rect(fenster, (255, 0, 0), (x, y, 50, 50))


    pygame.draw.rect(fenster, (0, 255, 0), (0, boden_y, 800, 100))
    #block
    pygame.draw.rect(fenster, (255, 0, 0), (block_x, block_y, 50, 50))
    #block
    pygame.draw.rect(fenster, (0,0,255),rect=(block2_x,block2_y,50,50))
    pygame.display.update()

pygame.quit()