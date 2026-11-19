import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_name="poly_skill.db"):
        self.db_path = Path(__file__).parent.parent / db_name
        self.conn = sqlite3.connect(str(self.db_path)); self.create_tables()
    def create_tables(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, name TEXT, overall_score REAL, level_name TEXT, industry_level TEXT, feedback TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS language_scores (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, language TEXT, score REAL, category TEXT, FOREIGN KEY(project_id) REFERENCES projects(id))")
        self.conn.commit()
    def save_assessment(self, url, name, result, scores):
        c = self.conn.cursor()
        c.execute('INSERT OR REPLACE INTO projects (url, name, overall_score, level_name, industry_level, feedback) VALUES (?, ?, ?, ?, ?, ?)', (url, name, result.overall_score, result.level_name, result.industry_equivalent, result.feedback))
        self.conn.commit()
        c.execute('SELECT id FROM projects WHERE url = ?', (url,)); row = c.fetchone()
        if not row: return
        pid = row[0]; c.execute('DELETE FROM language_scores WHERE project_id = ?', (pid,))
        for s in scores:
            cat_val = s.category.value if hasattr(s.category, 'value') else str(s.category)
            c.execute('INSERT INTO language_scores (project_id, language, score, category) VALUES (?, ?, ?, ?)', (pid, s.language, s.score, cat_val))
        self.conn.commit()
    def get_all_projects(self):
        c = self.conn.cursor(); c.execute('SELECT id, name, url, overall_score, level_name FROM projects'); return c.fetchall()
    def get_unique_languages(self):
        c = self.conn.cursor(); c.execute('SELECT DISTINCT language FROM language_scores'); return [r[0] for r in c.fetchall()]
    def get_scores_by_language(self, lang):
        c = self.conn.cursor(); c.execute('SELECT p.name, ls.score FROM language_scores ls JOIN projects p ON ls.project_id = p.id WHERE ls.language = ?', (lang,)); return c.fetchall()
