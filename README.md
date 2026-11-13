# 🚀 DYNAMIC 2.0 – Smart Study & Productivity Management System

<p align="center">
  <strong>An Integrated Platform for Academic Planning, Task Management and Personal Productivity</strong>
</p>

<p align="center">
  Built with Python • Flask • MySQL • HTML • CSS • JavaScript • Bootstrap
</p>

---

## 📌 About the Project

**DYNAMIC 2.0** is a web-based Smart Study and Productivity Management System developed to help students organize their academic activities, manage daily tasks, schedule important events, and improve their study habits.

The application brings multiple productivity features together in a centralized platform. Instead of relying on separate applications for task tracking, calendar scheduling, study sessions, and productivity management, users can access these functionalities through a single web application.

DYNAMIC 2.0 focuses on providing a structured and user-friendly environment where students can plan their academic activities, monitor their progress, and maintain a more organized study routine.

The system also includes personalized, rule-based study recommendations to help users identify and prioritize their academic activities.

---

## 🎯 Problem Statement

Students often use multiple applications or manual methods to manage their academic schedules, assignments, study sessions, and daily activities.

This fragmented approach can make it difficult to:

- Keep track of pending academic tasks.
- Remember important deadlines and events.
- Maintain a consistent study routine.
- Allocate sufficient time to different subjects.
- Monitor daily productivity.
- Balance study sessions with regular breaks.

There is a need for an integrated platform that combines essential academic planning and productivity management features.

**DYNAMIC 2.0 addresses this problem by providing a centralized study management environment with task organization, calendar scheduling, focused study sessions, and personalized recommendations.**

---

## 💡 Project Objectives

The primary objectives of DYNAMIC 2.0 are:

1. To develop a centralized platform for managing academic activities.
2. To simplify task creation, organization, and tracking.
3. To provide calendar-based scheduling for important events.
4. To encourage focused study habits through a dedicated Focus Zone.
5. To implement a Pomodoro-based study and break timer.
6. To provide personalized study suggestions using application data and predefined rules.
7. To maintain user information and application records using a MySQL database.
8. To provide a responsive and user-friendly interface.
9. To implement secure authentication and session management.
10. To create a modular web application that can be extended with additional productivity features.

---

## ✨ Key Features

### 1. 🔐 User Authentication

A user authentication system that provides individual access to the application.

Features include:
- User registration.
- User login and logout.
- Password hashing using Bcrypt.
- Session-based authentication.
- User-specific application access.
  
<img width="1255" height="751" alt="image" src="https://github.com/user-attachments/assets/144a00ca-94bc-4bf5-b83e-b9775969ad38" />

---
<img width="1802" height="911" alt="image" src="https://github.com/user-attachments/assets/ca6f10b5-9c22-4224-babf-2ce3c4349197" />


### 2. 📊 Smart Dashboard

The dashboard provides a centralized overview of the user's study and productivity activities.

It helps users access important application sections and view relevant information without navigating through multiple pages.

Key capabilities:
- Overview of study activities.
- Task-related information.
- Quick navigation to application modules.
- Access to productivity and planning features.

### 3. ✅ Task Management

The task management module helps users organize and monitor their academic responsibilities.

Users can use this section to:
- Create new tasks.
- Maintain task details.
- Organize academic activities.
- Track task progress.
- Manage pending responsibilities.

This module supports better planning and helps users maintain visibility over their work.

### 4. 📅 Calendar Management

The calendar module provides a structured way to organize important dates and academic activities.

Features include:
- Calendar-based event management.
- Adding scheduled events.
- Maintaining event titles and dates.
- Categorizing calendar activities.
- Viewing scheduled activities.

### 5. 🧠 Focus Zone

The Focus Zone provides a dedicated workspace for focused study sessions.

It is designed to encourage students to concentrate on specific academic activities while maintaining a structured study routine.

### 6. ⏱️ Pomodoro Timer

The application includes a Pomodoro-based timer interface to support time-managed study sessions.

The concept involves dividing study time into focused work intervals separated by breaks.

Benefits:
- Encourages structured study sessions.
- Helps maintain concentration.
- Promotes regular breaks.
- Supports better time management.

### 7. 💡 Smart Study Recommendations

DYNAMIC 2.0 includes a personalized study recommendation module.

The recommendation system uses predefined rules and available application information to generate relevant study suggestions.

It is designed to help users:
- Identify activities that need attention.
- Prioritize pending tasks.
- Improve study planning.
- Maintain a more organized academic routine.

