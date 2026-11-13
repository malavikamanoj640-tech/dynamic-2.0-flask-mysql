from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response, abort
from flask_mysqldb import MySQL
import MySQLdb
import bcrypt, os, csv, io
from functools import wraps
from datetime import date, datetime, timedelta
from collections import defaultdict
import secrets
import hmac


app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


@app.context_processor
def inject_csrf_token():
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return {'csrf_token': token}


@app.before_request
def csrf_protect():
    if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
        expected = session.get('_csrf_token')
        supplied = request.form.get('_csrf_token') or request.headers.get('X-CSRFToken')
        if not expected or not supplied or not hmac.compare_digest(expected, supplied):
            abort(400, description='The form security token is missing or invalid. Refresh the page and try again.')



def initialize_database():
    """Create the configured database and safely add any missing DYNAMIC tables/columns."""
    db_name = app.config.get('MYSQL_DB', 'dynamic2_db')
    host = app.config.get('MYSQL_HOST', 'localhost')
    user = app.config.get('MYSQL_USER', 'root')
    password = app.config.get('MYSQL_PASSWORD', '')
    port = int(app.config.get('MYSQL_PORT', 3306))
    conn = None
    try:
        # Connect to the MySQL server WITHOUT selecting a database so a fresh install works.
        conn = MySQLdb.connect(host=host, user=user, passwd=password, port=port, charset='utf8mb4')
        cur = conn.cursor()
        safe_db_name = db_name.replace('`', '``')
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{safe_db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cur.execute(f"USE `{safe_db_name}`")

        table_statements = [
            """CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS user_roles (
                user_id INT PRIMARY KEY,
                role ENUM('student','admin') NOT NULL DEFAULT 'student',
                CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, title VARCHAR(180) NOT NULL,
                priority ENUM('Low','Medium','High') DEFAULT 'Medium', due_date DATE NULL,
                status ENUM('Pending','Completed') DEFAULT 'Pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, title VARCHAR(180) NOT NULL,
                content TEXT NOT NULL, category VARCHAR(50) DEFAULT 'General', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_notes_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS study_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, subject VARCHAR(100) DEFAULT 'General Study',
                minutes INT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_study_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, score INT NOT NULL, total INT NOT NULL,
                subject VARCHAR(100) NOT NULL DEFAULT 'General', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_quiz_attempts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS calendar_events (
                id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, title VARCHAR(180) NOT NULL,
                event_date DATE NOT NULL, category VARCHAR(50) NOT NULL DEFAULT 'Other',
                CONSTRAINT fk_calendar_events_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS study_goals (
                id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, title VARCHAR(180) NOT NULL,
                target_minutes INT NOT NULL DEFAULT 300, start_date DATE NOT NULL, end_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_study_goals_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS user_activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, action VARCHAR(80) NOT NULL,
                details VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_activity_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, title VARCHAR(180) NOT NULL,
                description TEXT NOT NULL, category VARCHAR(50) DEFAULT 'General', generated_on DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_recommendations_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",

            """CREATE TABLE IF NOT EXISTS focus_preferences (
    user_id INT PRIMARY KEY,
    daily_goal INT NOT NULL DEFAULT 120,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_focus_preferences_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
        ]
        for statement in table_statements:
            cur.execute(statement)

        # Migrate older DYNAMIC 2.0 databases without dropping or replacing user data.
        migrations = {
            'tasks': {
                'priority': "ALTER TABLE tasks ADD COLUMN priority ENUM('Low','Medium','High') DEFAULT 'Medium'",
                'due_date': 'ALTER TABLE tasks ADD COLUMN due_date DATE NULL',
                'status': "ALTER TABLE tasks ADD COLUMN status ENUM('Pending','Completed') DEFAULT 'Pending'",
                'created_at': 'ALTER TABLE tasks ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            },
            'notes': {
    'category': "ALTER TABLE notes ADD COLUMN category VARCHAR(50) DEFAULT 'General'",
    'created_at': "ALTER TABLE notes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    'tags': "ALTER TABLE notes ADD COLUMN tags VARCHAR(255) DEFAULT NULL",
    'is_pinned': "ALTER TABLE notes ADD COLUMN is_pinned TINYINT(1) NOT NULL DEFAULT 0",
    'is_favourite': "ALTER TABLE notes ADD COLUMN is_favourite TINYINT(1) NOT NULL DEFAULT 0",
    'is_archived': "ALTER TABLE notes ADD COLUMN is_archived TINYINT(1) NOT NULL DEFAULT 0",
    'updated_at': "ALTER TABLE notes ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    'last_reviewed': "ALTER TABLE notes ADD COLUMN last_reviewed DATETIME NULL",
    'review_count': "ALTER TABLE notes ADD COLUMN review_count INT NOT NULL DEFAULT 0"
},
            'study_sessions': {
                'subject': "ALTER TABLE study_sessions ADD COLUMN subject VARCHAR(100) DEFAULT 'General Study'",
                'created_at': 'ALTER TABLE study_sessions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            },
            'quiz_attempts': {
                'subject': "ALTER TABLE quiz_attempts ADD COLUMN subject VARCHAR(100) NOT NULL DEFAULT 'General'",
                'created_at': 'ALTER TABLE quiz_attempts ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            },
            'calendar_events': {
                'category': "ALTER TABLE calendar_events ADD COLUMN category VARCHAR(50) NOT NULL DEFAULT 'Other'",
            },
            'user_activity_logs': {
                'action': "ALTER TABLE user_activity_logs ADD COLUMN action VARCHAR(80) NOT NULL DEFAULT 'Activity'",
                'details': 'ALTER TABLE user_activity_logs ADD COLUMN details VARCHAR(255) NULL',
                'created_at': 'ALTER TABLE user_activity_logs ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            },
        }
        for table, columns in migrations.items():
            for column, alter_sql in columns.items():
                cur.execute("""SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                               WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s""",
                            (db_name, table, column))
                if cur.fetchone()[0] == 0:
                    cur.execute(alter_sql)

        # Existing accounts receive the student role; existing admin roles remain unchanged.
        cur.execute("INSERT IGNORE INTO user_roles(user_id, role) SELECT id, 'student' FROM users")
        conn.commit()
        cur.close()
        print(f"[DYNAMIC] Database '{db_name}' is ready.")
    except Exception as exc:
        if conn:
            conn.rollback()
        raise RuntimeError(
            f"Could not initialise MySQL database '{db_name}'. Start MySQL in XAMPP and verify MYSQL_HOST, MYSQL_USER and MYSQL_PASSWORD in config.py. Details: {exc}"
        ) from exc
    finally:
        if conn:
            conn.close()


# Automatic setup runs before Flask-MySQLdb opens application connections.
initialize_database()
mysql = MySQL(app)


def db_execute(query, args=(), fetch='none'):
    cur = mysql.connection.cursor()
    cur.execute(query, args)
    result = cur.fetchall() if fetch == 'all' else (cur.fetchone() if fetch == 'one' else None)
    mysql.connection.commit()
    cur.close()
    return result


def rows(query, args=()):
    return db_execute(query, args, 'all')


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        role = db_execute('SELECT role FROM user_roles WHERE user_id=%s', (session['user_id'],), 'one')
        if not role or role[0] != 'admin':
            flash('Administrator access is required.', 'danger')
            return redirect(url_for('dashboard'))
        return fn(*args, **kwargs)
    return wrapper


def log_activity(action, details=''):
    db_execute('INSERT INTO user_activity_logs(user_id, action, details) VALUES(%s,%s,%s)',
               (session['user_id'], action[:80], details[:255]))


def build_recommendations(uid):
    task_total, task_done, overdue = db_execute(
        "SELECT COUNT(*), COALESCE(SUM(status='Completed'),0), COALESCE(SUM(status!='Completed' AND due_date<CURDATE()),0) FROM tasks WHERE user_id=%s", (uid,), 'one')
    avg_score = db_execute('SELECT COALESCE(AVG(score/total*100),0) FROM quiz_attempts WHERE user_id=%s AND total>0', (uid,), 'one')[0]
    subject_scores = rows('SELECT subject, ROUND(AVG(score/total*100),1) avg_score, COUNT(*) attempts FROM quiz_attempts WHERE user_id=%s AND total>0 GROUP BY subject ORDER BY avg_score ASC', (uid,))
    weekly_minutes = db_execute('SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE user_id=%s AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)', (uid,), 'one')[0]
    recs = []
    if overdue:
        recs.append(('Prioritise overdue work', f'You have {overdue} overdue task(s). Review their deadlines and complete the most important one first.', 'Tasks'))
    if subject_scores and float(subject_scores[0][1]) < 70:
        s = subject_scores[0]
        recs.append((f'Revise {s[0]}', f'Your average quiz score in {s[0]} is {s[1]}%. Spend a focused session revising its fundamentals and attempt another quiz.', 'Learning'))
    if weekly_minutes < 300:
        recs.append(('Build a consistent study routine', f'You recorded {weekly_minutes} study minutes in the last 7 days. Try scheduling one or two focused sessions each day.', 'Focus'))
    if task_total and task_done / task_total >= .8:
        recs.append(('Set a new learning goal', 'You have completed most of your recorded tasks. Add a new weekly goal to maintain momentum.', 'Goals'))
    if not recs:
        recs.append(('Keep your learning balanced', 'Continue tracking study sessions, completing tasks and attempting quizzes. Your workspace will use this activity to tailor future suggestions.', 'General'))
    db_execute('DELETE FROM recommendations WHERE user_id=%s AND generated_on=CURDATE()', (uid,))
    for title, body, category in recs:
        db_execute('INSERT INTO recommendations(user_id,title,description,category,generated_on) VALUES(%s,%s,%s,%s,CURDATE())', (uid, title, body, category))
    return recs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if len(name) < 2 or '@' not in email or len(password) < 8:
            flash('Enter a valid name and email. Password must contain at least 8 characters.', 'danger')
            return render_template('register.html')
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            db_execute('INSERT INTO users(fullname,email,password) VALUES(%s,%s,%s)', (name, email, hashed))
            uid = db_execute('SELECT id FROM users WHERE email=%s', (email,), 'one')[0]
            db_execute("INSERT INTO user_roles(user_id,role) VALUES(%s,'student')", (uid,))
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('That email may already be registered, or the database is unavailable.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = db_execute('SELECT id,fullname,password FROM users WHERE email=%s', (email,), 'one')
        if user and bcrypt.checkpw(request.form.get('password', '').encode(), user[2].encode()):
            session.clear(); session['user_id'] = user[0]; session['fullname'] = user[1]
            role = db_execute('SELECT role FROM user_roles WHERE user_id=%s', (user[0],), 'one')
            session['role'] = role[0] if role else 'student'
            log_activity('Login', 'User signed in')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    total, done, overdue = db_execute("SELECT COUNT(*),COALESCE(SUM(status='Completed'),0),COALESCE(SUM(status!='Completed' AND due_date<CURDATE()),0) FROM tasks WHERE user_id=%s", (uid,), 'one')
    focus = db_execute('SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE user_id=%s AND YEARWEEK(created_at,1)=YEARWEEK(CURDATE(),1)', (uid,), 'one')[0]
    quiz = db_execute('SELECT COALESCE(ROUND(AVG(score/total*100)),0) FROM quiz_attempts WHERE user_id=%s AND total>0', (uid,), 'one')[0]
    note_count = db_execute('SELECT COUNT(*) FROM notes WHERE user_id=%s', (uid,), 'one')[0]
    recent = rows('SELECT id,title,priority,due_date,status FROM tasks WHERE user_id=%s ORDER BY (status="Completed"),due_date IS NULL,due_date LIMIT 6', (uid,))
    upcoming = rows('SELECT title,event_date FROM calendar_events WHERE user_id=%s AND event_date>=CURDATE() ORDER BY event_date LIMIT 4', (uid,))
    daily = rows('SELECT DATE(created_at),SUM(minutes) FROM study_sessions WHERE user_id=%s AND created_at>=DATE_SUB(CURDATE(),INTERVAL 6 DAY) GROUP BY DATE(created_at)', (uid,))
    daily = [(r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0]), int(r[1])) for r in daily]
    recommendations = build_recommendations(uid)
    pct = round(done / total * 100) if total else 0
    return render_template('dashboard.html', task_count=total, done=done, overdue=overdue, focus=focus, quiz=quiz,
                           note_count=note_count, recent=recent, upcoming=upcoming, daily=daily, completion=pct, recommendations=recommendations[:2])


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    uid = session['user_id']

    # CREATE TASK
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        due = request.form.get('due_date') or None
        priority = request.form.get('priority', 'Medium')

        if not title:
            flash('Please enter a task title.', 'warning')
            return redirect(url_for('tasks'))

        if len(title) > 180:
            flash('Task title cannot exceed 180 characters.', 'warning')
            return redirect(url_for('tasks'))

        if priority not in ('Low', 'Medium', 'High'):
            priority = 'Medium'

        db_execute(
            '''
            INSERT INTO tasks(user_id, title, priority, due_date)
            VALUES(%s, %s, %s, %s)
            ''',
            (uid, title, priority, due)
        )

        log_activity('Task created', title)
        flash('Task added successfully.', 'success')

        return redirect(url_for('tasks'))

    # SEARCH AND FILTER TASKS (GET REQUEST)
    search = request.args.get('q', '').strip()
    status = request.args.get('status', 'All')
    priority = request.args.get('priority', 'All')

    if status not in ('All', 'Pending', 'Completed'):
        status = 'All'

    if priority not in ('All', 'High', 'Medium', 'Low'):
        priority = 'All'

    sql = '''
        SELECT id, title, priority, due_date, status
        FROM tasks
        WHERE user_id = %s
    '''

    params = [uid]

    if search:
        sql += ' AND title LIKE %s'
        params.append('%' + search + '%')

    if status in ('Pending', 'Completed'):
        sql += ' AND status = %s'
        params.append(status)

    if priority in ('High', 'Medium', 'Low'):
        sql += ' AND priority = %s'
        params.append(priority)

    sql += '''
        ORDER BY
        CASE WHEN status = 'Pending' THEN 0 ELSE 1 END,
        CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            ELSE 3
        END,
        due_date IS NULL,
        due_date ASC
    '''

    task_rows = rows(sql, tuple(params))

    return render_template(
        'tasks.html',
        tasks=task_rows,
        search=search,
        status=status,
        priority=priority
    )


@app.post('/tasks/<int:i>/toggle')
@login_required
def task_toggle(i):
    db_execute('UPDATE tasks SET status=IF(status="Pending","Completed","Pending") WHERE id=%s AND user_id=%s', (i,session['user_id']))
    log_activity('Task status changed', f'Task #{i}')
    return redirect(request.referrer or url_for('tasks'))

@app.post('/tasks/<int:i>/delete')
@login_required
def task_delete(i):
    db_execute('DELETE FROM tasks WHERE id=%s AND user_id=%s', (i,session['user_id']))
    log_activity('Task deleted', f'Task #{i}')
    return redirect(url_for('tasks'))

# ============================
# SMART KNOWLEDGE WORKSPACE
# ============================

# ============================================================
# SMART KNOWLEDGE WORKSPACE
# ============================================================

NOTE_CATEGORIES = [
    'General',
    'Programming',
    'Revision',
    'Idea',
    'Project'
]


def clean_note_tags(raw_tags):
    """Remove empty and duplicate tags; keep tags lowercase."""
    tags = [
        tag.strip().lower()
        for tag in (raw_tags or '').split(',')
        if tag.strip()
    ]

    # Preserve order while removing duplicates.
    return ', '.join(dict.fromkeys(tags))[:255]


@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():

    uid = session['user_id']

    # --------------------------------------------------------
    # CREATE NOTE
    # --------------------------------------------------------
    if request.method == 'POST':

        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'General')
        tags = clean_note_tags(request.form.get('tags', ''))

        if category not in NOTE_CATEGORIES:
            category = 'General'

        if not title or not content:
            flash('Please enter both title and content.', 'warning')
            return redirect(url_for('notes'))

        if len(title) > 180:
            flash('Title cannot exceed 180 characters.', 'warning')
            return redirect(url_for('notes'))

        if len(content) > 20000:
            flash('Note content cannot exceed 20,000 characters.', 'warning')
            return redirect(url_for('notes'))

        db_execute(
            """
            INSERT INTO notes
            (user_id, title, content, category, tags)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (uid, title, content, category, tags)
        )

        log_activity('Note created', title)
        flash('Your knowledge note has been saved.', 'success')

        return redirect(url_for('notes'))

    # --------------------------------------------------------
    # SEARCH AND FILTER
    # --------------------------------------------------------
    search = request.args.get('q', '').strip()
    category = request.args.get('category', 'All')
    view = request.args.get('view', 'All')
    sort = request.args.get('sort', 'newest')

    if category not in ['All'] + NOTE_CATEGORIES:
        category = 'All'

    if view not in ['All', 'Pinned', 'Favourites', 'Archived', 'Recent']:
        view = 'All'

    if sort not in ['newest', 'oldest', 'alphabetical']:
        sort = 'newest'

    sql = """
        SELECT
            id,
            title,
            content,
            category,
            created_at,
            updated_at,
            tags,
            is_pinned,
            is_favourite,
            is_archived,
            last_reviewed,
            review_count
        FROM notes
        WHERE user_id=%s
    """

    args = [uid]

    # Archived and active notes are displayed separately.
    if view == 'Archived':
        sql += ' AND is_archived=1'
    else:
        sql += ' AND is_archived=0'

    if view == 'Pinned':
        sql += ' AND is_pinned=1'

    elif view == 'Favourites':
        sql += ' AND is_favourite=1'

    elif view == 'Recent':
        sql += ' AND updated_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)'

    if category != 'All':
        sql += ' AND category=%s'
        args.append(category)

    if search:
        sql += """
            AND (
                title LIKE %s
                OR content LIKE %s
                OR tags LIKE %s
            )
        """

        keyword = '%' + search + '%'
        args.extend([keyword, keyword, keyword])

    # Sorting
    if sort == 'oldest':
        sql += ' ORDER BY created_at ASC, id ASC'

    elif sort == 'alphabetical':
        sql += ' ORDER BY title ASC'

    else:
        sql += ' ORDER BY is_pinned DESC, updated_at DESC, id DESC'

    note_rows = rows(sql, tuple(args))

    # --------------------------------------------------------
    # DASHBOARD STATISTICS
    # --------------------------------------------------------
    stats = db_execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(is_pinned), 0),
            COALESCE(SUM(is_favourite), 0),
            COALESCE(SUM(review_count), 0),
            COALESCE(SUM(is_archived), 0)
        FROM notes
        WHERE user_id=%s AND is_archived=0
        """,
        (uid,),
        'one'
    )

    category_stats = rows(
        """
        SELECT category, COUNT(*)
        FROM notes
        WHERE user_id=%s AND is_archived=0
        GROUP BY category
        ORDER BY COUNT(*) DESC
        """,
        (uid,)
    )

    return render_template(
        'notes.html',
        notes=note_rows,
        search=search,
        category=category,
        view=view,
        sort=sort,
        stats=stats,
        category_stats=category_stats,
        categories=NOTE_CATEGORIES
    )


# ------------------------------------------------------------
# EDIT NOTE
# ------------------------------------------------------------
@app.route('/notes/<int:i>/edit', methods=['POST'])
@login_required
def note_edit(i):

    uid = session['user_id']

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    category = request.form.get('category', 'General')
    tags = clean_note_tags(request.form.get('tags', ''))

    if category not in NOTE_CATEGORIES:
        category = 'General'

    if not title or not content:
        flash('Title and content are required.', 'warning')
        return redirect(url_for('notes'))

    if len(title) > 180 or len(content) > 20000:
        flash('Please check the title and content length.', 'warning')
        return redirect(url_for('notes'))

    db_execute(
        """
        UPDATE notes
        SET
            title=%s,
            content=%s,
            category=%s,
            tags=%s,
            updated_at=NOW()
        WHERE id=%s AND user_id=%s
        """,
        (title, content, category, tags, i, uid)
    )

    log_activity('Note updated', title)
    flash('Note updated successfully.', 'success')

    return redirect(url_for('notes'))


# ------------------------------------------------------------
# PIN / FAVOURITE / ARCHIVE
# ------------------------------------------------------------
@app.post('/notes/<int:i>/<action>')
@login_required
def note_action(i, action):

    uid = session['user_id']

    allowed_actions = {
        'pin': 'is_pinned',
        'favourite': 'is_favourite',
        'archive': 'is_archived'
    }

    column = allowed_actions.get(action)

    if not column:
        flash('Invalid note action.', 'danger')
        return redirect(url_for('notes'))

    # The column name is selected only from the fixed allowlist.
    db_execute(
        f"""
        UPDATE notes
        SET {column}=1-{column},
            updated_at=NOW()
        WHERE id=%s AND user_id=%s
        """,
        (i, uid)
    )

    messages = {
        'pin': 'Pin status updated.',
        'favourite': 'Favourite status updated.',
        'archive': 'Archive status updated.'
    }

    flash(messages[action], 'success')

    return redirect(request.referrer or url_for('notes'))


# ------------------------------------------------------------
# REVISION TRACKING
# ------------------------------------------------------------
@app.post('/notes/<int:i>/review')
@login_required
def note_review(i):

    uid = session['user_id']

    db_execute(
        """
        UPDATE notes
        SET
            last_reviewed=NOW(),
            review_count=review_count+1
        WHERE id=%s AND user_id=%s
        """,
        (i, uid)
    )

    log_activity('Note reviewed', f'Note #{i}')

    flash('Revision activity recorded.', 'success')

    return redirect(url_for('notes'))


# ------------------------------------------------------------
# DELETE NOTE
# ------------------------------------------------------------
@app.post('/notes/<int:i>/delete')
@login_required
def note_delete(i):

    uid = session['user_id']

    db_execute(
        """
        DELETE FROM notes
        WHERE id=%s AND user_id=%s
        """,
        (i, uid)
    )

    log_activity('Note deleted', f'Note #{i}')

    flash('Note deleted successfully.', 'success')

    return redirect(url_for('notes'))


@app.route('/focus')
@login_required
def focus():

    uid = session['user_id']

    # Ensure the user has a saved preference
    db_execute(
        """
        INSERT IGNORE INTO focus_preferences(user_id, daily_goal)
        VALUES(%s, 120)
        """,
        (uid,)
    )

    daily_goal = db_execute(
        """
        SELECT daily_goal
        FROM focus_preferences
        WHERE user_id=%s
        """,
        (uid,),
        'one'
    )[0]

    # Today's focus statistics
    today_minutes, today_sessions = db_execute(
        """
        SELECT
            COALESCE(SUM(minutes), 0),
            COUNT(*)
        FROM study_sessions
        WHERE user_id=%s
        AND DATE(created_at)=CURDATE()
        """,
        (uid,),
        'one'
    )

    # Last 7 days: daily focus minutes
    daily_rows = rows(
        """
        SELECT DATE(created_at), SUM(minutes)
        FROM study_sessions
        WHERE user_id=%s
        AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY DATE(created_at)
        """,
        (uid,)
    )

    daily_map = {
        str(r[0]): int(r[1])
        for r in daily_rows
    }

    weekly_data = []

    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)

        weekly_data.append({
            'day': day.strftime('%a'),
            'date': day.isoformat(),
            'minutes': daily_map.get(day.isoformat(), 0)
        })

    weekly_minutes = sum(
        item['minutes'] for item in weekly_data
    )

    # Subject-wise focus time for the last 7 days
    subject_rows = rows(
        """
        SELECT subject, SUM(minutes)
        FROM study_sessions
        WHERE user_id=%s
        AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY subject
        ORDER BY SUM(minutes) DESC
        LIMIT 6
        """,
        (uid,)
    )

    subject_data = [
        {
            'subject': str(r[0] or 'General Study'),
            'minutes': int(r[1])
        }
        for r in subject_rows
    ]

    # Calculate the current consecutive-day focus streak.
    # If today has no session, yesterday can still continue the streak.
    focus_dates = rows(
        """
        SELECT DISTINCT DATE(created_at)
        FROM study_sessions
        WHERE user_id=%s
        AND created_at >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
        ORDER BY DATE(created_at) DESC
        """,
        (uid,)
    )

    completed_dates = {
        r[0] for r in focus_dates
    }

    streak = 0
    check_date = date.today()

    if check_date not in completed_dates:
        check_date -= timedelta(days=1)

    while check_date in completed_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return render_template(
        'focus.html',
        today_minutes=int(today_minutes),
        today_sessions=int(today_sessions),
        daily_goal=int(daily_goal),
        weekly_minutes=int(weekly_minutes),
        weekly_data=weekly_data,
        subject_data=subject_data,
        streak=streak
    )


@app.post('/focus/goal')
@login_required
def save_focus_goal():

    data = request.get_json(silent=True) or {}

    try:
        goal = int(data.get('daily_goal', 120))
    except (ValueError, TypeError):
        return jsonify(
            ok=False,
            error='Please enter a valid daily goal.'
        ), 400

    if goal < 1 or goal > 1440:
        return jsonify(
            ok=False,
            error='Daily goal must be between 1 and 1440 minutes.'
        ), 400

    db_execute(
        """
        INSERT INTO focus_preferences(user_id, daily_goal)
        VALUES(%s, %s)
        ON DUPLICATE KEY UPDATE daily_goal=VALUES(daily_goal)
        """,
        (session['user_id'], goal)
    )

    return jsonify(
        ok=True,
        daily_goal=goal
    )



@app.post('/focus/save')
@login_required
def save_focus():
    data=request.get_json(silent=True) or {}
    try: mins=max(1,min(240,int(data.get('minutes',25))))
    except (ValueError,TypeError): return jsonify(ok=False,error='Invalid duration'),400
    subject=(data.get('subject') or 'General Study')[:100]
    db_execute('INSERT INTO study_sessions(user_id,subject,minutes) VALUES(%s,%s,%s)',(session['user_id'],subject,mins))
    log_activity('Focus session completed',f'{subject}: {mins} minutes')
    return jsonify(ok=True)

@app.route('/quiz')
@login_required
def quiz(): return render_template('quiz.html')

@app.post('/quiz/save')
@login_required
def save_quiz():
    d=request.get_json(silent=True) or {}
    try: score=int(d['score']); total=int(d['total'])
    except (KeyError,ValueError,TypeError): return jsonify(ok=False,error='Invalid quiz result'),400
    if total<1 or score<0 or score>total: return jsonify(ok=False,error='Invalid score'),400
    subject=(d.get('subject') or 'General').strip()[:100]
    db_execute('INSERT INTO quiz_attempts(user_id,score,total,subject) VALUES(%s,%s,%s,%s)',(session['user_id'],score,total,subject))
    log_activity('Quiz completed',f'{subject}: {score}/{total}')
    return jsonify(ok=True)

@app.route('/coding')
@login_required
def coding(): return render_template('coding.html')

@app.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    uid = session['user_id']
    allowed_categories = {'Study', 'Exam', 'Assignment', 'Personal', 'Other'}

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        event_date = request.form.get('event_date', '').strip()
        category = request.form.get('category', 'Other').strip()

        if not title or not event_date:
            flash('Please enter an event title and date.', 'warning')
            return redirect(url_for('calendar'))

        if len(title) > 180:
            flash('Event title cannot exceed 180 characters.', 'warning')
            return redirect(url_for('calendar'))

        if category not in allowed_categories:
            category = 'Other'

        try:
            datetime.strptime(event_date, '%Y-%m-%d')
        except ValueError:
            flash('Please choose a valid event date.', 'warning')
            return redirect(url_for('calendar'))

        db_execute(
            'INSERT INTO calendar_events(user_id, title, event_date, category) VALUES(%s, %s, %s, %s)',
            (uid, title, event_date, category)
        )
        log_activity('Planner event created', title)
        flash('Event added to your planner.', 'success')
        return redirect(url_for('calendar'))

    events = rows(
        """SELECT id, title, event_date, category
           FROM calendar_events
           WHERE user_id=%s
           ORDER BY event_date ASC""",
        (uid,)
    )
    return render_template('calendar.html', events=events)


@app.route('/calendar/delete/<int:i>', methods=['POST'])
@login_required
def calendar_delete(i):
    event = db_execute(
        'SELECT id FROM calendar_events WHERE id=%s AND user_id=%s',
        (i, session['user_id']),
        'one'
    )

    if not event:
        flash('Event not found or access denied.', 'warning')
        return redirect(url_for('calendar'))

    db_execute(
        'DELETE FROM calendar_events WHERE id=%s AND user_id=%s',
        (i, session['user_id'])
    )

    flash('Calendar event deleted successfully.', 'success')
    return redirect(url_for('calendar'))


@app.route('/games')
@login_required
def games(): return render_template('games.html')

@app.route('/analytics')
@login_required
def analytics():
    uid=session['user_id']
    sessions=rows('SELECT DATE(created_at),SUM(minutes) FROM study_sessions WHERE user_id=%s AND created_at>=DATE_SUB(CURDATE(),INTERVAL 6 DAY) GROUP BY DATE(created_at)',(uid,))
    sessions=[(r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0]), int(r[1])) for r in sessions]
    attempts=rows('SELECT score,total,created_at,subject FROM quiz_attempts WHERE user_id=%s ORDER BY id DESC LIMIT 10',(uid,))
    subjects=rows('SELECT subject,ROUND(AVG(score/total*100),1),COUNT(*) FROM quiz_attempts WHERE user_id=%s AND total>0 GROUP BY subject ORDER BY 2 DESC',(uid,))
    total_minutes=db_execute('SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE user_id=%s',(uid,),'one')[0]
    return render_template('analytics.html',sessions=sessions,attempts=attempts,subjects=subjects,total_minutes=total_minutes)


@app.route('/recommendations')
@login_required
def recommendations():
    recs = build_recommendations(session['user_id'])
    return render_template('recommendations.html', recommendations=recs)


@app.route('/goals',methods=['GET','POST'])
@login_required
def goals():
    uid=session['user_id']
    if request.method=='POST':
        title=request.form.get('title','').strip(); target=max(1,min(1000,int(request.form.get('target_minutes',300))))
        if title: db_execute('INSERT INTO study_goals(user_id,title,target_minutes,start_date,end_date) VALUES(%s,%s,%s,%s,%s)',(uid,title,target,request.form.get('start_date') or date.today(),request.form.get('end_date') or (date.today()+timedelta(days=7))))
        flash('Study goal created.','success'); return redirect(url_for('goals'))
    goals_rows=rows('SELECT g.id,g.title,g.target_minutes,g.start_date,g.end_date,COALESCE(SUM(s.minutes),0) FROM study_goals g LEFT JOIN study_sessions s ON s.user_id=g.user_id AND DATE(s.created_at) BETWEEN g.start_date AND g.end_date WHERE g.user_id=%s GROUP BY g.id ORDER BY g.id DESC',(uid,))
    return render_template('goals.html',goals=goals_rows)

@app.post('/goals/<int:i>/delete')
@login_required
def goal_delete(i):
    db_execute('DELETE FROM study_goals WHERE id=%s AND user_id=%s',(i,session['user_id']))
    return redirect(url_for('goals'))

@app.route('/reports/export.csv')
@login_required
def export_report():
    uid=session['user_id']; output=io.StringIO(); writer=csv.writer(output)
    writer.writerow(['DYNAMIC 2.0 Learning Activity Report']); writer.writerow(['Generated',datetime.now().strftime('%Y-%m-%d %H:%M')]); writer.writerow([])
    writer.writerow(['Study sessions']); writer.writerow(['Subject','Minutes','Recorded at'])
    for r in rows('SELECT subject,minutes,created_at FROM study_sessions WHERE user_id=%s ORDER BY created_at DESC',(uid,)): writer.writerow(r)
    writer.writerow([]); writer.writerow(['Quiz attempts']); writer.writerow(['Subject','Score','Total','Date'])
    for r in rows('SELECT subject,score,total,created_at FROM quiz_attempts WHERE user_id=%s ORDER BY created_at DESC',(uid,)): writer.writerow(r)
    writer.writerow([]); writer.writerow(['Tasks']); writer.writerow(['Title','Priority','Due date','Status'])
    for r in rows('SELECT title,priority,due_date,status FROM tasks WHERE user_id=%s ORDER BY id DESC',(uid,)): writer.writerow(r)
    response=make_response('\ufeff'+output.getvalue()); response.headers['Content-Type']='text/csv; charset=utf-8'; response.headers['Content-Disposition']='attachment; filename=dynamic_learning_report.csv'; return response

@app.route('/profile')
@login_required
def profile():
    user=db_execute('SELECT fullname,email,created_at FROM users WHERE id=%s',(session['user_id'],),'one')
    activity=rows('SELECT action,details,created_at FROM user_activity_logs WHERE user_id=%s ORDER BY id DESC LIMIT 8',(session['user_id'],))
    return render_template('profile.html',user=user,activity=activity)

@app.route('/admin')
@admin_required
def admin():
    counts=db_execute('SELECT (SELECT COUNT(*) FROM users),(SELECT COUNT(*) FROM tasks),(SELECT COUNT(*) FROM notes),(SELECT COUNT(*) FROM quiz_attempts)',fetch='one')
    users=rows('SELECT u.id,u.fullname,u.email,u.created_at,COALESCE(r.role,"student") FROM users u LEFT JOIN user_roles r ON r.user_id=u.id ORDER BY u.id DESC LIMIT 30')
    return render_template('admin.html',counts=counts,users=users)

@app.post('/admin/user/<int:uid>/role')
@admin_required
def admin_role(uid):
    role=request.form.get('role','student')
    if role not in ('student','admin') or uid==session['user_id']:
        flash('Invalid role change. You cannot change your own role here.','warning')
    else:
        db_execute('INSERT INTO user_roles(user_id,role) VALUES(%s,%s) ON DUPLICATE KEY UPDATE role=VALUES(role)',(uid,role))
        flash('User role updated.','success')
    return redirect(url_for('admin'))

@app.errorhandler(413)
def too_large(_): return 'Request too large (maximum 5 MB).',413

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))
