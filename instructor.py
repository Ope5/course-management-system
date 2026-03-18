import sqlite3
import sys
import os

#for login menu
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nPress Enter to continue...")
    clear()

#for my overideenrollment function
FORCED_CARD_NO = "0000000000000000"
FORCED_EXPIRY = "12/2026"

#instructor menu

def instructor_menu(conn, user):
    while True:
        clear()
        print('='*60)
        print(f"INSTRUCTOR: {user['name']} (ID: {user['uid']})")
        print('='*60)
        print("1. List My Courses")
        print("2. Update Course (price, pass_grade, max_students)")
        print("3. Override Enrollment (force add student)")
        print("4. Course Stats")
        print("L. Logout")
        print("0. Exit")
        print('='*60)

        c = input("Choice: ").upper().strip()

        if c == '1':
            try:
                courses = list_courses(conn, user['uid'])
                clear()
                print("MY COURSES")
                print('='*60)
                if not courses:
                    print("No courses found.")
                else:
                    print("cid | title | category | price | pass_grade | max_students")
                    print('-'*60)
                    for x in courses:
                        print(f"{x['cid']} | {x['title']} | {x['category']} | {x['price']} | {x['pass_grade']} | {x['max_students']}")
                pause()
            except Exception as e:
                print(e); pause()

        elif c == '2':
            try:
                cid = int(input("Enter cid to update: ").strip())

                prev = update_preview(conn, user['uid'], cid)
                clear()
                print("SELECTED COURSE")
                print('='*60)
                # displays the cid, title, category, price, pass_grade, max_students, current_enrollment
                print("cid | title | category | price | pass_grade | max_students | current_enrollment")
                print('-'*60)
                print(f"{prev['cid']} | {prev['title']} | {prev['category']} | {prev['price']} | {prev['pass_grade']} | {prev['max_students']} | {prev['current_enrollment']}")
                print('='*60)

                p = input("New price (blank keep): ").strip()
                g = input("New pass_grade (blank keep): ").strip()
                m = input("New max_students (blank keep): ").strip()

                price = float(p) if p != "" else None
                pass_grade = float(g) if g != "" else None
                max_students = int(m) if m != "" else None

                out = update_course(conn, user['uid'], cid, price=price, pass_grade=pass_grade, max_students=max_students)

                clear()
                print("UPDATED RESULT")
                print('='*60)
                # displays the cid, price, pass_grade, max_students, certificates_added, certificates_removed
                print("cid | price | pass_grade | max_students | certificates_added | certificates_removed")
                print('-'*60)
                print(f"{out['cid']} | {out['price']} | {out['pass_grade']} | {out['max_students']} | {out['certificates_added']} | {out['certificates_removed']}")
                pause()

            except Exception as e:
                print(e); pause()

        elif c == '3':
            try:
                cid = int(input("Enter cid: ").strip())
                student_uid = int(input("Enter student uid: ").strip())

                out = override_enrollment(conn, user['uid'], cid, student_uid)

                clear()
                if out.get("did_insert") is False:
                    print(out.get("message", "No changes made."))
                    print()

                # displays the cid, course_title, uid, student_name, start_ts
                print("cid | course_title | uid | student_name | start_ts")
                print('-'*60)
                print(f"{out['cid']} | {out['course_title']} | {out['uid']} | {out['student_name']} | {out['start_ts']}")
                pause()

            except Exception as e:
                print(e); pause()

        elif c == '4':
            try:
                stats = course_stats(conn, user['uid'])
                clear()
                print("COURSE STATS")
                print('='*60)
                # displays the cid, title, active_enrollment, completion_rate, average_final_grade
                print("cid | title | active_enrollment | completion_rate | average_final_grade")
                print('-'*60)
                if not stats:
                    print("No courses found.")
                else:
                    for s in stats:
                        print(f"{s['cid']} | {s['title']} | {s['active_enrollment']} | {s['completion_rate']} | {s['average_final_grade']}")
                pause()
            except Exception as e:
                print(e); pause()

        elif c == 'L':
            return

        elif c == '0':
            sys.exit(0)

        else:
            print("Invalid")
            pause()
    

def list_courses(conn, inst_uid):
    rows = conn.execute(
       """
        SELECT c.cid, c.title, c.category, c.price, c.pass_grade, c.max_students
        FROM courses c
        JOIN enrollments e ON e.cid = c.cid
        WHERE e.uid=? AND e.role='Instructor'
        ORDER BY c.cid
        """,
        (inst_uid,),
    ).fetchall()

    return [
        {
        "cid": r[0],
        "title": r[1],
        "category": r[2],
        "price" : r[3],
        "pass_grade": r[4],
        "max_students": r[5] 
        }
        for r in rows
    ]

