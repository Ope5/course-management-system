import sqlite3
import sys
from getpass import getpass
import student
import instructor
import admin

def clear(): print("\033c", end="")
def pause(): input("\nPress Enter to continue...")

def login(conn):
    cursor = conn.cursor()
    clear()
    print('='*60)
    print('LOGIN')
    print('='*60)
    uid = input('Enter UID: ')
    cursor.execute('''SELECT uid FROM users
                    WHERE uid=:uid;''', {'uid':uid})
    uidRow = cursor.fetchall()
    if(not uidRow): #empty means no match
        print('Not a valid UID')
        pause()
        return

    pwd = getpass('Enter Password: ')
    cursor.execute('''SELECT pwd FROM users
                    WHERE uid=:uid;''', {'uid':uid})
    pwdRow = cursor.fetchone()
    if(pwdRow == None or pwdRow[0] != pwd): 
        print('Incorrect Password')
        pause()
        return
        

    cursor.execute('''SELECT * FROM users
                   WHERE uid=:uid;''', {'uid':uid})
    userRow = cursor.fetchone()
    user = {
        'uid': userRow[0],
        'name': userRow[1],
        'email': userRow[2],
        'role': userRow[3]
    }

    #REPLACE PASS WITH FUNCTION CALLS WHEN READY
    if(user['role'] == 'Student'): student.student_menu(conn, user)
    if(user['role'] == 'Instructor'): instructor.instructor_menu(conn, user)
    if(user['role'] == 'Admin'): admin.adminMenu(conn)

def register(conn):
    #ONLY FOR STUDENTS
    #ASSUME INSTRUCTORS & ADMIN ALREADY IN SYSTEM
    cursor = conn.cursor()
    
    clear()
    print('='*60)
    print('REGISTRATION')
    print('='*60)
    name = input('Enter your Full Name: ')
    email = input('Enter your E-Mail Address: ')
    cursor.execute('''SELECT email FROM users
                    WHERE email=:email;''',{'email':email})
    emRow = cursor.fetchall()
    if(emRow): #empty means not taken
        print('Email already in use')
        pause()
        return

    pwd = getpass('Enter your Password: ')
    role = 'Student' #Only students can register

    cursor.execute("SELECT MAX(CAST(uid AS INTEGER)) FROM users")
    maxUID = cursor.fetchone()[0]
    newUID = str((maxUID or 0) + 1)

    cursor.execute('''INSERT INTO users VALUES (:uid, :name, :email, :role, :pwd);''', {'uid':newUID, 'name':name, 'email':email, 'role':role, 'pwd':pwd})

    conn.commit()
    print('\n*** YOUR NEW UID IS:', newUID, '***') 
    pause()
    login(conn)

def mainMenu(conn):
    while(1):
        clear()
        print('='*60)
        print('MAIN MENU')
        print(('='*60) + "\n1. Login\n2. Register\n0. Exit\n" + ('='*60))
        choice = input('Choice: ')
        if(choice == '1'):
            login(conn)
            break
        elif(choice == '2'):
            register(conn)
            break
        elif(choice == '0'):
            print('Goodbye!')
            conn.commit()
            conn.close()
            sys.exit(0)
            break
        print('Invalid Choice. Please try again')
        pause()

if __name__ == "__main__":
    conn = sqlite3.connect(sys.argv[1])
    conn.row_factory = sqlite3.Row
    while(1):
        mainMenu(conn)

    

    
    