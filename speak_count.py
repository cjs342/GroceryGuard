from num2words import num2words
from subprocess import call

cmd_beg = 'espeak '
cmd_end = ' 2>/dev/null'
x= int(raw_input("Enter a no. "))
count =" Count down starts"
print(count)

count= count.replace(' ', '_') #To identify words in the text entered
call([cmd_beg+count+cmd_end], shell=True)

for i in range(x,-1,-1):
   cmd=num2words(i)
   print(i)
   call([cmd_beg+cmd+cmd_end], shell=True)
