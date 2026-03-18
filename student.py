"""
CS291 mini Project 1
student portion! 
"""

import sys
from datetime import datetime, timedelta

# Constants
ITEMS_PER_PAGE = 5

# ===================
# useful tools i need
# ===================

def clear(): print("\033c", end="")
def pause(): input("\nPress Enter to continue...")

def format_date(d):
    if not d: return "N/A"
    try: return datetime.strptime(d, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    except: return d

def now(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def mask_card(card):
    c = ''.join([x for x in card if x.isdigit()])
    return '*' * (len(c)-4) + c[-4:] if len(c) >= 4 else '*' * len(c)

def valid_card(c):
    c = c.replace(' ', '')
    return c.isdigit() and len(c) == 16

def valid_expiry(e):
    try:
        e = e.replace('/', '')
        if len(e) != 4: return False
        m, y = int(e[:2]), int(e[2:]) + 2000
        return 1 <= m <= 12 and datetime(y, m, 1) >= datetime.now().replace(day=1)
    except: return False

def paginate(items, page, title):
    total = len(items)
    pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    if total == 0: print("\nNo items."); return 'back'
    if page < 1: page = 1
    elif page > pages: page = pages
    
    start = (page - 1) * ITEMS_PER_PAGE
    end = min(start + ITEMS_PER_PAGE, total)
    
    print(f"\n{'='*60}\n{title:^60}\n{'='*60}")
    print(f"Page {page}/{pages} ({start+1}-{end} of {total})\n{'-'*60}")
    for i, item in enumerate(items[start:end], 1): print(f"{i}. {item['text']}")
    print('-'*60)
    if page > 1: print("P - Previous")
    if page < pages: print("N - Next")
    print("B - Back\nQ - Logout\n" + '='*60)
    
    while True:
        c = input("Choice: ").upper()
        if c == 'P' and page > 1: return 'prev'
        if c == 'N' and page < pages: return 'next'
        if c == 'B': return 'back'
        if c == 'Q': return 'logout'
        if c.isdigit():
            idx = int(c) - 1
            if 0 <= idx < len(items[start:end]): return items[start + idx]['id']
        print("Invalid choice.")

# ============
# student menu
# ============

def student_menu(conn, user):
    while True:
        clear()
        print('='*60)
        print(f"STUDENT: {user['name']} (ID: {user['uid']})")
        print('='*60)
        print("1. Search Courses")
        print("2. My Enrolled Courses")
        print("3. Payment History")
        print("L. Logout")
        print("0. Exit")
        print('='*60)
        
        c = input("Choice: ").upper()
        if c == '1': search_courses(conn, user)
        elif c == '2': enrolled_courses(conn, user)
        elif c == '3': payment_history(conn, user)
        elif c == 'L': return
        elif c == '0': sys.exit(0)
        else: print("Invalid"); pause()

# ==================
# search for course 
# ==================

def search_courses(conn, user):
    page = 1
    params = None
    while True:
        clear()
        print('='*60)
        print("COURSE SEARCH")
        print('='*60)
        
        if page == 1 or params is None:
            params = {}
            k = input("Keyword (Enter to skip): ").strip().lower()
            if k: params['k'] = k
            cat = input("Category (Enter to skip): ").strip().lower()
            if cat: params['cat'] = cat
            try:
                minp = input("Min price (Enter to skip): ").strip()
                if minp: params['min'] = float(minp)
                maxp = input("Max price (Enter to skip): ").strip()
                if maxp: params['max'] = float(maxp)
            except: print("Invalid price")
        
        cursor = conn.cursor()
        q = """
            SELECT c.cid, c.title, c.price, c.max_students,
                   COUNT(DISTINCT e.uid) as enrolled
            FROM courses c
            LEFT JOIN enrollments e ON c.cid = e.cid AND e.role='Student'
                AND datetime('now') BETWEEN e.start_ts AND e.end_ts
            WHERE 1=1
        """
        vals = []
        if 'k' in params:
            q += " AND (LOWER(c.title) LIKE ? OR LOWER(c.description) LIKE ?)"
            vals.extend([f'%{params["k"]}%', f'%{params["k"]}%'])
        if 'cat' in params:
            q += " AND LOWER(c.category)=?"
            vals.append(params['cat'])
        if 'min' in params:
            q += " AND c.price>=?"
            vals.append(params['min'])
        if 'max' in params:
            q += " AND c.price<=?"
            vals.append(params['max'])
        q += " GROUP BY c.cid ORDER BY c.title"
        
        cursor.execute(q, vals)
        courses = cursor.fetchall()
        
        if not courses:
            print("\nNo courses found.")
            if input("Search again? (y/n): ").lower() == 'y':
                page = 1
                params = None
                continue
            return
        
        items = []
        for c in courses:
            pct = (c['enrolled']/c['max_students']*100) if c['max_students']>0 else 0
            bar = '█' * int(pct/10) + '░' * (10 - int(pct/10))
            items.append({
                'id': c['cid'],
                'text': f"ID:{c['cid']} | {c['title'][:30]} | ${c['price']} | [{bar}] {c['enrolled']}/{c['max_students']}"
            })
        
        res = paginate(items, page, "SEARCH RESULTS")
        if res == 'prev': page -= 1
        elif res == 'next': page += 1
        elif res == 'back': return
        elif res == 'logout': return
        elif res: course_details(conn, user, res)

def course_details(conn, user, cid):
    clear()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, COUNT(DISTINCT e.uid) as enrolled
        FROM courses c
        LEFT JOIN enrollments e ON c.cid=e.cid AND e.role='Student'
            AND datetime('now') BETWEEN e.start_ts AND e.end_ts
        WHERE c.cid=?
        GROUP BY c.cid
    """, (cid,))
    c = cursor.fetchone()
    if not c: print("Not found"); pause(); return
    
    cursor.execute("SELECT * FROM enrollments WHERE cid=? AND uid=? AND role='Student' AND datetime('now') BETWEEN start_ts AND end_ts", (cid, user['uid']))
    enrolled = cursor.fetchone() is not None
    
    print('='*60)
    print(f"CID: {c['cid']}\nTitle: {c['title']}\nDesc: {c['description']}")
    print(f"Category: {c['category']}\nPrice: ${c['price']}\nPass: {c['pass_grade']}%")
    print(f"Enrolled: {c['enrolled']}/{c['max_students']}")
    spots = c['max_students'] - c['enrolled']
    print('='*60)
    
    if enrolled: print("Already enrolled"); pause(); return
    if spots <= 0: print("Course full"); pause(); return
    
    if input("\nEnroll? (1=yes, 0=no): ") == '1':
        enroll(conn, user, c)

def enroll(conn, user, course):
    clear()
    print('='*60)
    print(f"ENROLL: {course['title']} - ${course['price']}")
    print('='*60)
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM enrollments WHERE cid=? AND role='Student' AND datetime('now') BETWEEN start_ts AND end_ts", (course['cid'],))
    if cursor.fetchone()['cnt'] >= course['max_students']:
        print("Sorry, course filled up."); pause(); return
    
    card = input("Card number (16 digits): ").strip()
    while not valid_card(card):
        card = input("Invalid. Enter 16 digits: ").strip()
    
    cvv = input("CVV (3 digits): ").strip()
    while not (cvv.isdigit() and len(cvv)==3):
        cvv = input("Invalid. Enter 3 digits: ").strip()
    
    exp = input("Expiry (MM/YY): ").strip()
    while not valid_expiry(exp):
        exp = input("Invalid. Use MM/YY: ").strip()
    
    now_ts = now()
    end = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("INSERT INTO enrollments (cid,uid,start_ts,end_ts,role) VALUES (?,?,?,?,'Student')", 
                      (course['cid'], user['uid'], now_ts, end))
        cursor.execute("INSERT INTO payments (uid,cid,ts,credit_card_no,expiry_date) VALUES (?,?,?,?,?)",
                      (user['uid'], course['cid'], now_ts, card, exp))
        conn.commit()
        print("\n✓ ENROLLED!")
        print(f"Course: {course['cid']} - {course['title']}")
        print(f"Date: {format_date(now_ts)}")
        print(f"Card: {mask_card(card)}")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    pause()

# ========
# enrolled
# ========
def enrolled_courses(conn, user):
    page = 1
    while True:
        clear()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.cid, c.title, c.pass_grade, e.start_ts,
                   (SELECT COUNT(*) FROM lessons l WHERE l.cid=c.cid) as total,
                   (SELECT COUNT(*) FROM completion comp WHERE comp.uid=? AND comp.cid=c.cid) as done
            FROM enrollments e JOIN courses c ON e.cid=c.cid
            WHERE e.uid=? AND e.role='Student' AND datetime('now') BETWEEN e.start_ts AND e.end_ts
            ORDER BY e.start_ts DESC
        """, (user['uid'], user['uid']))
        
        courses = cursor.fetchall()
        if not courses:
            print("\nNo enrolled courses."); pause(); return
        
        items = []
        for c in courses:
            pct = (c['done']/c['total']*100) if c['total']>0 else 0
            bar = '█' * int(pct/10) + '░' * (10 - int(pct/10))
            items.append({
                'id': c['cid'],
                'text': f"ID:{c['cid']} | {c['title'][:30]} | [{bar}] {pct:.0f}% | Pass: {c['pass_grade']}%"
            })
        
        res = paginate(items, page, "MY COURSES")
        if res == 'prev': page -= 1
        elif res == 'next': page += 1
        elif res == 'back': return
        elif res == 'logout': return
        elif res: course_menu(conn, user, res)

def course_menu(conn, user, cid):
    while True:
        clear()
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM courses WHERE cid=?", (cid,))
        c = cursor.fetchone()
        if not c: return
        
        print('='*60)
        print(f"COURSE: {c['title']}")
        print('='*60)
        print("1. View Modules")
        print("2. View Grades")
        print("3. View Certificate")
        print("B. Back")
        print('='*60)
        
        ch = input("Choice: ").upper()
        if ch == '1': view_modules(conn, user, cid)
        elif ch == '2': view_grades(conn, user, cid)
        elif ch == '3': view_cert(conn, user, cid)
        elif ch == 'B': return

def view_modules(conn, user, cid):
    page = 1
    while True:
        clear()
        cursor = conn.cursor()
        cursor.execute("SELECT mid, name, weight FROM modules WHERE cid=? ORDER BY mid", (cid,))
        mods = cursor.fetchall()
        if not mods: print("No modules"); pause(); return
        
        items = [{'id': m['mid'], 'text': f"Module {m['mid']}: {m['name'][:30]} | Weight: {m['weight']}%"} for m in mods]
        res = paginate(items, page, "MODULES")
        if res == 'prev': page -= 1
        elif res == 'next': page += 1
        elif res == 'back': return
        elif res == 'logout': return
        elif res: view_lessons(conn, user, cid, res)

def view_lessons(conn, user, cid, mid):
    page = 1
    while True:
        clear()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM modules WHERE cid=? AND mid=?", (cid, mid))
        m = cursor.fetchone()
        mname = m['name'] if m else f"Module {mid}"
        
        cursor.execute("""
            SELECT l.lid, l.title, l.duration,
                   CASE WHEN c.lid IS NOT NULL THEN '✓' ELSE '○' END as status
            FROM lessons l
            LEFT JOIN completion c ON l.cid=c.cid AND l.mid=c.mid AND l.lid=c.lid AND c.uid=?
            WHERE l.cid=? AND l.mid=?
            ORDER BY l.lid
        """, (user['uid'], cid, mid))
        less = cursor.fetchall()
        if not less: print("No lessons"); pause(); return
        
        items = [{'id': l['lid'], 'text': f"L{l['lid']}: {l['title'][:30]} | {l['duration']}min | {l['status']}"} for l in less]
        res = paginate(items, page, f"LESSONS - {mname}")
        if res == 'prev': page -= 1
        elif res == 'next': page += 1
        elif res == 'back': return
        elif res == 'logout': return
        elif res: lesson_detail(conn, user, cid, mid, res)

def lesson_detail(conn, user, cid, mid, lid):
    clear()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.*, CASE WHEN c.lid IS NOT NULL THEN '✓' ELSE '○' END as status
        FROM lessons l
        LEFT JOIN completion c ON l.cid=c.cid AND l.mid=c.mid AND l.lid=c.lid AND c.uid=?
        WHERE l.cid=? AND l.mid=? AND l.lid=?
    """, (user['uid'], cid, mid, lid))
    l = cursor.fetchone()
    if not l: print("Not found"); pause(); return
    
    print('='*60)
    print(f"Lesson {lid}: {l['title']}")
    print(f"Duration: {l['duration']}min")
    print(f"Status: {'Completed' if l['status']=='✓' else 'Not Started'}")
    print('-'*60)
    print("CONTENT:")
    print(l['content'])
    print('='*60)
    
    if l['status'] == '○':
        if input("\nMark complete? (1=yes, 0=no): ") == '1':
            mark_done(conn, user, cid, mid, lid)
    else:
        pause()

def mark_done(conn, user, cid, mid, lid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM completion WHERE uid=? AND cid=? AND mid=? AND lid=?", (user['uid'], cid, mid, lid))
    if cursor.fetchone():
        print("Already completed"); pause(); return
    
    try:
        cursor.execute("INSERT INTO completion (uid,cid,mid,lid,ts) VALUES (?,?,?,?,?)", 
                      (user['uid'], cid, mid, lid, now()))
        conn.commit()
        print("\n✓ Lesson completed!")
        
        cursor.execute("""
            SELECT COUNT(*) as total, COUNT(c.lid) as done
            FROM lessons l LEFT JOIN completion c ON l.cid=c.cid AND l.mid=c.mid AND l.lid=c.lid AND c.uid=?
            WHERE l.cid=?
        """, (user['uid'], cid))
        r = cursor.fetchone()
        if r['done'] == r['total'] and r['total'] > 0:
            print("\n🎉 CONGRATULATIONS! You completed all lessons!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    pause()

# ======
# grades
# ======
def view_grades(conn, user, cid):
    clear()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.mid, m.name, m.weight, g.grade
        FROM modules m
        LEFT JOIN grades g ON m.cid=g.cid AND m.mid=g.mid AND g.uid=?
        WHERE m.cid=?
        ORDER BY m.mid
    """, (user['uid'], cid))
    grades = cursor.fetchall()
    
    if not grades:
        print("No grades"); pause(); return
    
    print('='*60)
    print("GRADES")
    print('='*60)
    print(f"{'Mod':<4} {'Module':<30} {'Wgt':<6} {'Grade'}")
    print('-'*60)
    
    total_w = 0
    weighted = 0
    for g in grades:
        grade = f"{g['grade']}%" if g['grade'] else 'N/A'
        print(f"{g['mid']:<4} {g['name'][:28]:<30} {g['weight']:<6} {grade}")
        if g['grade']:
            total_w += g['weight']
            weighted += g['grade'] * g['weight']
    
    print('-'*60)
    if total_w > 0:
        print(f"FINAL GRADE: {weighted/total_w:.2f}%")
    else:
        print("FINAL GRADE: N/A")
    print('='*60)
    pause()

