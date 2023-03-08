import pygame
import random

class Simulation:
    def __init__(self, WIN_SIZE=(750,750), SCALE_DIVISOR=75, INIT_WEIGHT=5):
        self.WIN_SIZE = WIN_SIZE ## sets window resolution
        self.SCALE_DIVISOR = SCALE_DIVISOR ## sets the number of squares wide and tall the grid is
        self.pygame_flags = pygame.SCALED | pygame.RESIZABLE ## flags for display.set_mode
        self.grid_display = pygame.display.set_mode((WIN_SIZE[0], WIN_SIZE[1]), self.pygame_flags, vsync=1)
        self.square_width = int(self.WIN_SIZE[0]/self.SCALE_DIVISOR)
        self.square_height = int(self.WIN_SIZE[1]/self.SCALE_DIVISOR)
        self.INIT_WEIGHT = INIT_WEIGHT ## percent of squares that are alive on start

        ## pygame setup
        pygame.init()
        pygame.display.set_caption('Cellular Automata Python')
        pygame.display.get_surface().fill((175, 175, 175))  ## draws a gray background

    def draw_square(self, x, y, color):
        pygame.draw.rect(self.grid_display, color, [x, y, self.square_width, self.square_height])

    def draw_grid(self, matrix):
        square_width = int(self.WIN_SIZE[0]/self.SCALE_DIVISOR)
        square_height = int(self.WIN_SIZE[1]/self.SCALE_DIVISOR)
        y = 0 
        for row in matrix:
            x = 0
            for square in row:
                if square == 1:
                    self.draw_square(x, y, (0, 0, 0))        ## draw black square if 1
                else:
                    self.draw_square(x, y, (255, 255, 255))  ## draw white square if 0
                x += square_width # move right by square_width
            y += square_height   # move down by square_height

    def rule_check(self, matrix):
        ''' Check entire grid and return updated grid based on the rules. 

            Rules:
                1. Any white square not surrounded by any other white square will turn black
                2. Any white square that has at least one other white square left, right, above, or below it will duplicate
                3. Any square that is able to duplicate will have the extra square added at its diagonals
        '''
        for row_index, row in enumerate(matrix):
            for item_index, item in enumerate(matrix[row_index]):
                ## check the neighbors of the item here
                pass

    def loop(self):
        ALIVE_SQUARES = self.INIT_WEIGHT
        DEAD_SQUARES = 100 - self.INIT_WEIGHT
        
        matrix = [[int(random.choices([0,1], weights=[DEAD_SQUARES, ALIVE_SQUARES])[0]) for _ in range(100)] for _ in range(100)] ## int()[0] is needed because .choices() returns nums in single-item list

        running = True
        clock = pygame.time.Clock()
        while running:
            
            ## any controls should be added right here (pygame has built-in support for getting input from whatever controller is attached/connected to computer)
            ## https://stackoverflow.com/questions/49987072/controller-support-in-pygame

            for event in pygame.event.get(): ## simply checks through events for pygame.QUIT
                if event.type == pygame.QUIT:
                    running = False

            #matrix = [[int(random.choices(num_list, cum_weights=[15,85])[0]) for _ in range(100)] for _ in range(100)] ## updating random matrix for testing
            ## matrix = rule_check(matrix) UNCOMMENT WHEN RULE_CHECK IS COMPLETE
            self.draw_grid(matrix)
            pygame.display.update() ## update display
            clock.tick(60) ## set framerate

if __name__ == '__main__':
    sim = Simulation()
    sim.loop()