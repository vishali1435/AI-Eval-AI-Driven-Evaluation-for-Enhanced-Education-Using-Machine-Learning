import re
from difflib import SequenceMatcher

MAX_PLAGIARISM_CAP = 50.0  # Mandated 50% maximum cap per project requirements

def clean_text_for_plagiarism(text):
    """
    Normalizes text for plagiarism matching by stripping punctuation and normalizing whitespace.
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return " ".join(text.split())

def calculate_pairwise_plagiarism(text1, text2):
    """
    Calculates content similarity between two student submissions for a question.
    Returns capped plagiarism score (max 50.0%).
    """
    clean1 = clean_text_for_plagiarism(text1)
    clean2 = clean_text_for_plagiarism(text2)

    if not clean1 or not clean2:
        return 0.0

    # Sequence matcher ratio for string matching
    matcher = SequenceMatcher(None, clean1, clean2)
    raw_ratio = matcher.ratio() * 100.0

    # Word-level Jaccard similarity
    words1 = set(clean1.split())
    words2 = set(clean2.split())
    if words1 and words2:
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        jaccard = (intersection / union) * 100.0
    else:
        jaccard = 0.0

    # Blended similarity
    combined_sim = (raw_ratio * 0.6) + (jaccard * 0.4)

    # Strictly cap at 50% as specified in Core Functional Requirements
    capped_score = round(min(combined_sim, MAX_PLAGIARISM_CAP), 2)
    return capped_score

def check_cross_plagiarism(current_usn, current_answers_dict, all_students_answers):
    """
    Compares current student's answers against all other submissions in the database.
    current_answers_dict: {qno: answer_text}
    all_students_answers: list of dicts with 'usn' and question text
    Returns: list of plagiarism records
    """
    records = []
    for other in all_students_answers:
        other_usn = other.get('usn')
        if other_usn == current_usn:
            continue

        for qno in range(1, 7):
            ans1 = current_answers_dict.get(qno, "")
            ans2 = other.get(f'q{qno}_text', "")
            if ans1 and ans2:
                sim = calculate_pairwise_plagiarism(ans1, ans2)
                if sim > 5.0:  # Only record non-trivial overlap
                    records.append({
                        'usn1': current_usn,
                        'usn2': other_usn,
                        'qno': qno,
                        'similarity_pct': sim
                    })
    return records
