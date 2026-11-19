import customtkinter as ctk
import sqlite3
from pathlib import Path

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
DB_PATH = Path(__file__).parent / "poly_skill.db"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PolySkill - Оценка кода")
        self.geometry("1000x600")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="PolySkill", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        ctk.CTkButton(self.sidebar, text="Обновить", command=self.load_data).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkLabel(self.sidebar, text="Проекты:", anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=20, pady=(10, 0))
        self.proj_frame = ctk.CTkScrollableFrame(self.sidebar, width=210)
        self.proj_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="Языки:", anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=20, pady=(10, 0))
        self.lang_frame = ctk.CTkScrollableFrame(self.sidebar, width=210)
        self.lang_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.header = ctk.CTkLabel(self.main, text="Выберите проект или язык", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=20)
        self.details = ctk.CTkFrame(self.main)
        self.details.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.load_data()

    def load_data(self):
        for w in self.proj_frame.winfo_children(): w.destroy()
        for w in self.lang_frame.winfo_children(): w.destroy()
        if not DB_PATH.exists():
            ctk.CTkLabel(self.proj_frame, text="Нет БД. Запустите run_demo.py", text_color="red").pack(pady=20)
            return
        conn = sqlite3.connect(str(DB_PATH)); c = conn.cursor()
        c.execute('SELECT id, name, level_name FROM projects')
        for p in c.fetchall():
            ctk.CTkButton(self.proj_frame, text=p[1] + " (" + p[2] + ")", height=50, command=lambda pid=p[0]: self.show_proj(pid)).pack(fill="x", pady=5)
        c.execute('SELECT DISTINCT language FROM language_scores')
        for r in c.fetchall():
            ctk.CTkButton(self.lang_frame, text=r[0], fg_color="gray", command=lambda l=r[0]: self.show_lang(l)).pack(fill="x", pady=5)
        conn.close()

    def show_proj(self, pid):
        for w in self.details.winfo_children(): w.destroy()
        conn = sqlite3.connect(str(DB_PATH)); c = conn.cursor()
        c.execute('SELECT name, overall_score, level_name, industry_level, feedback FROM projects WHERE id=?', (pid,))
        p = c.fetchone()
        c.execute('SELECT language, score FROM language_scores WHERE project_id=?', (pid,))
        scores = c.fetchall(); conn.close()
        if not p: return
        self.header.configure(text="Проект: " + p[0])
        ctk.CTkLabel(self.details, text=str(p[1]) + "%", font=ctk.CTkFont(size=40, weight="bold"), text_color="#2ecc71").pack(pady=10)
        ctk.CTkLabel(self.details, text=p[2] + " (" + p[3] + ")", font=ctk.CTkFont(size=18)).pack(pady=5)
        ctk.CTkLabel(self.details, text="Отзыв:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        tb = ctk.CTkTextbox(self.details, height=80); tb.insert("0.0", p[4]); tb.configure(state="disabled"); tb.pack(fill="x", pady=5, padx=20)
        ctk.CTkLabel(self.details, text="Языки:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        for lang, score in scores:
            row = ctk.CTkFrame(self.details); row.pack(fill="x", pady=5, padx=20)
            ctk.CTkLabel(row, text=lang, width=120, anchor="w").pack(side="left", padx=10)
            pb = ctk.CTkProgressBar(row, width=300); pb.pack(side="left", padx=10, pady=10); pb.set(score / 100.0)
            ctk.CTkLabel(row, text=str(round(score, 1)) + "%", width=60).pack(side="left", padx=10)

    def show_lang(self, lang):
        for w in self.details.winfo_children(): w.destroy()
        conn = sqlite3.connect(str(DB_PATH)); c = conn.cursor()
        c.execute('SELECT p.name, ls.score FROM language_scores ls JOIN projects p ON ls.project_id = p.id WHERE ls.language = ?', (lang,))
        items = c.fetchall(); conn.close()
        self.header.configure(text="Язык: " + lang)
        ctk.CTkLabel(self.details, text="Проекты с " + lang + ":", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=20, pady=10)
        for name, score in items:
            row = ctk.CTkFrame(self.details); row.pack(fill="x", pady=5, padx=20)
            ctk.CTkLabel(row, text=name, width=200, anchor="w").pack(side="left", padx=10)
            pb = ctk.CTkProgressBar(row, width=300); pb.pack(side="left", padx=10, pady=10); pb.set(score / 100.0)
            ctk.CTkLabel(row, text=str(round(score, 1)) + "%", width=60).pack(side="left", padx=10)

if __name__ == "__main__": App().mainloop()
