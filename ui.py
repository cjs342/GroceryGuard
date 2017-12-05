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
import pygame.camera
import pygame.image
import pygame.surfarray
from PIL import Image
import numpy as np
import sys
import zbar
import zbar.misc
import time
import numpy as np
import psycopg2
import datetime
from num2words import num2words
import subprocess
from subprocess import call
import RPi.GPIO as GPIO


os.putenv('SDL_VIDEODRIVER','fbcon')
os.putenv('SDL_FBDEV','/dev/fb1')
os.putenv('SDL_MOUSEDRV','TSLIB')
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')
# Initialize Environment Variables!!!

pygame.init()
pygame.mouse.set_visible(False)

SIZE = WIDTH, HEIGHT = 320,240            #PiTFT Resolution!!!

BLACK = [0, 0, 0]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
WHITE = [255, 255, 255]

CAM_NAME='/dev/video0'
CAM_RES=(640,480)

screen = pygame.display.set_mode(SIZE)
WINDOW = 62 #display margins

TEST_ING = np.asarray(['Cheese 4oz 2','Chicken 6oz 5','ing3 7tbs 10',
                        'ing4 10tbs 11','ing5 20oz 6','ing6 10oz 1',
                        'ing7 5oz 3','ing8 100tbs 3','ing9 9oz 15',
                        'ing10 7oz 110','ing11 3tbs 1'])
TEST_REC = np.asarray([['rec1 90','rec2 80','rec3 75','rec4 67','rec5 50'],[1,2,3,4,5]])
TEST_NOT = np.asarray(['ing1 low','ing2 low','ing3 exp in 2 days','not4','not5','not6','not7','not8','not9','not10','not11'])
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def GPIO27_callback(channel):
   cmd = 'kill -9 $(pgrep python)'
   call(cmd, shell=True)

GPIO.add_event_detect(27,GPIO.FALLING,callback=GPIO27_callback,bouncetime=300)



def home_screen():
   #global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   #print CAM_NAME
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

   start_time = time.time()
   delay = 100 #scanning interval
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
      
      if delay == 0:
         id = scan()
         if id > 0:
            print str(id) + " scanned"
            item = get_item_name(id)
            print item, type(item)
            display_item_added(item,id)
         delay = 100
         #print "elapsed time: ",time.time()-start_time
         start_time=time.time()
      
      delay -= 1

      #count -= 1

