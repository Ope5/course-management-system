# Course Management System

A terminal-based course management platform built using Python and SQLite.  
This system supports multiple user roles (Student, Instructor, Admin) and provides functionality for course enrollment, grading, and analytics.

---

## 🚀 Features

### 👨‍🎓 Student
- Search courses with filters (keyword, category, price range)
- Enroll in courses with payment validation
- View enrolled courses and track progress
- Complete lessons and view grades
- View certificates upon course completion
- Access payment history

### 👨‍🏫 Instructor
- View and manage assigned courses
- Update course details (price, pass grade, max students)
- Override enrollment limits to add students manually
- View course statistics (enrollment, completion rate, average grades)

### 🛠️ Admin
- View top 5 courses by enrollment
- Analyze payment counts per course

---

## 🧱 Tech Stack

- Language: Python  
- Database: SQLite  
- Interface: Command-Line Interface (CLI)

---

## 🗂️ Project Structure

main.py        # Entry point (login + registration)  
student.py     # Student functionalities  
instructor.py  # Instructor functionalities  
admin.py       # Admin functionalities  

---

## ⚙️ Setup Instructions

1. Clone the repository:
git clone https://github.com/yourusername/course-management-system.git
cd course-management-system

2. Create and initialize the database:
sqlite3 prj.db < setup.sql

3. Run the program:
python main.py prj.db

---

## 🔑 Sample Login Credentials

Student  
UID: 1  
Password: pass123  

Instructor  
UID: 3  
Password: pass123  

Admin  
UID: 4  
Password: admin123  

---

## 📌 Key Concepts Implemented

- Role-based access control  
- Relational database design  
- SQL queries (joins, aggregation, filtering)  
- Input validation and error handling  
- Pagination for large datasets  

---

## 📈 Future Improvements

- Add GUI or web interface  
- Implement password hashing  
- Improve UI/UX design  
- Add more advanced analytics  

---

## 👤 Author

Ope Odubela  
Software Engineering Student @ University of Alberta
