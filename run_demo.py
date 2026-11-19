from services.git_client import GitClient
from services.repository_scanner import RepositoryScanner
from services.aggregator import AssessmentAggregator
from services.database import Database
from models.entities import LanguageScore, TechCategory, LANGUAGE_CATEGORY

def demo():
    print("=" * 60 + "\nDEMO: Оценка FastAPI\n" + "=" * 60)
    git_client = GitClient('./temp_repos')
    scanner = RepositoryScanner(git_client)
    aggregator = AssessmentAggregator()
    db = Database()
    try:
        metrics = scanner.scan_repository('https://github.com/tiangolo/fastapi', ['Python', 'HTML'])
        scores = []
        for lang, m_list in metrics.items():
            if not m_list: continue
            cat = LANGUAGE_CATEGORY.get(lang.lower(), TechCategory.ALGORITHM)
            avg_loc = sum(m.lines_of_code for m in m_list) / len(m_list)
            type_ratio = sum(1 for m in m_list if m.has_type_hints) / len(m_list)
            err_ratio = sum(1 for m in m_list if m.has_error_handling) / len(m_list)
            score = min(100, max(0, min(100, avg_loc / 5) * 0.3 + type_ratio * 100 * 0.4 + err_ratio * 100 * 0.3))
            print("  " + lang + ": " + str(round(score, 1)) + "%")
            scores.append(LanguageScore(language=lang, score=score, category=cat))
        result = aggregator.aggregate(scores)
        db.save_assessment('https://github.com/tiangolo/fastapi', 'FastAPI', result, scores)
        print("=" * 60 + "\nОБЩИЙ: " + str(result.overall_score) + "% (" + result.level_name + ")\n" + result.feedback + "\n" + "=" * 60)
    finally:
        git_client.cleanup_all()

if __name__ == '__main__': demo()