# ====
# cert
# ====

def view_cert(conn, user, cid):
    clear()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cert.*, c.title
        FROM certificates cert
        JOIN courses c ON cert.cid=c.cid
        WHERE cert.uid=? AND cert.cid=?
        ORDER BY cert.received_ts DESC LIMIT 1
    """, (user['uid'], cid))
    cert = cursor.fetchone()
    
    if not cert:
        print("No certificate found"); pause(); return
    
    print('='*60)
    print("CERTIFICATE OF COMPLETION")
    print('='*60)
    print(f"\n{user['name']}\n")
    print(f"has completed\n")
    print(f"{cert['title']}\n")
    print('='*60)
    print(f"Date: {format_date(cert['received_ts'])}")
    print(f"Grade: {cert['final_grade']}%")
    print('='*60)
    pause()

# ===============
# payment history
# ===============

def payment_history(conn, user):
    page = 1
    while True:
        clear()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.ts, p.cid, c.title, p.credit_card_no
            FROM payments p
            JOIN courses c ON p.cid=c.cid
            WHERE p.uid=?
            ORDER BY p.ts DESC
        """, (user['uid'],))
        pays = cursor.fetchall()
        
        if not pays:
            print("No payments"); pause(); return
        
        items = []
        for p in pays:
            items.append({
                'id': p['cid'],
                'text': f"{format_date(p['ts'])} | {p['title'][:25]} | Card: {mask_card(p['credit_card_no'])}"
            })
        
        res = paginate(items, page, "PAYMENTS")
        if res == 'prev': page -= 1
        elif res == 'next': page += 1
        elif res == 'back': return
        elif res == 'logout': return
        elif res: payment_detail(conn, user, res)

def payment_detail(conn, user, cid):
    clear()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, c.title
        FROM payments p
        JOIN courses c ON p.cid=c.cid
        WHERE p.uid=? AND p.cid=?
        ORDER BY p.ts DESC LIMIT 1
    """, (user['uid'], cid))
    p = cursor.fetchone()
    
    if not p:
        print("Not found"); pause(); return
    
    print('='*60)
    print("PAYMENT DETAILS")
    print('='*60)
    print(f"Date: {format_date(p['ts'])}")
    print(f"Course: {p['title']} (ID: {p['cid']})")
    print(f"Card: {mask_card(p['credit_card_no'])}")
    print(f"Expiry: {p['expiry_date']}")
    print('='*60)
    pause()


#500 lines of code, mostly just print statements and c.execute tho LMAOOOOO is this efficent? no, does it work? WE shall see!!!!