**Note:** Recommendations are generated through rule-based application logic and are not presented as predictions from a trained machine learning model.

### 8. 📈 Productivity Management

The application brings together study planning and activity management features to help users maintain a more structured workflow.

It provides a foundation for monitoring academic activities and improving personal productivity.

---

## 🛠️ Technology Stack

The project uses the following technologies:

| Layer | Technologies |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| UI Framework | Bootstrap |
| Backend | Python |
| Web Framework | Flask |
| Database | MySQL |
| Database Connectivity | Flask-MySQLdb |
| Password Security | Bcrypt |
| Development Environment | Visual Studio Code |
| Local Server | XAMPP |
| Version Control | Git and GitHub |

### Technology Overview

**Python:** Used for application logic, backend processing, and implementation of productivity-related functionality.

**Flask:** A lightweight Python web framework used to manage application routes, requests, sessions, and backend functionality.

**MySQL:** Used for persistent storage of user information and application records.

**HTML, CSS and JavaScript:** Used to build the application's user interface and client-side interactions.

**Bootstrap:** Used to create a consistent and responsive interface.

**Bcrypt:** Used for password hashing to improve authentication security.

---

## 🏗️ System Architecture

DYNAMIC 2.0 follows a client-server architecture.

The frontend communicates with the Flask backend through HTTP requests. The backend processes user actions, executes application logic, interacts with the MySQL database, and returns the appropriate response.

### Architecture Flow

```text
          USER
           |
           v
    WEB INTERFACE
  HTML / CSS / JS
     Bootstrap
           |
           v
     FLASK BACKEND
   Python Application
           |
     +-----+------+
     |            |
     v            v
 APPLICATION    AUTHENTICATION
   MODULES         LOGIC
     |            |
     +------+-----+
            |
            v
      MYSQL DATABASE
            |
            v
     APPLICATION RESPONSE
            |
            v
       USER INTERFACE
```

### Main Application Layers

1. **Presentation Layer:** Displays pages, forms, dashboards, and interactive elements.
2. **Application Layer:** Handles business logic, authentication, task operations, scheduling, and recommendations.
3. **Data Layer:** Stores and retrieves application information through MySQL.

---

## 🗂️ Main Application Modules

| Module | Purpose |
|---|---|
| Authentication | Registration, login and session handling |
| Dashboard | Centralized productivity overview |
| Task Management | Academic task organization |
| Calendar | Event scheduling and management |
| Focus Zone | Dedicated study workspace |
| Pomodoro Timer | Structured study and break intervals |
| Recommendations | Rule-based personalized study suggestions |
| Database | Persistent application data storage |

---

## 🗄️ Database Management

DYNAMIC 2.0 uses **MySQL** as its relational database management system.

The database maintains application records and supports communication between the backend and persistent storage.

Database responsibilities include:

- Maintaining user account information.
- Storing task-related records.
- Managing scheduled calendar events.
- Maintaining application-specific activity information.
- Supporting data retrieval and updates.

The project includes a database schema file for setting up the required database structure.

**Database:** `dynamic2_db`

**Database Server:** MySQL (XAMPP)

---

## ⚙️ Installation and Setup

Follow these instructions to run DYNAMIC 2.0 on your local machine.

### Prerequisites

Make sure the following software is installed:

- Python 3.x
- MySQL Server
- XAMPP
- Visual Studio Code or another Python IDE
- Git (optional)

### Step 1: Clone the Repository

Open a terminal and execute:

```bash
git clone https://github.com/malavikamanoj640-tech/dynamic-2.0-flask-mysql.git
```

### Step 2: Navigate to the Project Directory