def display_fridge(ingredients,starti):
   #global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
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
      print tmp_list
      
      #ing_list[entry] = ((WIDTH/2),30+20*i)
      ing_list[" ".join(tmp_list[:-4]) + " "*(i+1)] = ((WIDTH/2),30+20*i)
      amt_list[tmp_list[-4] + " "*(i+1)] = ((WIDTH/2),30+20*i)
      exp_list[tmp_list[-3] + " days" + " "*(i+1)] = ((WIDTH/2),30+20*i)

      #if tmp_list[0][:4] == "Ing7":
      #print tmp
      #print tmp_list[0], tmp_list[1], tmp_list[2]
      #ing_list[ingredients[starti+i]] = ((WIDTH/2),30+20*i)

   more = True if ingredients.shape[0]-starti > NUM_ING else False
   prev = True if starti > NUM_ING-1 else False
   if more:
      ing_list['More Ingredients'] = ((WIDTH/2),10+20*(NUM_ING+1)+5)
   elif prev:
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
               elif prev:
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
         text_rect.left = 170
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
   #global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   ids = recipes[1]
   recipes = recipes[0]


   text_list={"Recipe                          Percent Match":((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)
   
   my_font = pygame.font.Font(None,25)
   my_font2 = pygame.font.Font(None,20)
   rec_list = {}
   match_list = {}
   #NUM_ING = 9 #number of ingredient to display per screen
   for i in range(5):
      tmp = recipes[i]
      tmp_list = tmp.split()
      match = float(tmp_list[-1])*100
      if match >= 100:
         match_str = str(match)[:3]
      else:
         match_str = str(match)[:2]
      var = ' '.join(tmp_list[:-1])
      if len(var) > 18:
         var = var[:16] + '...'
      rec_list[var + " "*(i+1)] = ((WIDTH/2),35+33*i)
      match_list[match_str + "%"  + " "*(i+1)] = ((WIDTH/2),35+33*i)

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
         text_rect.left = 230
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in text_list.items():
         #if my_text != "More Ingredients":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 50
         screen.blit(text_surface,text_rect)

      pygame.display.flip()

def display_notifications(notifications, starti):
   #global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
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
      tmp_list = tmp.split(";")
      print tmp_list
      #print tmp_list[0]
      ing_list[tmp_list[0]+" "*(i+1)] = ((WIDTH/2),30+20*i)
      not_list[tmp_list[1]+" "*(i+1)] = ((WIDTH/2),30+20*i)

   more = True if notifications.shape[0]-starti > NUM_NOT else False
   prev = True if starti > NUM_NOT-1 else False
   if more:
      ing_list['More notifications'] = ((WIDTH/2),10+20*(NUM_NOT+1)+5)
   elif prev:
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
               elif prev:
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
   #global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   #print notifications

   #get recipe from SQL
   #img = 

   conn = psycopg2.connect('dbname=grocery_guard')
   cur = conn.cursor()
   cur.execute("select name,ingredients,amounts,instructions,image from recipes where id = %s" %str(id))
   data = cur.fetchone()

   name = data[0]
   ingredients = data[1]
   quantities = data[2]
   instructions = data[3].split("\n")
   amounts=['']*len(ingredients)
   for i in range(len(ingredients)):
      print str(int(ingredients[i]))
      cur.execute("select name from codes where id = %s" % str(int(ingredients[i])))
      amounts[i] = str(quantities[i]) + ' ' + cur.fetchone()[0]
   #amounts = ["6oz eggs","3tbs milk","4oz cheese"]
   #instructions = ["stir together","mix","whatever"]
   recipe = np.asarray([[name.title()],instructions,amounts])

   my_font = pygame.font.Font(None,26)
   my_font2 = pygame.font.Font(None,20)

   text_list={recipe[0][0]:((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)
   text_list["Ingredients:"]=((WIDTH/2),30)
   text_list2={}
   for i in range(len(amounts)):
      if i < 6:
         text_list[amounts[i]+" "*(i+1)] = ((WIDTH/2),50+20*i)
      else:
         text_list2[amounts[i]+" "*(i+1)] = ((WIDTH/2),50+20*(i-6))

   my_buttons = {'Show Instructions':(75,220),
               'Back to Recipes':(250,220)}

   #count = 3600 #execution loop counter
   #screenshots = 1 #counter to print inputs sequentially
   done = False #set to true when quit button pressed
   pos = (0,0) 
   cur.close()
   conn.close()
   cooked = False
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
            #cook recipe
            if y > 170 and 130<x<190 and not cooked:
               cook_recipe(id) 
               cooked = True
               for i in range(len(ingredients)):
                  print ingredients[i], quantities[i]
                  update_fridge(ingredients[i],quantities[i])
            #Display Items
            if y>210:
               #back to menu   
               if x<140:
                  display_instruction(instructions,0,id,False)
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
      #for i in range(len(text_list.items())):
         #if my_text != "More notifications":
         #my_text = text_list.items()[i][0]
         #text_pos = text_list.items()[i][1]
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         #if i < 6:
         text_rect.left = 50
         #else:
         #   text_rect.left = 175
         screen.blit(text_surface,text_rect)
      for my_text,text_pos in text_list2.items():
      #for i in range(len(text_list.items())):
         #if my_text != "More notifications":
         #my_text = text_list.items()[i][0]
         #text_pos = text_list.items()[i][1]
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         #if i < 6:
         text_rect.left = 175
         #else:
         #   text_rect.left = 175
         screen.blit(text_surface,text_rect)

      #pygame.draw.rect(screen, RED, [WIDTH/2-20,HEIGHT-40-25,40,50])
      
      if not cooked:
         text = "COOK!"
         button_color = RED
      else:
         text = "COOKED!"
         button_color = GREEN

      pygame.draw.circle(screen, button_color, [WIDTH/2,HEIGHT-40],30)
      text_surface = my_font2.render(text, True, WHITE)
      text_rect = text_surface.get_rect(center=(WIDTH/2,HEIGHT-40))
      screen.blit(text_surface,text_rect)
      pygame.display.flip()
   
def display_instruction(instructions,starti,id,s):
   #global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   cmd_beg = 'espeak -s150 ' 
   cmd_end = ' | aplay /home/pi/GroceryGuard/Text.wav 2>/dev/null &'
   cmd_out = '--stdout > /home/pi/GroceryGuard/Text.wav '
   #instructions1=list(instructions)
   instructions1 = instructions[starti].replace(' ','_')
   print instructions1
   #print instructions
   #print len(instructions)
   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)

   text_list={"Step " + str(starti+1):((WIDTH/2),10)}
   text_list["-"*(WINDOW+5)]=((WIDTH/2),20)
   #call([cmd_beg+cmd_out+str(instructions1)+cmd_end], shell=True)
   #parse step and add to text_list
   instr = instructions[starti]
   wndw = WINDOW-25
   blocks = int(np.ceil(float(len(instr))/(wndw)))
   for i in range(blocks):
      text = instr[wndw*i:wndw*(i+1)].strip()
      text_list[text + " "*(i+1)]=((WIDTH/2),30+20*i)

   more = True if starti+1 < len(instructions)-1 else False
   prev = True if starti != 0 else False
   
   my_buttons = {'Back to Recipe':(160,220),'Toggle Speech':((WIDTH-50),10)}

   if more:
      my_buttons["Next Step"] = (270,220)
   if prev:
      my_buttons["Previous Step"] = (50,220)

   #count = 3600 #execution loop counter
   #screenshots = 1 #counter to print inputs sequentially
   done = False #set to true when quit button pressed
   pos = (0,0) 
   first=True
   speak = s
   print speak
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
               if x<100 and prev:
                  call("kill -9 $(pgrep aplay)",shell=True)
                  display_instruction(instructions,starti-1,id,speak)
               #Suggest Recipes
               elif 100<x<225:
                  #recipes = get_recipes()
                  #recipes = TEST_REC
                  #display_recipes(recipes)

                  call("kill -9 $(pgrep aplay)",shell=True)
                  display_single_recipe(id)
               #Display Fridge
               elif x>230 and more:
                  call("kill -9 $(pgrep aplay)",shell=True)
                  display_instruction(instructions,starti+1,id,speak)
            #toggle speech
            if y<20 and x>220:
               if speak == False:
                  speak = True
                  first = True
               else:
                  call("kill -9 $(pgrep aplay)",shell=True)
                  speak = False
                  first = False

      screen.fill(BLACK) # Erase the Work space
      for my_text,text_pos in my_buttons.items():
            
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         screen.blit(text_surface,text_rect)

      for my_text,text_pos in text_list.items():
         #if my_text != "More notifications":
         text_surface = my_font2.render(my_text, True, WHITE)
         text_rect = text_surface.get_rect(center=text_pos)
         text_rect.left = 25
         screen.blit(text_surface,text_rect)

      pygame.display.flip()
      if first and speak:
         print "speaking"
         call([cmd_beg+cmd_out+'"'+str(instructions1)+'"'+cmd_end], shell=True)
         first=False
   


def display_item_added(item,id):
   #global screen,SIZE,WIDTH,HEIGHT,BLACK,RED,GREEN,BLUE,WHITE,TEST_ING,TEST_REC, TEST_NOT,WINDOW
   
   my_font = pygame.font.Font(None,30)
   my_font2 = pygame.font.Font(None,20)

   text_list={"Item Added!":((WIDTH/2),10)}
   text_list["-"*WINDOW]=((WIDTH/2),20)

   #item_list = item.split()
   #itm = item_list[1]
   #amt = item_list[0]
   #print item_list
   print item
   text_list2={item.title() + " added":((WIDTH/2),100)}

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
   """return UPC number if barcode detected. Return -1 if no barcode detected."""
   pygame.init()
   pygame.camera.init()
   pygame.camera.list_cameras()
   cam = pygame.camera.Camera(CAM_NAME, CAM_RES,'RGB')
   #print cam
   #screen = pygame.display.set_mode(cam.get_size())
   cam.start()
   time.sleep(0.5)  # You might need something higher in the beginning
   pygame_screen_image = cam.get_image()
   #screen.blit(pygame_screen_image, (0,0))
   #pygame.display.flip() # update the display
   cam.stop()

   #pygame.display.quit()

   img_arr = pygame.surfarray.array3d(pygame_screen_image)
   #print img_arr.dtype
   #convert to grayscale and cast to uint8
   img_arr = np.dot(img_arr[...,:3], [0.299, 0.587, 0.114])
   img_arr=img_arr.astype(np.uint8)
   #print img_arr.dtype
   #now that we have the image, scan for a barcode
   scanner = zbar.Scanner()
   results = scanner.scan(img_arr)
   if results==[]:
      print "no barcode found"
      return -1
   else:
      for result in results:
         # By default zbar returns barcode data as byte array, so decode byte array$
         print(result.type, result.data.decode("ascii"), result.quality)
         return int(result.data.decode("ascii"))
   

def get_item_name(id):
   #return "128 oz of milk"
   id = str(int(id))
   conn = psycopg2.connect('dbname=grocery_guard')
   cur = conn.cursor()
   cur.execute("select name,quantity from codes where id = %s" % id)
   data = np.asarray(cur.fetchone())
   print data
   name = data[0]
   #quantity = data[1]

   cur.close()
   conn.close()
   return name.title()

def add_to_fridge(id):
   # get name, quantity, exp_days from codes
   id = str(int(id))
   conn = psycopg2.connect('dbname=grocery_guard')
   cur = conn.cursor()
   cur.execute("select name,quantity,exp_days from codes where id = %s" % id)
   data = np.asarray(cur.fetchone())
   name = data[0]
   quantity = int(float(data[1]))
   exp_days = int(float(data[2]))

   added = "date '" + str(datetime.date.today()) + "'"
   
   #check if already in fridge
   cur.execute("select exists(select 1 from fridge where id = %s)" % id)
   exists = cur.fetchone()[0]
   if exists:
      cur.execute("select quantity from fridge where id = %s" % id)
      amt = int(cur.fetchone()[0]+quantity)
      msg = "update fridge set quantity = %s where id = %s" %(amt,id)
   else:
      # write to fridge id, name, quantity, added, exp_days
      msg = "insert into fridge values (%s, '%s', %s, %s, %s)" % (id,name,quantity,added,exp_days)
   cur.execute(msg)
   conn.commit()

   cur.close()
   conn.close()

def update_fridge(id,amt):
   id = str(int(id))
   #amt = amount to subtract
   conn = psycopg2.connect('dbname=grocery_guard')
   cur = conn.cursor()
   
   #check if ingredient in fridge
   cur.execute("select exists(select 1 from fridge where id = %s)" % id)
   exists = cur.fetchone()[0]
   if exists:
      # get amount currently in fridge
      cur.execute("select quantity from fridge where id = %s" % id)
      quantity = int(np.asarray(cur.fetchone())[0])
      
      new_amt = int(quantity-amt)

      #remove from fridge
      if new_amt <= 0:
         cur.execute("delete from fridge where id = %s" % id)
      #update fridge with new value
      else:
         cur.execute("update fridge set quantity = %s where id = %s" % (str(new_amt),id))

      conn.commit()
   cur.close()
   conn.close()

"""Integrate below methods with Postgres query script"""
def get_ingredients():
   #return TEST_ING
   #global TEST_ING, TEST_NOT, TEST_REC
   """Queries Postgres 'fridge' table and formats ingredients as a numpy array.
      Format of each entry is np.asarray([ing1,ing2,...])
      where ingi = "Name amt+unit time to expire in days"
   """
   #get name + amt + exp length + date added
   conn = psycopg2.connect('dbname=grocery_guard')
   cur = conn.cursor()
   cur.execute("select name,quantity,added,exp_days from fridge")
   f = np.asarray(cur.fetchall())
   ingredients = np.asarray([])
   for ing in f:
      name = ing[0]
      quantity = ing[1]
      added = ing[2]
      exp_on = added + datetime.timedelta(ing[3])
      days_to_exp = exp_on - datetime.date.today()

      msg = ' '.join([name,str(int(quantity)),str(days_to_exp)])
      ingredients = np.append(ingredients,msg)
   
   cur.close()
   conn.close()
   return ingredients
   
def get_recipes():
   #global TEST_ING, TEST_NOT, TEST_REC
   #return TEST_REC
   """Implements recipe suggestion algorithm.
      Formats each recipe as np.asarray([[recipe1,recipe2,...],[id1,id2,...]])
      where recipei = 'name %match'
      %match = #ing in fridge used by recipe/# total ing used by recipe
   """
   #pass
   max_recipes = np.asarray([0,0,0,0,0])  #IDs of max overlap recipes
   max_overlap = np.asarray([0,0,0,0,0])

   conn = psycopg2.connect('dbname=grocery_guard')
   cur = conn.cursor()
   cur.execute("select id from fridge")
   I = np.asarray(cur.fetchall())
   cur.execute("select id from recipes")
   recipes = np.asarray(cur.fetchall())
   #j=0
   
   #get max recipe ID to use as loop control
   cur.execute("select id from recipes where id = (select max(id) from recipes)")
   num_recs = int(cur.fetchone()[0])
   print "number of recipes: ", num_recs
   
   #print 'r',max_recipes,'o', max_overlap
   #print "---------------------------------------"
   #Get list of recipe IDs from SQL
   for r in range(1,num_recs+1):
      #get row for recipe ID r from SQL as numpy array
      cur.execute("select ingredients from recipes where id = %s" % str(r))
      ri = np.asarray(cur.fetchone())[0]  #ingredients for recipe r
      cur.execute("select amounts from recipes where id = %s" % str(r))
      ra = np.asarray(cur.fetchone())[0]  #amounts for recipe r
      #ri =np.asarray(recipes[j][1]) # r's ingredients
      s = np.intersect1d(ri,I)
      n = s.size
      #print "ingredients ", I
      #print "required    ", ri
      #print "difference  ", I-ri
      #print "overlap     ", n
      for i in s:
         indr = np.where(ri==i)[0][0] # index of i in r's ingredient list
         #indi = np.where(ingredients[:,0]==i)[0][0]
         #cur.execute("select id from fridge where id = %s" % str(i))
         #indi = int(cur.fetchone()[0])
         #Get Ingredient row for ID indi from SQL as numpy array
         cur.execute("select quantity from fridge where id = %s" % str(int(i)))
         tmp = cur.fetchone()[0]
         if tmp < ra[indr] : #amount of ingredient i
            print "subtracted ", r
            n-=1
            #n+=1
         # print 'recipe: ',r[0]
         # print indi, indr
   
      #print "recipe: " + str(r), "overlap: ", n
      m = np.min(max_overlap)
   
      n = float(n)/ra.shape[0] #convert to percentage
      if n > m:
         #print "m: ",m, "n: ",n
         ind = np.where(max_overlap==m)[0][0]
         #print ind
         max_overlap = np.delete(max_overlap,ind)
         max_overlap = np.append(max_overlap,n)
         max_recipes = np.delete(max_recipes,ind)
         max_recipes = np.append(max_recipes,r)

   #get recipe names
   names = np.asarray([])
   for i in range(max_recipes.size):
      cur.execute("select name from recipes where id = %s" % str(max_recipes[i]))
      try:
         result = cur.fetchone()[0]
      except:
         result = ' '
      names = np.append(names,result + ' ' + str(max_overlap[i]))

   return np.asarray([names,max_recipes])


"""Compute notifications based on ingredients list?"""
def get_notifications(ingredients):
   EXP_DAYS = 5 #number of days til expiration to trigger notification
   #TBS_LOW = 10 #number of tbs to trigger notification
   ING_LOW = 5 #number of oz to trigger notification
   notifications = np.asarray([])
   for ing in ingredients:
      #parse ingredient into name amount exp days
      ing_list = ing.split()
      print ing_list
      name = " ".join(ing_list[:-4])
      amount = ing_list[-4]
      exp = ing_list[-3]
      
      if int(amount) <= ING_LOW:
         msg = name + ";low"
         notifications = np.append(notifications, msg)
      if int(exp) <= EXP_DAYS:
         if int(exp) < 0:
            msg = name + ";expired " + str(-1*int(exp)) + " days ago"
         else:
            msg = name + ";expiring in " + exp + " days"
         notifications = np.append(notifications, msg)

      """
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
      """
   return notifications

def cook_recipe(id):
   pass


if __name__ == "__main__":
      #ingredients = TEST_ING

      #recipes = TEST_REC
      #display_item_added(get_item_name(100),100)
      #display_fridge(ingredients,0)
      #display_recipes(recipes)
      home_screen()
