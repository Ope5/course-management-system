-- =========================
-- RESET TABLES
-- =========================
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS completion;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS certificates;
DROP TABLE IF EXISTS payments;

-- =========================
-- CREATE TABLES
-- =========================
CREATE TABLE users (
    uid TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    role TEXT,
    pwd TEXT
);

CREATE TABLE courses (
    cid INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    category TEXT,
    price REAL,
    pass_grade REAL,
    max_students INTEGER
);

CREATE TABLE enrollments (
    cid INTEGER,
    uid TEXT,
    start_ts TEXT DEFAULT CURRENT_TIMESTAMP,
    end_ts TEXT,
    role TEXT,
    PRIMARY KEY (cid, uid, role)
);

CREATE TABLE modules (
    cid INTEGER,
    mid INTEGER,
    name TEXT,
    summary TEXT,
    weight REAL,
    PRIMARY KEY (cid, mid)
);

CREATE TABLE lessons (
    cid INTEGER,
    mid INTEGER,
    lid INTEGER,
    title TEXT,
    duration INTEGER,
    content TEXT,
    PRIMARY KEY (cid, mid, lid)
);

CREATE TABLE completion (
    uid TEXT,
    cid INTEGER,
    mid INTEGER,
    lid INTEGER,
    ts TEXT,
    PRIMARY KEY (uid, cid, mid, lid)
);

CREATE TABLE grades (
    uid TEXT,
    cid INTEGER,
    mid INTEGER,
    received_ts TEXT,
    grade REAL
);

CREATE TABLE certificates (
    cid INTEGER,
    uid TEXT,
    received_ts TEXT,
    final_grade REAL
);

CREATE TABLE payments (
    uid TEXT,
    cid INTEGER,
    ts TEXT,
    credit_card_no TEXT,
    expiry_date TEXT
);

-- =========================
-- USERS
-- =========================
INSERT INTO users VALUES ('1', 'Alice Johnson', 'alice@email.com', 'Student', 'pass123');
INSERT INTO users VALUES ('2', 'Bob Smith', 'bob@email.com', 'Student', 'pass123');
INSERT INTO users VALUES ('3', 'Dr. Brown', 'brown@email.com', 'Instructor', 'pass123');
INSERT INTO users VALUES ('4', 'Admin User', 'admin@email.com', 'Admin', 'admin123');

-- =========================
-- COURSES
-- =========================
INSERT INTO courses VALUES (101, 'Intro to Databases', 'Learn SQL and relational design', 'Database', 100, 50, 2);
INSERT INTO courses VALUES (102, 'Python Programming', 'Learn Python basics', 'Programming', 80, 60, 3);

-- =========================
-- INSTRUCTOR ENROLLMENTS
-- =========================
INSERT INTO enrollments VALUES (101, '3', CURRENT_TIMESTAMP, datetime('now','+1 year'), 'Instructor');
INSERT INTO enrollments VALUES (102, '3', CURRENT_TIMESTAMP, datetime('now','+1 year'), 'Instructor');

-- =========================
-- STUDENT ENROLLMENTS
-- =========================
INSERT INTO enrollments VALUES (101, '1', CURRENT_TIMESTAMP, datetime('now','+1 year'), 'Student');
INSERT INTO enrollments VALUES (101, '2', CURRENT_TIMESTAMP, datetime('now','+1 year'), 'Student');

-- =========================
-- MODULES
-- =========================
INSERT INTO modules VALUES (101, 1, 'SQL Basics', 'Intro to SQL', 50);
INSERT INTO modules VALUES (101, 2, 'Advanced Queries', 'Joins and aggregation', 50);

-- =========================
-- LESSONS
-- =========================
INSERT INTO lessons VALUES (101, 1, 1, 'SELECT Statements', 20, 'Basic SELECT queries');
INSERT INTO lessons VALUES (101, 1, 2, 'WHERE Clause', 15, 'Filtering data');
INSERT INTO lessons VALUES (101, 2, 1, 'JOINs', 25, 'Combining tables');
INSERT INTO lessons VALUES (101, 2, 2, 'GROUP BY', 20, 'Aggregation');

-- =========================
-- COMPLETION (Alice completed full course)
-- =========================
INSERT INTO completion VALUES ('1', 101, 1, 1, CURRENT_TIMESTAMP);
INSERT INTO completion VALUES ('1', 101, 1, 2, CURRENT_TIMESTAMP);
INSERT INTO completion VALUES ('1', 101, 2, 1, CURRENT_TIMESTAMP);
INSERT INTO completion VALUES ('1', 101, 2, 2, CURRENT_TIMESTAMP);

-- =========================
-- GRADES
-- =========================
INSERT INTO grades VALUES ('1', 101, 1, CURRENT_TIMESTAMP, 85);
INSERT INTO grades VALUES ('1', 101, 2, CURRENT_TIMESTAMP, 90);

-- =========================
-- PAYMENTS
-- =========================
INSERT INTO payments VALUES ('1', 101, CURRENT_TIMESTAMP, '1234567812345678', '12/2026');
INSERT INTO payments VALUES ('2', 101, CURRENT_TIMESTAMP, '8765432187654321', '11/2026');
