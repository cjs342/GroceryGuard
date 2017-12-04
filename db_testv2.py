""" This program simulates a SQL database to test our recipe suggestion algorithm"""
import numpy as np
import base64
import psycopg2


# table of recipes.
#             ID   ingredients  amounts
#recipes = np.asarray([[[1],     [2,5,8,4],   [4,2,6,3]],
#                      [[2],     [5,7,1,2],   [8,9,3,4]],
#                      [[3],     [6,7,3],     [6,9,8]],
#                      [[4],     [2,5,8,9,3], [4,5,6,3,2]]])

#table of available ingredients
#               ID   amount
#ingredients = np.asarray([[1,   4],
#                          [2,   5],
#                          [3,   1],
#                          [4,   4],
#                          [5,   8],
#                          [6,   6],
#                          [7,   7],
#                          [8,   2],
#                          [9,   5]])

max_recipes = np.asarray([0,0,0,0,0])  #IDs of max overlap recipes
max_overlap = np.asarray([0,0,0,0,0])

#Get ingredient IDs from SQL as numpy array
#I = ingredients[:,0] # array of ingredient IDs
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
      cur.execute("select quantity from fridge where id = %s" % str(i))
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
      #print 'r',max_recipes
      #print 'o', max_overlap
   #j+=1   


print 'recipes: ',max_recipes
print 'sizes:   ',max_overlap



