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
import zbar
import zbar.misc

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

CAM_NAME='/dev/video1'
CAM_RES=(640,480)

screen = pygame.display.set_mode(SIZE)
WINDOW = 62 #display margins

TEST_ING = np.asarray(['Cheese 4oz 2','Chicken 6oz 5','ing3 7tbs 10',
                        'ing4 10tbs 11','ing5 20oz 6','ing6 10oz 1',
                        'ing7 5oz 3','ing8 100tbs 3','ing9 9oz 15',
                        'ing10 7oz 110','ing11 3tbs 1'])
TEST_REC = np.asarray([['rec1 90','rec2 80','rec3 75','rec4 67','rec5 50'],[1,2,3,4,5]])
TEST_NOT = np.asarray(['ing1 low','ing2 low','ing3 exp in 2 days','not4','not5','not6','not7','not8','not9','not10','not11'])


def home_screen():
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   print CAM_NAME
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
               ingredients = get_ingredients()
               #ingredients = TEST_ING
               display_fridge(ingredients,0)
            #Suggest Recipes
            elif 75<y<125:
               recipes = get_recipes()
               #recipes = TEST_REC
               display_recipes(recipes)
            #Display Notifications
            elif 125<y<175:
               ingredients = get_ingredients()
               #ingredients = TEST_ING
               notifications = get_notifications(ingredients)
               #notifications = TEST_NOT
               display_notifications(notifications,0)

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
      
      id = scan()
      if id > 0:
         print str(id) + " scanned"
         item = get_item_name(id)
         display_item_added(item,id)

      #count -= 1

