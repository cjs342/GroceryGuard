"""
Lab2: quit_button.py
September 25, 2017
Authors: Cameron Schultz (cjs342) and Dev Sanghvi (dys27)
Description: Pygame program the animates a quit button on the screen and
             a the coordinates of the most recent mouse click. The button 
             is drawn as a text box Surface and mouse (or touchscreen) 
             inputs are detected. When a mouse click occurs within the 
             quit button boundaries, the program exits. The coordinates of
             all other mouse clicks are displayed on the screen.
"""

import os
import pygame
from pygame.locals import *
import numpy as np
import sys

#os.putenv('SDL_VIDEODRIVER','fbcon')
#os.putenv('SDL_FBDEV','/dev/fb1')
#os.putenv('SDL_MOUSEDRV','TSLIB')
#os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')
# Initialize Environment Variables!!!

pygame.init()
#pygame.mouse.set_visible(False)

SIZE = WIDTH, HEIGHT = 320,240            #PiTFT Resolution!!!

BLACK = [0, 0, 0]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
WHITE = [255, 255, 255]

screen = pygame.display.set_mode(SIZE)

TEST_ING = np.asarray(['Cheese 4oz 2d','Chicken 6oz 5d','ing3','ing4','ing5','ing6','ing7','ing8','ing9','ing10','ing11'])
TEST_REC = np.asarray([['rec1 90','rec2 80','rec3 75','rec4 67','rec5 50'],[1,2,3,4,5]])

def home_screen():
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC
   my_font = pygame.font.Font(None,40)
   my_buttons = {'Display Items':(WIDTH/2,50),
               'Suggest Recipes':(WIDTH/2,100),
               'Notifications':(WIDTH/2,150)}

   #count = 3600 #execution loop counter
   #screenshots = 1 #counter to print inputs sequentially
   done = False #set to true when quit button pressed
   pos = (0,0) 
   pow_surf = pygame.image.load("power_button.png")
   pow_surf = pygame.transform.scale(pow_surf,(30,30))
   pow_rect = pow_surf.get_rect(center = (WIDTH-15,HEIGHT-15))

   while not done:

      #mouse/touchscreen input
      for event in pygame.event.get():
         if(event.type is MOUSEBUTTONDOWN):
            pos=pygame.mouse.get_pos()
            #print 'click '+ str(screenshots) + ': ' +str(pos)
            #screenshots += 1
         elif(event.type is MOUSEBUTTONUP):
            pos=pygame.mouse.get_pos()
            x,y=pos
            #power button
            if y>210:
               if x>290:
                  done = True
                  sys.exit()
            #Display Items
            elif 25<y<75:
               #ingredients = get_ingredients()
               ingredients = TEST_ING
               display_fridge(ingredients,0)
            #Suggest Recipes
            elif 75<y<125:
               #recipes = get_recipes()
               recipes = TEST_REC
               display_recipes(recipes)
            #Display Notifications
            elif 125<y<175:
               ingredients = get_ingredients()
               notifications = get_notifications(ingredients)
               display_notifications(notifications)

      screen.fill(BLACK) # Erase the Work space
      for my_text,text_pos in my_buttons.items():
         text_surface = my_font.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)
      
      #msg = "hit at " + str(pos)
      #text_surface = my_font.render(msg, True, white)
      #text_rect = text_surface.get_rect(center=(width/2,height/2))
      #screen.blit(text_surface,text_rect)

      screen.blit(pow_surf,pow_rect)

      pygame.display.flip() # display workspace on screen
      #count -= 1

