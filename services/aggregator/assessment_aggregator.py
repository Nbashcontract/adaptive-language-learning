from models.entities import StackAssessment, WEIGHT_MATRIX

class AssessmentAggregator:
    LEVELS = [(0, 19, "Новичок", "Trainee"), (20, 39, "Начинающий", "Junior-"), (40, 59, "Базовый", "Junior"), (60, 79, "Уверенный", "Middle"), (80, 100, "Эксперт", "Senior")]
    def aggregate(self, scores):
        if not scores: return StackAssessment([], 0.0, "Новичок", "Trainee", "Нет данных")
        total_w, total_s = 0.0, 0.0
        for s in scores:
            w = WEIGHT_MATRIX.get(s.category, 0.5); pf = 1.0
            if s.pattern_verdicts:
                avg = sum(v.appropriateness for v in s.pattern_verdicts) / len(s.pattern_verdicts)
                pf = 0.8 + avg * 0.2
            total_s += s.score * w * pf; total_w += w
        overall = total_s / total_w if total_w > 0 else 0.0
        level, ind = "Неизвестно", "-"
        for mn, mx, n, i in self.LEVELS:
            if mn <= overall <= mx: level, ind = n, i; break
        fb = f"Общий уровень: {round(overall, 1)}% ({level} / {ind}).\n"
        if scores: fb += f"Сильная сторона: {max(scores, key=lambda x: x.score).language}.\n"
        fb += "Вы можете самостоятельно разрабатывать приложения." if overall >= 60 else "Рекомендуется углубить знания."
        return StackAssessment(scores, round(overall, 1), level, ind, fb)