def display_fridge(ingredients,starti):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)
   ing_list = {}
   amt_list={}
   exp_list={}
   text_list={"Item                 Amount      Expiring in":((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)
   NUM_ING = 8 #number of ingredient to display per screen
   for i in range(min(ingredients.shape[0]-starti,NUM_ING)):
      #parse ingredient
      tmp = ingredients[starti+i]
      tmp_list = tmp.split()
      
      #ing_list[entry] = ((WIDTH/2),30+20*i)
      ing_list[tmp_list[0] + " "*(i+1)] = ((WIDTH/2),30+20*i)
      amt_list[tmp_list[1] + " "*(i+1)] = ((WIDTH/2),30+20*i)
      exp_list[tmp_list[2] + " days" + " "*(i+1)] = ((WIDTH/2),30+20*i)

      #if tmp_list[0][:4] == "Ing7":
      #print tmp
      #print tmp_list[0], tmp_list[1], tmp_list[2]
      #ing_list[ingredients[starti+i]] = ((WIDTH/2),30+20*i)

   more = True if ingredients.shape[0]-starti > NUM_ING else False
   if more:
      ing_list['More Ingredients'] = ((WIDTH/2),10+20*(NUM_ING+1)+5)
   else:
      ing_list['Previous'] = ((WIDTH/2),10+20*(NUM_ING+1)+5)

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
                  recipes = get_recipes()
                  #recipes = TEST_REC
                  display_recipes(recipes)
               #Display Notifications
               elif x>230:
                  notifications = get_notifications(ingredients)
                  #notifications = TEST_NOT
                  display_notifications(notifications,0)

      screen.fill(BLACK) # Erase the Work space

      for my_text,text_pos in text_list.items():
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)

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
      for my_text,text_pos in amt_list.items():
         #if my_text != "More Ingredients":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 150
         screen.blit(text_surface,text_rect)
      for my_text,text_pos in exp_list.items():
         #if my_text != "More Ingredients":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 225
         screen.blit(text_surface,text_rect)

      pygame.display.flip()
   #pass
def display_recipes(recipes):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   ids = recipes[1]
   recipes = recipes[0]

   text_list={"Recipe                 Percent Match":((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)
   
   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)
   rec_list = {}
   match_list = {}
   #NUM_ING = 9 #number of ingredient to display per screen
   for i in range(5):
      tmp = recipes[i]
      tmp_list = tmp.split()

      rec_list[tmp_list[0] + " "*(i+1)] = ((WIDTH/2),35+33*i)
      match_list[tmp_list[1] + "%"  + " "*(i+1)] = ((WIDTH/2),35+33*i)

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
               if 30<y<45:
                  display_single_recipe(ids[0])
                  print ids[0]
               elif 55<y<80:
                  display_single_recipe(ids[1])
                  print ids[1]
               elif 90<y<115:
                  display_single_recipe(ids[2])
                  print ids[2]
               elif 120<y<145:
                  display_single_recipe(ids[3])
                  print ids[3]
               elif 155<y<180:
                  display_single_recipe(ids[4])
                  print ids[4]
            #Display Items
            if y>210:
               #back to menu   
               if x<75:
                  home_screen()
               #Display Items
               elif 115<x<210:
                  ingredients = get_ingredients()
                  #ingredients = TEST_ING
                  display_fridge(ingredients,0)
               #Display Notifications
               elif x>230:
                  ingredients = get_ingredients()
                  #ingredients = TEST_ING
                  notifications = get_notifications(ingredients)
                  #notifications = TEST_NOT
                  display_notifications(notifications,0)

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

      for my_text,text_pos in match_list.items():
         #if my_text != "More Ingredients":
         text_surface = my_font.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 200
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in text_list.items():
         #if my_text != "More Ingredients":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)

      pygame.display.flip()

   pass
def display_notifications(notifications, starti):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   #print notifications

   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)

   text_list={"Item                 Message":((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)
   ing_list = {}
   not_list = {}
   NUM_NOT = 8 #number of notifications to display per screen
   for i in range(min(notifications.shape[0]-starti,NUM_NOT)):
      tmp = notifications[starti+i]
      tmp_list = tmp.split(" ",1)
      #print tmp_list[0]
      ing_list[tmp_list[0]+" "*(i+1)] = ((WIDTH/2),30+20*i)
      not_list[tmp_list[1]+" "*(i+1)] = ((WIDTH/2),30+20*i)

   more = True if notifications.shape[0]-starti > NUM_NOT else False
   if more:
      ing_list['More notifications'] = ((WIDTH/2),10+20*(NUM_NOT+1)+5)
   else:
      ing_list['Previous'] = ((WIDTH/2),10+20*(NUM_NOT+1)+5)

   my_buttons = {'Menu':(50,220),
               'Suggest Recipes':(160,220),
               'Display Items':(270,220)}

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
            #more notifications
            if 185<y<205:
               if more:
                  display_notifications(notifications,starti+NUM_NOT)
               else:
                  display_notifications(notifications,starti-NUM_NOT)
            #Display Items
            if y>210:
               #back to menu   
               if x<75:
                  home_screen()
               #Suggest Recipes
               elif 100<x<225:
                  recipes = get_recipes()
                  #recipes = TEST_REC
                  display_recipes(recipes)
               #Display Fridge
               elif x>230:
                  ingredients = get_ingredients()
                  #ingredients = TEST_ING
                  display_fridge(ingredients,0)

      screen.fill(BLACK) # Erase the Work space
      for my_text,text_pos in my_buttons.items():
            
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in not_list.items():
         #if my_text != "More notifications":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 150
         screen.blit(text_surface,text_rect)
      for my_text,text_pos in ing_list.items():
         #if my_text != "More notifications":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)
      for my_text,text_pos in text_list.items():
         #if my_text != "More notifications":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)

      pygame.display.flip()
   
def display_single_recipe(id):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   #print notifications

   #get recipe from SQL
   #img = 
   amounts = ["6oz eggs","3tbs milk","4oz cheese"]
   instructions = ["stir together","mix","whatever"]
   recipe = np.asarray([["Recipe"],instructions,amounts])

   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)

   text_list={recipe[0][0]:((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)
   text_list["Ingredients:"]=((WIDTH/2),30)
   for i in range(len(amounts)):
      text_list[amounts[i]+" "*(i+1)] = ((WIDTH/2),50+20*i)

   my_buttons = {'Show Instructions':(75,220),
               'Back to Recipes':(250,220)}

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
            #Display Items
            if y>210:
               #back to menu   
               if x<140:
                  display_instruction(instructions,0)
               #suggest recipes
               elif x>190:
                  recipes = get_recipes()
                  #recipes = TEST_REC
                  display_recipes(recipes)

      screen.fill(BLACK) # Erase the Work space
      for my_text,text_pos in my_buttons.items():
            
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in text_list.items():
         #if my_text != "More notifications":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)

      pygame.display.flip()
   
def display_instruction(instructions,starti):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW

   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)

   text_list={"Step " + str(starti+1):((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)
   
   #parse step and add to text_list
   instr = instructions[starti]
   blocks = int(np.ceil(float(len(instr))/WINDOW))
   for i in range(blocks):
      text = instr[WINDOW*i:WINDOW*(i+1)]
      text_list[text + " "*(i+1)]=((WIDTH/2),30+20*i)


   more = True if starti+1 < len(instructions) else False
   prev = True if starti != 0 else False
   
   my_buttons = {'Suggest Recipes':(160,220)}

   if more:
      my_buttons["Next Step"] = (270,220)
   if prev:
      my_buttons["Previous Step"] = (50,220)

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
            #more notifications
            #Display Items
            if y>210:
               #previous step  
               if x<75 and prev:
                  display_instruction(instructions,starti-1)
               #Suggest Recipes
               elif 100<x<225:
                  recipes = get_recipes()
                  #recipes = TEST_REC
                  display_recipes(recipes)
               #Display Fridge
               elif x>230 and more:
                  display_instruction(instructions,starti+1)

      screen.fill(BLACK) # Erase the Work space
      for my_text,text_pos in my_buttons.items():
            
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in text_list.items():
         #if my_text != "More notifications":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)

      pygame.display.flip()
   


def display_item_added(item,id):
   global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   
   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)

   text_list={"Item Added!":((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)

   item_list = item.split()
   itm = item_list[1]
   amt = item_list[0]

   text_list2={amt + " of " + itm + " added":((WIDTH/2),100)}

   my_buttons = {'Incorrect?':(75,220),
               'Correct?':(250,220)}

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
            #Display Items
            if y>210:
               #back to menu   
               if x<140:
                  home_screen()
               #suggest recipes
               elif x>190:
                  add_to_fridge(id)
                  home_screen()

      screen.fill(BLACK) # Erase the Work space
      for my_text,text_pos in my_buttons.items():
            
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in text_list.items():
         #if my_text != "More notifications":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)
      for my_text,text_pos in text_list2.items():
         #if my_text != "More notifications":
         text_surface = my_font.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)

      pygame.display.flip()
   pass

def scan():
   pass

def get_item_name(id):
   return "128oz milk"

def add_to_fridge(id):
   pass

"""Integrate below methods with Postgres query script"""
def get_ingredients():
   global TEST_ING, TEST_NOT, TEST_REC
   return TEST_ING
   """Queries Postgres 'fridge' table and formats ingredients as a numpy array.
      Format of each entry is np.asarray([ing1,ing2,...])
      where ingi = "Name amt+unit time to expire in days"
   """
   pass
def get_recipes():
   global TEST_ING, TEST_NOT, TEST_REC
   return TEST_REC
   """Implements recipe suggestion algorithm.
      Formats each recipe as np.asarray([[recipe1,recipe2,...],[id1,id2,...]])
      where recipei = 'name %match'
      %match = #ing in fridge used by recipe/# total ing used by recipe
   """
   pass

"""Compute notifications based on ingredients list?"""
def get_notifications(ingredients):
   EXP_DAYS = 5 #number of days til expiration to trigger notification
   TBS_LOW = 10 #number of tbs to trigger notification
   OZ_LOW = 5 #number of oz to trigger notification
   notifications = np.asarray([])
   for ing in ingredients:
      #parse ingredient into name amount exp days
      ing_list = ing.split()
      name = ing_list[0]
      amount = ing_list[1]
      exp = ing_list[2]

      # check amount
      if amount[-2:] == "oz":
         #ounces
         if int(amount[:-2]) <= OZ_LOW:
            msg = name + " low"
            notifications = np.append(notifications, msg)
      else:
         #tbs
         if int(amount[:-3]) <= TBS_LOW:
            msg = name + " low"
            notifications = np.append(notifications, msg)
   
      # check expiration
      if int(exp) <= EXP_DAYS:
         msg = name + " expiring in " + exp + " days"
         notifications = np.append(notifications, msg)

   return notifications



if __name__ == "__main__":
      #ingredients = TEST_ING

      #recipes = TEST_REC
      #display_item_added(get_item_name(100),100)
      #display_fridge(ingredients,0)
      #display_recipes(recipes)
      home_screen()