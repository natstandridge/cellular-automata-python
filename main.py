import pygame
import hid
import random

class Simulation:
    def __init__(self, WIN_SIZE=(750,750), SCALE_DIVISOR=75, INIT_WEIGHT=3):
        self.WIN_SIZE = WIN_SIZE ## sets window resolution
        self.SCALE_DIVISOR = SCALE_DIVISOR ## sets the number of squares wide and tall the grid is
        self.INIT_WEIGHT = INIT_WEIGHT ## percent of squares that are alive on start
        self.SQUARE_WIDTH = int(self.WIN_SIZE[0]/self.SCALE_DIVISOR)
        self.SQUARE_HEIGHT = int(self.WIN_SIZE[1]/self.SCALE_DIVISOR)

        self.pygame_flags = pygame.SCALED | pygame.RESIZABLE ## flags for display.set_mode
        self.clock = pygame.time.Clock()
        self.grid_display = pygame.display.set_mode((WIN_SIZE[0], WIN_SIZE[1]), self.pygame_flags, vsync=1)

        ## pygame setup
        pygame.init()
        pygame.display.set_caption('Cellular Automata Python')
        pygame.display.get_surface().fill((175, 175, 175))  ## draws a gray background

    def draw_square(self, x, y, color):
        pygame.draw.rect(self.grid_display, color, [x, y, self.SQUARE_WIDTH, self.SQUARE_HEIGHT])

    def draw_grid(self, matrix):

        y = 0 
        for row in matrix:
            x = 0
            for square in row:
                if square == 0:
                    self.draw_square(x, y, (0, 0, 0))             ## draw black square if 0
                elif square == 2:
                    self.draw_square(x, y, (255, 255, 0))         ## draw yellow where pointer currently pointing
                else:
                    self.draw_square(x, y, (255, 255, 255))       ## draw white square if 1

                x += self.SQUARE_WIDTH                            ## move right by SQUARE_WIDTH
            y += self.SQUARE_HEIGHT                               ## move down by SQUARE_HEIGHT

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
        ALIVE_SQUARES = self.INIT_WEIGHT
        DEAD_SQUARES = 100 - self.INIT_WEIGHT
        pointer_loc = [0,0]

        matrix = [[int(random.choices([0,1], weights=[DEAD_SQUARES, ALIVE_SQUARES])[0]) for _ in range(100)] for _ in range(100)] ## int()[0] is needed because .choices() returns nums in single-item list

        ## check for and initialize controller (assumes controller has 'Controller' in product_string)
        for device in hid.enumerate():
            if 'controller' in device['product_string'].lower():
                gamepad = hid.device()
                gamepad.open(device['vendor_id'], device['product_id'])
                gamepad.set_nonblocking(True)
                print(f"Found gamepad named {device['product_string']}.")
        
        
        looping = True
        while looping:

            report = gamepad.read(128)
            last_pointer_loc = pointer_loc
            for row_index, row in enumerate(matrix): ## checking through matrix to add yellow square at pointer_loc

                for item_index, item in enumerate(matrix[row_index]):

                    if row_index == pointer_loc[0] and item_index == pointer_loc[1]:

                        last_pointer_loc_val = matrix[pointer_loc[0]][pointer_loc[1]]
                        matrix[last_pointer_loc[0]][last_pointer_loc[1]] = last_pointer_loc_val
                        print(last_pointer_loc_val)

                        matrix[row_index][item_index] = 2 ## set pointer_loc to 2 to be painted yellow

                        self.draw_grid(matrix)  ## redraw grid with new values
                        pygame.display.update() ## update display


            if report:
                con_state = self.io_check(report)

                if pointer_loc[0] < 0:
                    pointer_loc[0] = 0
                if pointer_loc[1] < 0:
                    pointer_loc[1] = 0

                match con_state:
                    case 'Right':
                        print("Right")
                        pointer_loc[1] += 1
                    case 'Left':
                        print("Left")
                        pointer_loc[1] -= 1
                    case 'Up':
                        print("Up")
                        pointer_loc[0] -= 1
                    case 'Down':
                        print("Down")
                        pointer_loc[0] += 1
                    case 'A':
                        print("A")
                        self.draw_square(pointer_loc[0], pointer_loc[1], (255, 255, 255)) ## add white square at pointer_loc if applicable
                    case 'B':
                        print("B")
                        self.draw_square(pointer_loc[0], pointer_loc[1], (0, 0, 0)) ## add black square at pointer_loc 
       
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    looping = False

            ## matrix = rule_check(matrix) UNCOMMENT WHEN RULE_CHECK IS COMPLETE
            self.draw_grid(matrix)
            pygame.display.update()          ## update display
            self.clock.tick(60)              ## set framerate

if __name__ == '__main__':
    sim = Simulation()
    sim.main()