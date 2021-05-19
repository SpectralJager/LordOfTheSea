import pygame
import random
import sys
import os
import numpy as np

class MainMenu:
    def __init__(self,size=(720,380)):
        self.size = size
        self.window = pygame.display.set_mode(self.size)

        self.WHITE = pygame.Color(255,255,255)
        self.BLACK = pygame.Color(0,0,0)

        self.font_name = '8BIT WONDER.otf'

        self.is_running = False
        self.is_playing = False

        pygame.display.set_caption('Lord of the sea')

        self.g = Game()

    def menuLoop(self):
        self.is_running = True
        while self.is_running:
            self.pos = (0,0)
            self.chackEvents()
            self.showMenu()
            pygame.display.update()
            pygame.time.Clock().tick(30)
        sys.exit()

    def chackEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    self.pos = pygame.mouse.get_pos()
                    if self.menu_btns[0].collidepoint(self.pos):
                        g = Game()
                        g.gameLoop()
                    if self.menu_btns[1].collidepoint(self.pos):
                        print('settings')
                    if self.menu_btns[2].collidepoint(self.pos):
                        sys.exit()

    def showMenu(self):
        screen_rect = self.window.get_rect()
        self.window.fill(self.BLACK)
        self.textRender('Lord of The Sea',40,(screen_rect.centerx,screen_rect.centery/3))
        self.menu_btns = [
            self.textRender('play',30,(screen_rect.centerx,screen_rect.centery/1.4)),
            self.textRender('settings',30,(screen_rect.centerx,screen_rect.centery)),
            self.textRender('exit',30,(screen_rect.centerx,screen_rect.centery*1.3))
        ]
        
    def textRender(self,text:str,text_size:int,place:tuple):
        font = pygame.font.Font(self.font_name,text_size)
        font_surface = font.render(text,True,self.WHITE)
        font_rect = font_surface.get_rect()
        font_rect.center = place
        self.window.blit(font_surface,font_rect)
        return font_rect

class Game:
    def __init__(self,size=(720,380)):
        self.size = size
        self.window = pygame.display.set_mode(self.size)
        self.screen = self.window.subsurface((0,0,self.size[0],self.size[1]))

        self.WHITE = pygame.Color(255,255,255)
        self.BLACK = pygame.Color(0,0,0)

        self.is_game = False
        self.is_over = False
        self.is_ranning = True

        self.font_name = '8BIT WONDER.otf'

        pygame.display.set_caption('Lord of the sea')

        self.pl = Board()
        self.bot = Board()
        self.bot.board_colors[1] = pygame.Color(255,255,255)
        self.bot.generateBoard()
        
        self.dirrection = True

    def gameLoop(self):
        while self.is_ranning:
            self.checkEvents()
            self.screen.fill(self.BLACK)
            if self.is_over:
                self.over()
            elif self.is_game:
                self.game()
            else:
                self.pregame()
            pygame.display.flip()
            pygame.time.Clock().tick(30)

    def pregame(self):
        self.textRender('dirrection is {}'.format('vertical' if self.dirrection else 'horrizontal'),10,(200,30))
        self.screen.blit(self.pl.drawBoard(),(50,40))
        #self.screen.blit(self.bot.drawBoard(),(self.pl.size*10 + 60,40))
        self.is_game = self.pl.isReady()

    def game(self):
        self.screen.blit(self.pl.drawBoard(),(50,40))
        self.screen.blit(self.bot.drawBoard(),(self.pl.size*10 + 60,40))
        if self.pl.isOver():
            self.is_over = True
            self.over_text = 'You LOOOOOOOOOSER'
        elif self.bot.isOver():
            self.is_over = True
            self.over_text = 'You WIIINNER'

    def over(self):
        self.textRender(self.over_text,40,(360,190))
        self.exit_btn = pygame.draw.rect(self.screen,(255,0,0),[320,300,80,50])
        self.textRender('OK',30,(360,320))
        self.is_game = False


    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.dirrection = not self.dirrection
                if event.key == pygame.K_q:
                    self.is_ranning = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    self.mouse_pos = pygame.mouse.get_pos()
                    if self.is_game:
                        x,y = self.mouse_pos
                        self.bot.isHit((x-(self.pl.size*10 + 60),y - 40))

                        x,y = self.bot.shoot()
                        self.pl.isHit((x*self.pl.size + 15,y*self.pl.size + 15))
                    elif self.is_over:
                        if self.exit_btn.collidepoint(self.mouse_pos):
                            self.is_ranning = False
                    else:
                        #print(self.mouse_pos)
                        self.pl.addShip(self.mouse_pos,self.dirrection)

    def textRender(self,text:str,text_size:int,place:tuple):
        font = pygame.font.Font(self.font_name,text_size)
        font_surface = font.render(text,True,self.WHITE)
        font_rect = font_surface.get_rect()
        font_rect.center = place
        self.screen.blit(font_surface,font_rect)
        return font_rect


