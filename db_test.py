""" This program simulates a SQL database to test our recipe suggestion algorithm"""
import numpy as np

# table of recipes.
#             ID   ingredients  amounts
recipes = np.asarray([[[1],     [2,5,8,4],   [4,2,6,3]],
                      [[2],     [5,7,1,2],   [8,9,3,4]],
                      [[3],     [6,7,3],     [6,9,8]],
                      [[4],     [2,5,8,9,3], [4,5,6,3,2]]])

#table of available ingredients
#               ID   amount
ingredients = np.asarray([[1,   4],
                          [2,   5],
                          [3,   1],
                          [4,   4],
                          [5,   8],
                          [6,   6],
                          [7,   7],
                          [8,   2],
                          [9,   5]])

max_recipes = np.asarray([0,0,0,0])  #IDs of max overlap recipes
max_overlap = np.asarray([0,0,0,0])

#Get ingredient IDs from SQL as numpy array
I = ingredients[:,0] # array of ingredient IDs

j=0
#Get list of recipe IDs from SQL
for r in recipes:
   #get row for recipe ID r from SQL as numpy array
   ri =np.asarray(recipes[j][1])
   s = np.intersect1d(ri,I)
   n = s.size
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
   if n > m:
      max_overlap = np.delete(max_overlap,np.where(max_overlap==m)[0][0])
      max_overlap = np.append(max_overlap,n)

      max_recipes = np.delete(max_recipes,np.where(max_recipes==m)[0][0])
      max_recipes = np.append(max_recipes,r[0])
   j+=1   


print 'recipes: ',max_recipes
print 'sizes:   ',max_overlap



