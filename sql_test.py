#!/usr/bin/env python


import MySQLdb as sql

db = sql.connect("localhost","monitor","password","temps")
curs = db.cursor()

try:
    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE() - INTERVAL 1 DAY, NOW(), 'kitchen', 21.7)""")
    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE() - INTERVAL 1 DAY, NOW(), 'greenhouse', 24.5)""")
    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE() - INTERVAL 1 DAY, NOW(), 'garage', 18.1)""")

    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE(), NOW() - INTERVAL 12 HOUR, 'kitchen', 20.6)""")
    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE(), NOW() - INTERVAL 12 HOUR, 'greenhouse', 17.1)""")
    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE(), NOW() - INTERVAL 12 HOUR, 'garage', 16.2)""")

    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE(), NOW(), 'kitchen', 22.9)""")
    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE(), NOW(), 'greenhouse', 25.7)""")
    curs.execute ("""INSERT INTO tempdat 
            values(CURRENT_DATE(), NOW(), 'garage', 18.2)""")

    db.commit()
    print "Data committed"

except:
    print "Error: the database is being rolled back"
    db.rollback()


curs.execute ("SELECT * FROM tempdat")

print "\nDate     	Time		Zone		Temperature"
print "==========================================================="

for reading in curs.fetchall():
    print str(reading[0])+"	"+str(reading[1])+" 	"+\
                reading[2]+"  	"+str(reading[3])

db.close()