def update_preview(conn, inst_uid, cid):
    #When an instructor chooses a course to update we return cid, title, category, price, pass_grade, max_students, current_enrollment
    if not _teaches(conn, inst_uid, cid):
        raise PermissionError("Instructor may only perform actions on courses they teach")
    course = conn.execute(
        """
        SELECT cid, title, category, price, pass_grade, max_students
        FROM courses 
        WHERE cid=?
        """,
        (cid,),
    ).fetchone()

    if course is None:
        raise ValueError("Course not found")
    return {
        "cid": course[0],
        "title": course[1],
        "category": course[2],
        "price": course[3],
        "pass_grade": course[4],
        "max_students": course[5],
        "current_enrollment": _current_enrollment(conn, cid),
    }    

def update_course(conn, inst_uid, cid, price=None, pass_grade=None, max_students=None):
    if not _teaches(conn, inst_uid, cid):
        raise PermissionError("Instructor may only perform actions on courses they teach.")

    old = conn.execute(
        "SELECT price, pass_grade, max_students FROM courses WHERE cid=?",
        (cid,),
    ).fetchone()
    if old is None:
        raise ValueError("Course not found.")

    old_price, old_pass, old_max = float(old[0]), float(old[1]), int(old[2])

    new_price = old_price if price is None else float(price)
    new_pass  = old_pass  if pass_grade is None else float(pass_grade)
    new_max   = old_max   if max_students is None else int(max_students)

    cert_counts = {"certificates_added":0, "certificates_removed": 0}

    with conn:
        conn.execute(
            "UPDATE courses SET price =?, pass_grade=?, max_students=? WHERE cid=?",
            (new_price, new_pass, new_max, cid)
        )
        if new_pass != old_pass:
            cert_counts = _reevaluate_certificates(conn, cid, new_pass)

    return {
        "cid": cid,
        "price": new_price,
        "pass_grade": new_pass,
        "max_students": new_max,
        **cert_counts,
    }
        

def override_enrollment(conn, inst_uid, cid, student_uid):
    #instructor forces a student into their course even when full
    if not _teaches(conn, inst_uid, cid):
        raise PermissionError("Instructor may only perform actions on courses they teach.")
    
    #See if the student exists
    urow = conn.execute(
    """
    SELECT name FROM users WHERE uid=? AND role='Student'
    """,
    (student_uid,),
    ).fetchone()
    if urow is None:
        raise ValueError("The user id must exist and have role Student.")
    student_name = urow[0]
    
    #to get the course title
    crow = conn.execute(
        "SELECT title FROM courses WHERE cid=?",
        (cid,),
    ).fetchone()
    if crow is None:
        raise ValueError("Course not found.") 
    course_title = crow[0]

    #check if already enrolled in course
    active = conn.execute(
        """
        SELECT start_ts FROM enrollments
        WHERE cid=? AND uid=? AND role='Student'
        AND start_ts <= CURRENT_TIMESTAMP
        AND end_ts >= CURRENT_TIMESTAMP
        ORDER BY start_ts DESC
        LIMIT 1
        """,
        (cid, student_uid),
    ).fetchone()

    if active is not None:
        return {
            "cid": cid,
            "course_title": course_title,
            "uid": student_uid,
            "student_name": student_name,
            "start_ts": active[0],
            "did_insert": False,
            "message": "Student is already actively enrolled; no changes made."
        }
    #insrt enrollment and force the payment
    with conn:
        conn.execute(
            """
            INSERT INTO enrollments (cid,uid,end_ts,role)
            VALUES (?,?,datetime(CURRENT_TIMESTAMP,'+1 year'),'Student')
            """,
            (cid,student_uid),
        )
        conn.execute(
            """
            INSERT INTO payments (uid, cid, ts, credit_card_no, expiry_date)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?) 
            """,
            (student_uid,cid,FORCED_CARD_NO,FORCED_EXPIRY),

        )

    #get the latest start_ts
    start_ts = conn.execute(
        """
        SELECT start_ts FROM enrollments WHERE cid=? AND uid=? AND role='Student'
        ORDER BY start_ts DESC 
        LIMIT 1 
        """,
        (cid,student_uid),
    ).fetchone()[0]
    
    return {
        "cid": cid,
        "course_title": course_title,
        "uid": student_uid,
        "student_name": student_name,
        "start_ts": start_ts,
        "did_insert": True
    }

