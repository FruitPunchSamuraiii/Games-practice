from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface() #Getting display surf from anywhere
        self.offset = pygame.Vector2() #This is for camera

    #Camera
    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2) #If not negative, player and camera move in opposite directions
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        ground_sprites = [sprite for sprite in self if hasattr(sprite, "ground")] #Gathers every sprite with attribute of ground from list into this var
        object_sprites = [sprite for sprite in self if not hasattr(sprite, "ground")]

        for layer in [ground_sprites, object_sprites]:
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery): #Compares center position of sprite of player with objects, so you are infront if below and behind if above
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)