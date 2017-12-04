""" This program simulates a SQL database to test our recipe suggestion algorithm"""
import numpy as np
import base64
import psycopg2


# table of recipes.
#             ID   ingredients  amounts
recipes = np.asarray([[[1],     [1,2,3,4,5],  [1,1,1,1,1]],
                      [[2],     [5,7,1,2],    [1,9,3,4]],
                      [[3],     [6,7,3],      [1,1,1]],
                      [[4],     [2,5,8,9,3],  [4,5,6,3,2]],
                      [[5],     [1,2,3,4,5],  [1,1,1,1,2]],
                      [[6],     [1,2,3],      [1,1,1]]])

#table of available ingredients
#               ID   amount
ingredients = np.asarray([[1,   1],
                          [2,   1],
                          [3,   1],
                          [4,   1],
                          [5,   1],
                          [6,   1],
                          [7,   1],
                          [8,   1],
                          [9,   1]])

max_recipes = np.asarray([-3,-2,-1,0])  #IDs of max overlap recipes
max_overlap = np.asarray([-3,-2,-1,0])

#Get ingredient IDs from SQL as numpy array
I = ingredients[:,0] # array of ingredient IDs
#conn = psycopg2.connect('dbname=grocery_guard')
#cur = conn.cursor()
#cur.execute("select id from fridge")
#I = np.asarray(cur.fetchall())

#cur.execute("select (id,ingredients,amounts) from recipes")
#recipes = np.asarray(cur.fetchall())
j=0
#Get list of recipe IDs from SQL
for r in recipes:
   #get row for recipe ID r from SQL as numpy array
   ri =np.asarray(recipes[j][1])
   print "ri: ",ri
   s = np.intersect1d(ri,I)
   print "s: ",s
   n = s.size
   print "n: ",n
   for i in s:
      indr = np.where(r[1]==i)[0][0] # index of i in r's ingredient list
      indi = np.where(ingredients[:,0]==i)[0][0]
      #Get Ingredient row for ID indi from SQL as numpy array
      if ingredients[indi,1] < r[2][indr] : #amount of ingredient i
         n-=1
        #n+=1
      # print 'recipe: ',r[0]
      # print indi, indr
      m = np.min(max_overlap)
   #print 'ind: ',ind
   print 'recipes: ',max_recipes
   print 'size: ',max_overlap
   #print 'indi: ',indi
   #print "m: ",m
   #print "n: ",n
   if n > m:
      m = np.min(max_overlap)
      ind = (np.where(max_overlap)==m)
      #inds = (np.where(max_overlap)==m)
      print 'ind: ',ind
      max_overlap = np.delete(max_overlap,ind==True)
      max_overlap = np.append(max_overlap,n)
      max_recipes = np.delete(max_recipes,ind==True)
      max_recipes = np.append(max_recipes,r[0])
   j+=1   


print 'recipes: ',max_recipes
print 'sizes:   ',max_overlap