class Board:
    def __init__(self,size = 30):
        self.size =size
        self.board_matr = np.zeros((10,10),dtype='int32')
        self.cell_condition = [0,1,2,3]
        self.ships = [1,1,2,2,2,3,3,4]
        self.board_colors = [
            pygame.Color(255,255,255),
            pygame.Color(0,0,255),
            pygame.Color(255,0,0),
            pygame.Color(0,255,0)
        ]
        self.hits = np.zeros((10,10))

    def isValid(self,pos:tuple,d:int,l:int):
        y,x = pos
        l = l - 1
        if (x+l > 9 and d == 0) or (y + l > 9 and d == 1):
            #print('1')
            return False

        try:
            for i in range(l+1):
                if (self.board_matr[y,x+i] == 1 and d == 0):
                    #print('2')
                    return False
                elif (self.board_matr[y+i,x] == 1 and d == 1):
                    #print('3')
                    return False
                elif (((self.board_matr[y+i,x+1] == 1) or (self.board_matr[y+i,x-1] == 1)) and (d == 1)) or (((self.board_matr[y+1,x+i] == 1) or (self.board_matr[y-1,x+i] == 1)) and (d == 0)):
                    #print('4')
                    return False

            if ((self.board_matr[y+l+1,x] == 1 or self.board_matr[y-1,x] == 1) and d == 1) or ((self.board_matr[y,x+l+1] == 1 or self.board_matr[y,x-1] == 1) and d == 0):
                #print('5')
                return False
        except IndexError as e:
            pass#print(e)
        
        return True

    def addShip(self,mouse_pos:tuple,dirrection):
        mouse_pos = mouse_pos[0] - 50, mouse_pos[1] - 40
        for i in range(10):
            for j in range(10):
                if self.cells[i][j].collidepoint(mouse_pos):
                    index = (i,j)
                    if self.ships == []:
                        return False
                    if not self.isValid(index,dirrection,self.ships[-1]):# or self.board_matr[i,j] == 1:
                        return False
                    self.board_matr[i,j] = 1
                    l = self.ships.pop()
                    for k in range(l):
                        if dirrection == 0:
                            self.board_matr[i,j+k] = 1
                        if dirrection == 1:
                            self.board_matr[i+k,j] = 1
        #print(self.board_matr)

    def generateBoard(self):
        while True:
            if self.ships == []:
                return
            pos = (random.randint(0,9),random.randint(0,9))
            dirrection = random.randint(0,1)
            if self.isValid(pos,dirrection,self.ships[-1]):
                #print(self.ships)
                l = self.ships.pop()
                for k in range(l):
                    if dirrection == 0:
                        self.board_matr[pos[0],pos[1]+k] = 1
                    if dirrection == 1:
                        self.board_matr[pos[0]+k,pos[1]] = 1
        #print(self.board_matr)


    def drawBoard(self,pos = (0,0)):
        screen = pygame.Surface((self.size*10,self.size*10))
        x, y = pos
        self.cells = [[]]
        for i in range(10):
            for j in range(10):
                self.cells[i].append(pygame.draw.rect(screen,self.board_colors[self.board_matr[i,j]],(x + j*self.size,y + i*self.size,self.size,self.size)))
            self.cells.append([])
        return screen

    def shoot(self):
        while True:
            pos = (random.randint(0,9),random.randint(0,9))
            #print(pos)
            if self.hits[pos[0],pos[1]] == 0:
                self.hits[pos[0],pos[1]] = 1
                return pos

    def isHit(self,pos:tuple):
        for i in range(10):
            for j in range(10):
                if self.cells[i][j].collidepoint(pos):
                    if self.board_matr[i,j] == 0:
                        self.board_matr[i,j] = 3
                    elif self.board_matr[i,j] == 1:
                        self.board_matr[i,j] = 2

    def isReady(self):
        if self.ships == []:
            #print(self.board_matr.tolist())
            return True
        return False

    def isOver(self):
        count = 0
        for i in range(10):
            for j in range(10):
                if self.board_matr[i][j] == 1:
                    count += 1
                
        if count == 0:
            print('over')
            return True
        return False



if __name__ == '__main__':
    pygame.init()

    g = MainMenu()
    g.menuLoop()


        