def display_fridge(ingredients,starti):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC
   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)
   ing_list = {}
   NUM_ING = 9 #number of ingredient to display per screen
   for i in range(min(ingredients.shape[0]-starti,NUM_ING)):
      ing_list[ingredients[starti+i]] = ((WIDTH/2),10+20*i)

   more = True if ingredients.shape[0]-starti > NUM_ING else False
   if more:
      ing_list['More Ingredients'] = ((WIDTH/2),10+20*NUM_ING+5)
   else:
      ing_list['Previous'] = ((WIDTH/2),10+20*NUM_ING+5)

   my_buttons = {'Menu':(50,220),
               'Suggest Recipes':(160,220),
               'Notifications':(270,220)}

   #count = 3600 #execution loop counter
   #screenshots = 1 #counter to print inputs sequentially
   done = False #set to true when quit button pressed
   pos = (0,0) 
   
   while not done:

      #mouse/touchscreen input
      for event in pygame.event.get():
         if(event.type is MOUSEBUTTONDOWN):
            pos=pygame.mouse.get_pos()
            print 'click: ' +str(pos)
            #screenshots += 1
         elif(event.type is MOUSEBUTTONUP):
            pos=pygame.mouse.get_pos()
            x,y=pos
            #more ingredients
            if 185<y<205:
               if more:
                  display_fridge(ingredients,starti+NUM_ING)
               else:
                  display_fridge(ingredients,starti-NUM_ING)
            #Display Items
            if y>210:
               #back to menu   
               if x<75:
                  home_screen()
               #Suggest Recipes
               elif 100<x<225:
                  #recipes = get_recipes()
                  recipes = TEST_REC
                  display_recipes(recipes)
               #Display Notifications
               elif x>230:
                  notifications = get_notifications(ingredients)
                  display_notifications(notifications)

      screen.fill(BLACK) # Erase the Work space
      for my_text,text_pos in my_buttons.items():
            
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in ing_list.items():
         #if my_text != "More Ingredients":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)

      pygame.display.flip()
   #pass
def display_recipes(recipes):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE
   ids = recipes[1]
   recipes = recipes[0]
   
   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)
   rec_list = {}
   #NUM_ING = 9 #number of ingredient to display per screen
   for i in range(5):
      rec_list[recipes[i]] = ((WIDTH/2),20+33*i)

   #more = True if ingredients.shape[0]-starti > NUM_ING else False
   #if more:
   #   ing_list['More Ingredients'] = ((WIDTH/2),10+20*NUM_ING+5)
   #else:
   #   ing_list['Previous'] = ((WIDTH/2),10+20*NUM_ING+5)

   my_buttons = {'Menu':(50,220),
               'Display Items':(160,220),
               'Notifications':(270,220)}

   #count = 3600 #execution loop counter
   #screenshots = 1 #counter to print inputs sequentially
   done = False #set to true when quit button pressed
   pos = (0,0) 
   
   while not done:

      #mouse/touchscreen input
      for event in pygame.event.get():
         if(event.type is MOUSEBUTTONDOWN):
            pos=pygame.mouse.get_pos()
            print 'click: ' +str(pos)
            #screenshots += 1
         elif(event.type is MOUSEBUTTONUP):
            pos=pygame.mouse.get_pos()
            x,y=pos
            #go to recipe screen
            if x>50:
               if 15<y<30:
                  display_single_recipe(ids[0])
                  print ids[0]
               elif 40<y<65:
                  display_single_recipe(ids[1])
                  print ids[1]
               elif 75<y<100:
                  display_single_recipe(ids[2])
                  print ids[2]
               elif 105<y<130:
                  display_single_recipe(ids[3])
                  print ids[3]
               elif 140<y<165:
                  display_single_recipe(ids[4])
                  print ids[4]
            #Display Items
            if y>210:
               #back to menu   
               if x<75:
                  home_screen()
               #Display Items
               elif 115<x<210:
                  #ingredients = get_ingredients()
                  ingredients = TEST_ING
                  display_fridge(ingredients,0)
               #Display Notifications
               elif x>230:
                  #ingredients = get_ingredients()
                  ingredients = TEST_ING
                  notifications = get_notifications(ingredients)
                  display_notifications(notifications)

      screen.fill(BLACK) # Erase the Work space
      for my_text,text_pos in my_buttons.items():
            
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in rec_list.items():
         #if my_text != "More Ingredients":
         text_surface = my_font.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)

      pygame.display.flip()

   pass
def display_notifications(notifications):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE
   pass
def display_single_recipe(recipe):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE
   pass
def display_instruction(instr):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE
   pass
def display_item_added(item):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE
   pass


"""Integrate below methods with Postgres query script"""
def get_ingredients():
   """Queries Postgres 'fridge' table and formats ingredients as a numpy array.
      Format of each entry is np.asarray([ing1,ing2,...])
      where ingi = "Name amt+unit time to expire"
   """
   pass
def get_recipes():
   """Implements recipe suggestion algorithm.
      Formats each recipe as np.asarray([[recipe1,recipe2,...],[id1,id2,...]])
      where recipei = 'name %match'
      %match = #ing in fridge used by recipe/# total ing used by recipe
   """
   pass

"""Compute notifications based on ingredients list?"""
def get_notifications(ingredients):
   pass

if __name__ == "__main__":
      ingredients = TEST_ING
      recipes = TEST_REC
      #display_fridge(ingredients,0)
      display_recipes(recipes)
      #home_screen()