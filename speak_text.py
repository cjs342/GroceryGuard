from num2words import num2words
from subprocess import call

cmd_beg = 'espeak '
cmd_end = ' | aplay /home/pi/GroceryGuard/Text.wav  2>/dev/null'
cmd_out = '--stdout > /home/pi/GroceryGuard/Text.wav '

text=raw_input(" ENter text: ")
print(text)

text=text.replace(' ','_')
call([cmd_beg+cmd_out+text+cmd_end], shell=True)
