import sqlite3
import sys

def clear(): print("\033c", end="")
def pause(): input("\nPress Enter to continue...")
def print_table(headers, rows):
    col_widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0)) for i, h in enumerate(headers)]
    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_row = "| " + " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    print(sep)
    print(header_row)
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers))) + " |")
    print(sep)

def top5(cursor):
    #TOP 5 COURSES BY ENROLLMENT
    #cid, title, active_enrollment
    clear()
    print('='*60)
    print('TOP 5 COURSES REPORT:')
    print('='*60)
    cursor.execute('''SELECT cid, title, active_enrollment FROM (
                   SELECT c.cid, c.title, COUNT(*) AS active_enrollment, RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk
                   FROM enrollments e
                   JOIN courses c ON e.cid=c.cid
                   WHERE e.role='Student' AND (CURRENT_TIMESTAMP BETWEEN e.start_ts AND e.end_ts)
                   GROUP BY c.cid, c.title) ranked
                   WHERE rnk <= 5
                   ORDER BY active_enrollment DESC''')
    rows = cursor.fetchall()
    headers = ["CID", "Title", "Active Enrollment"]
    print_table(headers,rows)
    print('='*60)
    pause()
    
def coursePayment(cursor):
    #PAYMENTS REVIEVED FOR EVERY COURSE
    #cid, title, payment_count
    clear()
    print('='*60)
    print('COURSE PAYMENT REPORT:')
    print('='*60)
    cursor.execute('''SELECT c.cid, c.title, COUNT(p.uid) AS payment_count FROM courses c
                   LEFT JOIN payments p ON c.cid=p.cid
                   GROUP BY c.cid, c.title
                   ORDER BY payment_count DESC;''')
    rows = cursor.fetchall()
    headers = ["CID", "Title", "Payment Count"]
    print_table(headers, rows)
    print('='*60)
    pause()
    
def adminMenu(conn):
    cursor = conn.cursor()
    while(1):
        clear()
        print('ADMIN MENU')
        print(('='*60) + "\n1. Top 5 Courses Report\n2. Course Payment Report\nL. Logout\n0. Exit\n" + ('='*60))
        choice = input('Choice: ')
        if(choice == '1'):
            top5(cursor)
        elif(choice == '2'):
            coursePayment(cursor)
        elif(choice == 'L'):
            print('Goodbye!')
            return
        elif(choice == '0'):
            print('Goodbye!')
            conn.commit()
            conn.close()
            sys.exit(0)
        else:
            print('Invalid Choice. Please try again')
            pause()