def course_stats(conn, inst_uid):
    #returns the cid,title,active enrollments completion rate and average final grade
    stats_output = []
    courses = list_courses(conn, inst_uid)

    for c in courses:
        cid = c["cid"]
        uids = _active_student_uids(conn, cid)
        n = len(uids)

        completed = sum(1 for uid in uids if _completed_all_lessons(conn, cid, uid))
        finals = [fg for uid in uids if (fg := _final_grade(conn, cid, uid)) is not None]

        stats_output.append({
            "cid": cid,
            "title": c["title"],
            "active_enrollment": n,
            "completion_rate": 0.0 if n == 0 else round((completed / n) * 100.0, 2),
            "average_final_grade": None if not finals else round(sum(finals) / len(finals), 2),
        })

    return stats_output



#helper functions

def _teaches(conn, inst_uid, cid) -> bool:
    row = conn.execute( 
        """
        SELECT 1 FROM enrollments
        WHERE uid=? AND cid=? AND role='Instructor'
        LIMIT 1
        """,
        (inst_uid, cid),
    ).fetchone()
    return row is not None

def _active_student_uids(conn, cid):
    #get the list of uids of studentts who are actively enrolled in course cid
    rows = conn.execute(
        """
        SELECT DISTINCT uid FROM enrollments 
        WHERE cid=? AND role='Student'
        AND start_ts <= CURRENT_TIMESTAMP
        AND end_ts >= CURRENT_TIMESTAMP
        """,
        (cid,),
    ).fetchall()
    return [r[0] for r in rows]

def _current_enrollment(conn, cid) -> int:
    #finds the number of active student enrollments in a course right now
    row = conn.execute(
    """
    SELECT COUNT(*)
    FROM enrollments 
    WHERE cid=? and role ='Student'
    AND start_ts <= CURRENT_TIMESTAMP
    AND end_ts >= CURRENT_TIMESTAMP
    """,
    (cid,),
    ).fetchone()
    return int(row[0])


def _completed_all_lessons(conn, cid, uid) -> bool:
    #TRUE if a studewnt has a complettion role for all lessons in a course
    total = conn.execute(
        "SELECT COUNT(*) FROM lessons WHERE cid=?",
        (cid,),
    ).fetchone()[0]

    if total == 0:
        return True
    
    done = conn.execute(
        """
        SELECT COUNT(*) FROM lessons 
        WHERE lessons.cid=? 
        AND EXISTS(
        SELECT 1
        FROM completion
        WHERE completion.uid=? AND completion.cid = lessons.cid AND completion.mid = lessons.mid AND completion.lid = lessons.lid
        )
        """,
        (cid,uid),
    ).fetchone()[0]

    return int(done) == int(total)


def _final_grade(conn, cid, uid):
    #final grade by using the moduel weights and latest grade per module
    row = conn.execute(
    """
    WITH latest AS(
    SELECT mid, MAX(received_ts) AS mx
    FROM grades WHERE cid=? AND uid=?
    GROUP BY mid
    )
    SELECT SUM(grades.grade * modules.weight) AS num,
    SUM(modules.weight) AS den,
    COUNT(*) AS cnt
    FROM latest
    JOIN grades ON grades.cid=? AND grades.uid=? AND grades.mid=latest.mid and grades.received_ts=latest.mx
    JOIN modules ON modules.cid=? and modules.mid=grades.mid
    """,
    (cid, uid, cid, uid, cid),
    ).fetchone()

    #Takes the sql results and return the weighted average grade
    num,den,cnt = row
    if cnt == 0 or num is None or den is None or float(den) == 0.0:
        return None
    return float(num) / float(den)

def _has_certificate(conn, cid, uid) -> bool:
    #TRUE if the certificate exists for any cid or uid
    return conn.execute(
        """SELECT 1 FROM certificates WHERE cid=? AND uid=? LIMIT 1""",
        (cid,uid),
    ).fetchone() is not None
   

def _insert_certificate(conn, cid, uid, fg):
     #inserts certificates
    conn.execute(
        """
        INSERT INTO certificates (cid, uid, received_ts, final_grade)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?)
        """,
        (cid,uid,fg),
    )

def _delete_certificates(conn, cid, uid) -> int:
    #deletes certificates and tells us how many were deleted
    cursor = conn.execute(
        """DELETE FROM certificates WHERE cid=? AND uid=?""",
        (cid,uid),
    )
    return cursor.rowcount

def _reevaluate_certificates(conn, cid, new_pass):
    added = 0 
    removed = 0
    
    for uid in _active_student_uids(conn,cid):
        completed = _completed_all_lessons(conn, cid, uid)
        fg = _final_grade(conn, cid, uid)
        qualifies = completed and (fg is not None) and (fg >= new_pass)

        has_cert = _has_certificate(conn, cid, uid)

        if qualifies and not has_cert:
            _insert_certificate(conn, cid, uid, fg)
            added +=1
        elif (not qualifies) and has_cert:
            removed += _delete_certificates(conn, cid, uid)
    return {"certificates_added": added, "certificates_removed": removed}

