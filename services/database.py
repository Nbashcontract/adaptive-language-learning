import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path="poly_skill.db"):
        self.db_path = Path(db_path)
        # Разрешаем использование соединения в отдельном потоке DB Writer
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            name TEXT,
            overall_score REAL,
            level_name TEXT,
            industry_level TEXT,
            feedback TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS language_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            language TEXT,
            score REAL,
            category TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )""")
        self.conn.commit()

    def save_assessment(self, url, name, result, scores):
        c = self.conn.cursor()
        c.execute("""INSERT OR REPLACE INTO projects 
                     (url, name, overall_score, level_name, industry_level, feedback) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (url, name, result.overall_score, result.level_name, 
                   result.industry_equivalent, result.feedback))
        project_id = c.lastrowid
        
        for score in scores:
            c.execute("""INSERT INTO language_scores 
                         (project_id, language, score, category) 
                         VALUES (?, ?, ?, ?)""",
                      (project_id, score.language, score.score, score.category.value))
        self.conn.commit()

    def get_all_projects(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name, url, overall_score, level_name FROM projects")
        return c.fetchall()

    def get_unique_languages(self):
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT language FROM language_scores")
        return [row[0] for row in c.fetchall()]

    def get_scores_by_language(self, language):
        c = self.conn.cursor()
        c.execute("""SELECT p.name, ls.score FROM language_scores ls 
                     JOIN projects p ON ls.project_id = p.id 
                     WHERE ls.language = ?""", (language,))
        return c.fetchall()