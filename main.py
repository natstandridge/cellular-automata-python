import pygame
import hid
import random

FPS = 5
WIN_SIZE = (1000, 1000) ## sets window resolution
INIT_WEIGHT = 5 ## percent of squares that are alive on start
ALIVE_SQUARES = INIT_WEIGHT
DEAD_SQUARES = 100 - INIT_WEIGHT
SCALE_DIVISOR = 100 ## sets the number of squares in a row/column (has to evenly divide into WIN_SIZE to not show empty space)
SQUARE_WIDTH = int(WIN_SIZE[0]/SCALE_DIVISOR)
SQUARE_HEIGHT = int(WIN_SIZE[1]/SCALE_DIVISOR)

class Simulation:
    ''' The game class that keeps track of the grid, the clock, and checking the grid against the rules. '''
    def __init__(self):
        self.pygame_flags = pygame.SCALED | pygame.RESIZABLE ## flags for display.set_mode
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIN_SIZE[0], WIN_SIZE[1]), self.pygame_flags, vsync=1)
        self.matrix = [[int(random.choices([0,1], weights=[DEAD_SQUARES, ALIVE_SQUARES])[0]) for _ in range(100)] for _ in range(100)]
        pygame.init()
        pygame.display.set_caption('Cellular Automata Python')
        pygame.display.get_surface().fill((175, 175, 175))  ## draws a gray background

    def draw_square(self, x, y, color):
        pygame.draw.rect(self.screen, color, [x, y, SQUARE_WIDTH, SQUARE_HEIGHT])

    def draw_grid(self, matrix, pointer_x=None, pointer_y=None, mode=None, modify=False):
        ''' Draws the grid and takes in pointer_loc to add or remove squares if modify is True and mode is passed (create or remove). '''

        if modify:
            if mode == 'create':
                matrix[pointer_y][pointer_x] = 1
            elif mode == 'remove':
                matrix[pointer_y][pointer_x] = 0
            else:
                pass
            
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
        left, above, right, below = None, None, None, None ## initialize variables for neighbors
        for row_index, row in enumerate(matrix):
            if 1 not in row: ## skip any row that is all 0
                continue
            for item_index, item in enumerate(matrix[row_index]):
                if item != 0: ## only check neighbors if square is alive
                    if item_index != 0:
                        left = matrix[row_index][item_index - 1]
                    if row_index != 0:
                        above = matrix[row_index - 1][item_index]
                    if item_index < len(matrix[0]) - 1:
                        right = matrix[row_index][item_index + 1]
                    if row_index < len(matrix) - 1:
                        below = matrix[row_index + 1][item_index]

                    try:
                        if left and above and right and below:
                            matrix[row_index+1][item_index] = 1
                            matrix[row_index-1][item_index] = 0
                            matrix[row_index][item_index+1] = 0
                            matrix[row_index][item_index-1] = 1

                        elif left and right:
                            matrix[row_index+1][item_index+1] = 1
                            matrix[row_index+1][item_index-1] = 0
                            matrix[row_index-1][item_index+1] = 0
                            matrix[row_index-1][item_index-1] = 0

                        elif above and below:
                            matrix[row_index+1][item_index+1] = 1
                            matrix[row_index-1][item_index-1] = 1

                        elif above or below:
                            matrix[row_index][item_index+1] = 1
                            matrix[row_index-1][item_index] = 1
                        else:
                            ## no neighbors causes square to die
                            matrix[row_index][item_index] = 0

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

        if report[3] == 6:      ## left on D-pad pressed
            return('left')

        if report[3] == 2:      ## right on D-pad pressed
            return('right')

        if report[3] == 0:      ## up on D-pad pressed
            return('up')

        if report[3] == 4:      ## down on D-pad pressed
            return('down')

        if report[2] == 2:      ## start is pressed (for exiting)
            return('start')

    def main(self):

        ## check for and initialize controller (assumes controller has 'Controller' in product_string)
        for device in hid.enumerate():
            if 'controller' in device['product_string'].lower():
                gamepad = hid.device()
                gamepad.open(device['vendor_id'], device['product_id'])
                gamepad.set_nonblocking(True)
                print(f"Found gamepad named {device['product_string']}.")
    
        player = Pointer(0,0) ## player has to start at 0,0 right now
        player.resize() ## resize player based on square scale
        looping = True
        pause = False
        mode = ''

        while looping:

            try:
                report = gamepad.read(128)
                if report:
                    con_state = self.io_check(report)
                    match con_state:
                        case 'right':
                            player.move('right')
                        case 'left':
                            player.move('left')
                        case 'up':
                            player.move('up')
                        case 'down':  
                            player.move('down')
                        case 'A':
                            if mode == 'create':
                                mode = ''
                            else:
                                mode = 'create'
                            print("A")
                        case 'B':
                            if mode == 'remove':
                                mode = ''
                            else:
                                mode = 'remove'
                            print("B")
                        case 'start':
                            if pause:
                                pause = False
                            else:
                                pause = True

            except UnboundLocalError:
                pass

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    looping = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player.move("up")
                    if event.key == pygame.K_DOWN:
                        player.move("down")
                    if event.key == pygame.K_RIGHT:
                        player.move("right")
                    if event.key == pygame.K_LEFT:
                        player.move("left")
                    if event.key == pygame.K_RETURN:
                        if mode == 'create':
                            mode = ''
                        else:
                            mode = 'create'
                    if event.key == pygame.K_DELETE:
                        if mode == 'remove':
                            mode = ''
                        else:
                            mode = 'remove'
                    if event.key == pygame.K_ESCAPE:
                        if pause:
                            pause = False
                        else:
                            pause = True

            if not pause:
                self.matrix = self.rule_check(self.matrix)

            player_x, player_y = player.give_loc()

            if mode == 'create' or 'remove':
                self.draw_grid(self.matrix, player_x, player_y, mode, True)
            else:
                self.draw_grid(self.matrix)

            player.draw(self.screen)
            pygame.display.update() ## update display
            self.clock.tick(FPS)     ## set framerate

class Pointer:
    ''' Represents a yellow square that can be moved around the grid to place and remove squares. '''
    def __init__(self, x, y, grid_loc_x=0, grid_loc_y=0):
        self.image = pygame.image.load('pointer.png')
        self.x = x # visual x location
        self.y = y # visual y location
        self.grid_loc_x = grid_loc_x # x location on grid
        self.grid_loc_y = grid_loc_y # y location on grid

    def resize(self):
        width = self.image.get_rect().width
        height = self.image.get_rect().height
        self.image = pygame.transform.scale(self.image, (width*SQUARE_WIDTH, height*SQUARE_HEIGHT)) ## transforms image to fit with grid (source image must be 1 pixel)

    def give_loc(self):
        return(self.grid_loc_x, self.grid_loc_y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, direction):
        if direction == 'right':
            self.x += SQUARE_WIDTH
            self.grid_loc_x += 1
        if direction == 'left':
            self.x -= SQUARE_WIDTH
            self.grid_loc_x -= 1
        if direction == 'up':
            self.y -= SQUARE_HEIGHT
            self.grid_loc_y -= 1
        if direction == 'down':
            self.y += SQUARE_HEIGHT
            self.grid_loc_y += 1

if __name__ == '__main__':
    sim = Simulation()
    sim.main()