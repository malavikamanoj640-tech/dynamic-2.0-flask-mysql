-- Run this script in phpMyAdmin for an existing DYNAMIC 2.0 database.
-- It preserves existing users, tasks, notes, study sessions, quiz attempts and events.
USE dynamic2_db;

CREATE TABLE IF NOT EXISTS user_roles (
 user_id INT PRIMARY KEY,
 role ENUM('student','admin') NOT NULL DEFAULT 'student',
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
INSERT IGNORE INTO user_roles(user_id, role) SELECT id, 'student' FROM users;

-- The subject column is needed for subject-wise quiz analytics.
-- If MySQL reports that the column already exists, skip this ALTER statement.
ALTER TABLE quiz_attempts ADD COLUMN subject VARCHAR(100) NOT NULL DEFAULT 'General';

CREATE TABLE IF NOT EXISTS study_goals (
 id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, title VARCHAR(180) NOT NULL,
 target_minutes INT NOT NULL DEFAULT 300, start_date DATE NOT NULL, end_date DATE NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS user_activity_logs (
 id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, action VARCHAR(80) NOT NULL,
 details VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS recommendations (
 id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, title VARCHAR(180) NOT NULL,
 description TEXT NOT NULL, category VARCHAR(50) DEFAULT 'General',
 generated_on DATE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- Older installations: add any missing activity log columns without deleting records.
SET @has_action = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='user_activity_logs' AND COLUMN_NAME='action');
SET @sql = IF(@has_action=0, 'ALTER TABLE user_activity_logs ADD COLUMN action VARCHAR(80) NOT NULL DEFAULT ''Activity''', 'SELECT ''action column already exists''');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @has_details = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='user_activity_logs' AND COLUMN_NAME='details');
SET @sql = IF(@has_details=0, 'ALTER TABLE user_activity_logs ADD COLUMN details VARCHAR(255) NULL', 'SELECT ''details column already exists''');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @has_created = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='user_activity_logs' AND COLUMN_NAME='created_at');
SET @sql = IF(@has_created=0, 'ALTER TABLE user_activity_logs ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'SELECT ''created_at column already exists''');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
