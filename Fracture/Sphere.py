
class Sphere:
    sphere_list = []
    def __init__(self, game):
        self.image = game.sphere
        self.speed = 1
        self.width, self.height = self.get_sphere_size()
        self.x = 100
        self.y = game.screen_height - 100
        self.right = True
        self.left = False
        self.up = True
        self.down = False
        Sphere.sphere_list.append(self)

    def get_sphere_size(self):
        image_size = self.image.get_size()
        width = image_size[0]
        height = image_size[1]
        return width, height


def draw(game, screen):
    for sphere in Sphere.sphere_list:
        screen.blit(sphere.image, (sphere.x,sphere.y))
    return

def edge_bounce(game, sphere):
    # Right Border
    if (sphere.x + sphere.speed + sphere.width >= game.screen_width):
        sphere.right = False
        sphere.left = True
    # Left Border
    if (sphere.x - sphere.speed <= 0):
        sphere.right = True
        sphere.left = False
    # Top Border
    if (sphere.y - sphere.speed <= 0):
        sphere.up = False
        sphere.down = True
    # Bottom Border
    if (sphere.y + sphere.speed + sphere.height >= game.screen_height):
        sphere.up = True
        sphere.down = False
    return



def update(game):
    for sphere in Sphere.sphere_list:
        if (sphere.right):
            sphere.x += sphere.speed
        else:
            sphere.x -= sphere.speed
        if (sphere.down):
            sphere.y += sphere.speed
        else:
            sphere.y -= sphere.speed
        edge_bounce(game, sphere)
    return