```bash
cd dynamic-2.0-flask-mysql
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Start XAMPP

1. Open the XAMPP Control Panel.
2. Start Apache.
3. Start MySQL.
4. Open phpMyAdmin in your browser.

### Step 6: Create and Import the Database

1. Open phpMyAdmin.
2. Create the database named `dynamic2_db`, if it does not already exist.
3. Select the database.
4. Open the Import section.
5. Select the project's `schema.sql` file.
6. Execute the import.

If the project schema already creates the database, follow the instructions in that file instead of creating it separately.

### Step 7: Configure Environment Variables

Refer to `.env.example` for the available configuration variables.

Configure the database connection details:

```text
DYNAMIC_MYSQL_HOST=localhost
DYNAMIC_MYSQL_USER=root
DYNAMIC_MYSQL_PASSWORD=
DYNAMIC_MYSQL_DB=dynamic2_db
DYNAMIC_MYSQL_PORT=3306
DYNAMIC_SECRET_KEY=your-own-secret-key
DYNAMIC_DEBUG=false
```

Replace the example secret key with a strong, randomly generated value.

Do not upload real credentials or secret keys to GitHub.

### Step 8: Run the Application

Execute:

```bash
python app.py
```

### Step 9: Open the Application

Visit the following address in your browser:

```text
http://127.0.0.1:5000/
```

Register an account and explore the available application modules.

---

## 📁 Project Structure

The project is organized into backend application files, frontend templates, static resources, and configuration files.

```text
DYNAMIC_2_0/
│
├── app.py
├── config.py
├── config.example.py
├── requirements.txt
├── schema.sql
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── calendar.html
│   ├── recommendations.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── screenshots/
│   └── README.md
│
├── .env.example
├── .gitignore
├── LICENSE
├── SECURITY.md
└── README.md
```

### Important Files

| File | Description |
|---|---|
| `app.py` | Main Flask application |
| `config.py` | Application configuration |
| `config.example.py` | Example configuration reference |
| `requirements.txt` | Python dependencies |
| `schema.sql` | Database schema |
| `.env.example` | Environment configuration template |
| `SECURITY.md` | Security-related information |
| `README.md` | Project documentation |

---

## 🔒 Security Implementation

Security is an important consideration in DYNAMIC 2.0.

The application incorporates the following measures:

- **Password Hashing:** Bcrypt is used for password hashing.
- **Session Management:** Session-based authentication is used to manage logged-in users.
- **CSRF Protection:** Protection is implemented for state-changing requests.
- **Environment-Based Configuration:** Sensitive configuration values can be supplied through environment variables.
- **Debug Configuration:** Debug mode is disabled by default.
- **Git Protection:** Local environment and sensitive configuration files are excluded through `.gitignore`.

For additional information, refer to `SECURITY.md`.

---

## 🧪 Testing and Validation

The project should be validated across its major application workflows.

Suggested manual testing areas:

| Test Area | Validation |
|---|---|
| Registration | Verify new account creation |
| Login | Verify valid and invalid login attempts |
| Logout | Verify session termination |
| Dashboard | Verify authenticated dashboard access |
| Task Management | Verify task creation and updates |
| Calendar | Verify event creation and display |
| Focus Zone | Verify study workspace functionality |
| Pomodoro Timer | Verify timer interactions |
| Recommendations | Verify rule-based suggestion output |
| Database | Verify data persistence |

Testing should be performed using the local MySQL environment after completing the installation steps.

---

## 🌟 Benefits of the Project

- Centralized academic activity management.
- Better organization of daily study tasks.
- Convenient scheduling of important events.
- Structured study sessions through the Focus Zone.
- Improved time management using the Pomodoro technique.
- Personalized study suggestions.
- Persistent storage using a relational database.
- Modular architecture that supports future enhancements.

---

## 🔮 Future Scope

DYNAMIC 2.0 provides a foundation for additional academic productivity features.

Possible future enhancements include:

1. Advanced productivity analytics and graphical reports.
2. Weekly and monthly study progress summaries.
3. Enhanced subject-wise study planning.
4. Deadline reminders and notifications.
5. Calendar synchronization.
6. More customizable Pomodoro sessions.
7. Additional recommendation rules.
8. Improved mobile and tablet experience.
9. Exportable productivity reports.
10. Additional dashboard customization.

---

## 🎓 Academic Relevance

DYNAMIC 2.0 demonstrates the practical application of several concepts from computer science and software development.

The project incorporates:

- Python programming.
- Web application development.
- Flask framework.
- Client-server architecture.
- Relational database management.
- SQL queries and database connectivity.
- Authentication and session management.
- Frontend development.
- CRUD operations.
- Application security practices.

It provides practical experience in designing, developing, and organizing a database-driven web application.

---

## 👩‍💻 Developer

**Malavika Manoj**

Master of Computer Applications (MCA)

**Areas of Interest:**
- Python Development
- Software Development
- Web Application Development
- Database Management
- Data Science and Machine Learning

---

## 📜 License

This project is licensed under the MIT License.


---

## ⭐ Support

If you find this project interesting or useful, consider giving this repository a ⭐.

Your feedback and suggestions are welcome!

---

<p align="center">
  <strong>DYNAMIC 2.0</strong><br>
  Plan Better. Focus Better. Achieve More.
</p>
