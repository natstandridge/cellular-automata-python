import pygame
import hid
import random

WIN_SIZE = (750, 750) ## sets window resolution
INIT_WEIGHT = 3 ## percent of squares that are alive on start
SCALE_DIVISOR = 75 ## sets the number of squares wide and tall the grid is
SQUARE_WIDTH = int(WIN_SIZE[0]/SCALE_DIVISOR)
SQUARE_HEIGHT = int(WIN_SIZE[1]/SCALE_DIVISOR)

class Simulation:
    ''' The game class that keeps track of the grid, the clock, and checking the grid against the rules. '''
    def __init__(self):
        self.pygame_flags = pygame.SCALED | pygame.RESIZABLE ## flags for display.set_mode
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIN_SIZE[0], WIN_SIZE[1]), self.pygame_flags, vsync=1)
        pygame.init()
        pygame.display.set_caption('Cellular Automata Python')
        pygame.display.get_surface().fill((175, 175, 175))  ## draws a gray background

    def draw_square(self, x, y, color):
        pygame.draw.rect(self.screen, color, [x, y, SQUARE_WIDTH, SQUARE_HEIGHT])

    def draw_grid(self, matrix):
        y = 0
        for row in matrix:
            x = 0
            for square in row:
                if square == 0:
                    self.draw_square(x, y, (0, 0, 0))             ## draw black square if 0
                else:
                    self.draw_square(x, y, (255, 255, 255))       ## draw white square if 1

                x += SQUARE_WIDTH                            ## move right by SQUARE_WIDTH
            y += SQUARE_HEIGHT                               ## move down by SQUARE_HEIGHT

    def rule_check(self, matrix):
        ''' Check entire grid and return updated grid based on the rules. 

            Rules:
                1. Any white square not surrounded by any other white square will turn black
                2. Any white square that has at least one other white square left, right, above, or below it will duplicate
                3. Any square that is able to duplicate will have the extra square added at its diagonals
        '''
        for row_index, row in enumerate(matrix):
            if 1 not in row: ## skip any row that is all 0
                continue
            for item_index, item in enumerate(matrix[row_index]):
                if item != 0: ## only check neighbors if square is alive
                    try:
                        ## check the neighbors of the item here
                        if item_index != 0: ## keep the item_index from going negative and picking the wrong index
                            above = matrix[item_index - 1][item_index]
                            left = matrix[item_index][item_index - 1]
                        right = matrix[item_index][item_index + 1]
                        below = matrix[item_index + 1][item_index]

                        ## do the changes to the matrix here based on above, left, right, and below

                    except IndexError:
                        pass

        return(matrix)

    def io_check(self, report: list) -> str:
        ''' Checks bitfield from controller signal and returns a string representing the button or direction pressed. 
            Mapped based on values of the buttons on the Nintendo Switch SNES Controller. '''
        
        if report[1] == 2:      ## A button
            return('A')

        if report[1] == 1:      ## B button
            return('B')

        if report[3] == 6:      ## Left on D-pad pressed
            return('Left')

        if report[3] == 2:      ## Right on D-pad pressed
            return('Right')

        if report[3] == 0:      ## Up on D-pad pressed
            return('Up')

        if report[3] == 4:      ## Down on D-pad pressed
            return('Down')

        if report[2] == 2:      ## Start is pressed (for exiting)
            return('Start')

    def main(self):
        ALIVE_SQUARES = INIT_WEIGHT
        DEAD_SQUARES = 100 - INIT_WEIGHT

        matrix = [[int(random.choices([0,1], weights=[DEAD_SQUARES, ALIVE_SQUARES])[0]) for _ in range(100)] for _ in range(100)] ## int()[0] is needed because .choices() returns nums in single-item list

        ## check for and initialize controller (assumes controller has 'Controller' in product_string)
        for device in hid.enumerate():
            if 'controller' in device['product_string'].lower():
                gamepad = hid.device()
                gamepad.open(device['vendor_id'], device['product_id'])
                gamepad.set_nonblocking(True)
                print(f"Found gamepad named {device['product_string']}.")
        
        player = Pointer(0, 0)
        player.resize()
        looping = True
        while looping:

            report = gamepad.read(128)

            if report:
                con_state = self.io_check(report)

                match con_state:
                    case 'Right':
                        print("Right")
                        player.move('Right')
                    case 'Left':
                        print("Left")
                        player.move('Left')
                    case 'Up':
                        print("Up")
                        player.move('Up')
                    case 'Down':
                        print("Down")
                        player.move('Down')
                    case 'A':
                        print("A")
                         ## add white square/1 on matrix if applicable
                    case 'B':
                        print("B")
                        ## add black square/0 at pointer_loc 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    looping = False

            ## matrix = rule_check(matrix) UNCOMMENT WHEN RULE_CHECK IS COMPLETE
            self.draw_grid(matrix)
            player.draw(self.screen)
            pygame.display.update()          ## update display
            self.clock.tick(60)              ## set framerate

class Pointer(Simulation):
    ''' Represents a yellow square that can be moved around the grid to place and remove squares. '''
    def __init__(self, x, y):
        self.image = pygame.image.load('pointer.png')
        self.x = x
        self.y = y

    def resize(self):
        width = self.image.get_rect().width
        height = self.image.get_rect().height
        self.image = pygame.transform.scale(self.image, (width*SQUARE_WIDTH, height*SQUARE_HEIGHT)) ## transforms image to fit with grid

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, direction):
        if direction == 'Right':
            self.x += SQUARE_WIDTH
        if direction == 'Left':
            self.x -= SQUARE_WIDTH
        if direction == 'Up':
            self.y -= SQUARE_HEIGHT
        if direction == 'Down':
            self.y += SQUARE_HEIGHT

if __name__ == '__main__':
    sim = Simulation()
    sim.main()