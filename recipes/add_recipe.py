import sys
import base64
import psycopg2

def main(recipe):
    with open(recipe + '.txt') as fin:
        print 'reading txt'
        lines = fin.readlines()
        ID,name,ingredients,amounts = lines[0][:-1].split(';')
        lines = lines[1:]
        instructions = ''
        for line in lines:
            instructions = instructions + line
    with open(recipe + '.jpg') as fin:
        print 'reading image'
        image = base64.b64encode(fin.read())
    write_to_db(ID,name,ingredients,amounts,instructions,image)

def write_to_db(ID,name,ingredients,amounts,instructions,image):
    print 'db'
    conn = psycopg2.connect('dbname=grocery_guard')
    print 'connected'
    cur = conn.cursor()
    cmd = 'insert into recipes values (%s,\'%s\',\'%s\',\'%s\',\'%s\',decode(E\'%s\',\'base64\'));' % (ID,name,ingredients,amounts,instructions,image)
    #print cmd
    #cmd = 'insert into recipes values (%s,\'%s\',\'%s\',\'%s\',\'%s\',decode(E\'123\\\\000456\',\'escape\'));' % (ID,name,ingredients,amounts,instructions)
    #print cmd
    try:
        #cmd = 'insert into recipes values (%s,\'%s\',\'%s\',\'%s\',\'%s\');' % (ID,name,ingredients,amounts,instructions)
        #print cmd
        cur.execute(cmd)
    except Exception, e:
        print e.pgerror
    #print cmd
    conn.commit()
    conn.close()
if __name__ == "__main__":
    if len(sys.argv)<2:
        pass
    else:
        print 'main'
        main(sys.argv[1])
