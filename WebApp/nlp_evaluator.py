import re
import string
import math
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure stopwords are available
try:
    STOP_WORDS = set(stopwords.words('english'))
except Exception:
    STOP_WORDS = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
        'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'it', 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'what', 'which', 'who', 'whom', 'this',
        'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a',
        'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
        'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
        'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
        'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
        'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
        'just', 'don', 'should', 'now'
    }

def clean_and_tokenize(text):
    """
    Remove punctuation and stopwords, convert to lowercase tokens.
    """
    if not text:
        return []
    text = text.lower()
    # Strip punctuation
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text_clean = text.translate(translator)
    tokens = re.findall(r'\b[a-zA-Z]{2,}\b', text_clean)
    filtered = [w for w in tokens if w not in STOP_WORDS]
    return filtered

def get_synonyms(word):
    """
    Retrieve synonyms for a given word using NLTK WordNet.
    """
    synonyms = set()
    try:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                name = lemma.name().lower().replace('_', ' ')
                synonyms.add(name)
    except Exception:
        pass
    return synonyms

def calculate_keyword_match(student_text, key_keywords, key_answer_text=""):
    """
    Calculate keyword match ratio (0.0 to 100.0) between student answer and essential keywords/key answer.
    Supports WordNet synonym matching.
    """
    if not student_text or not student_text.strip():
        return 0.0, []

    student_tokens = set(clean_and_tokenize(student_text))
    
    # Extract target keywords
    target_keywords = set()
    if key_keywords:
        parts = re.split(r'[,;|\n]+', key_keywords)
        for part in parts:
            p = part.strip().lower()
            if p:
                target_keywords.update(clean_and_tokenize(p))
    
    if key_answer_text and not target_keywords:
        target_keywords = set(clean_and_tokenize(key_answer_text))

    if not target_keywords:
        return 50.0, []

    matched_keywords = []
    missing_keywords = []

    for kw in target_keywords:
        if kw in student_tokens:
            matched_keywords.append(kw)
        else:
            # Check for synonyms
            syns = get_synonyms(kw)
            if syns & student_tokens:
                matched_keywords.append(f"{kw} (syn)")
            else:
                missing_keywords.append(kw)

    ratio = (len(matched_keywords) / len(target_keywords)) * 100.0
    return min(100.0, round(ratio, 2)), missing_keywords

def calculate_semantic_similarity(student_text, key_answer_text):
    """
    Calculate semantic similarity using CountVectorizer and Cosine Similarity (0.0 to 100.0).
    """
    if not student_text or not student_text.strip():
        return 0.0
    if not key_answer_text or not key_answer_text.strip():
        return 50.0

    try:
        corpus = [student_text, key_answer_text]
        vectorizer = CountVectorizer(stop_words='english')
        count_matrix = vectorizer.fit_transform(corpus)
        sim = cosine_similarity(count_matrix[0:1], count_matrix[1:2])[0][0]
        return round(float(sim) * 100.0, 2)
    except Exception as e:
        print(f"[NLP] Error in CountVectorizer cosine_similarity: {e}")
        return 0.0

def calculate_grammar_score(text):
    """
    Evaluate structural grammar, sentence completion, capitalization, and punctuation quality.
    Returns a score between 0.0 and 100.0.
    """
    if not text or not text.strip():
        return 0.0

    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if not sentences:
        return 30.0

    valid_sentences = 0
    total_words = 0
    
    for s in sentences:
        words = s.split()
        total_words += len(words)
        # Check capitalization of first letter
        starts_capital = s[0].isupper() if s else False
        has_min_words = len(words) >= 3
        if starts_capital and has_min_words:
            valid_sentences += 1

    sentence_quality = (valid_sentences / len(sentences)) * 70.0
    length_factor = min(30.0, (total_words / 30.0) * 30.0)
    score = sentence_quality + length_factor
    return min(100.0, round(score, 2))

def calculate_length_score(text, max_expected_words=150):
    """
    Evaluate length based on total words and sentences, aligned with document's ansLen function.
    Returns a normalized score (0.0 to 10.0).
    """
    if not text or not text.strip():
        return 0.0

    words = text.split()
    num_words = len(words)
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    ans_length = len(sentences)

    if num_words > 80:
        w_score = 10.0
    elif num_words > 60:
        w_score = 8.5
    elif num_words > 40:
        w_score = 7.0
    elif num_words > 20:
        w_score = 5.0
    elif num_words > 5:
        w_score = 3.0
    else:
        w_score = 1.0

    if ans_length >= 4:
        s_score = 10.0
    elif ans_length >= 3:
        s_score = 8.0
    elif ans_length >= 2:
        s_score = 6.0
    elif ans_length >= 1:
        s_score = 4.0
    else:
        s_score = 0.0

    return round((w_score + s_score) / 2.0, 2)

def evaluate_single_answer(student_text, key_answer_text, keywords, total_marks=10):
    """
    Runs full NLP feature extraction and provides a criteria breakdown and constructive feedback.
    """
    if not student_text or not student_text.strip():
        return {
            'marks': 0.0,
            'keyword_ratio': 0.0,
            'cosine_sim': 0.0,
            'grammar_score': 0.0,
            'length_score': 0.0,
            'word_count': 0,
            'feedback': "Question not attempted or empty answer sheet."
        }

    word_count = len(student_text.split())
    kw_ratio, missing_kws = calculate_keyword_match(student_text, keywords, key_answer_text)
    cosine_sim = calculate_semantic_similarity(student_text, key_answer_text)
    grammar_score = calculate_grammar_score(student_text)
    length_score = calculate_length_score(student_text)

    # Feedback generation
    feedback_points = []
    if kw_ratio >= 80.0:
        feedback_points.append("Excellent keyword coverage.")
    elif kw_ratio >= 50.0:
        feedback_points.append("Good conceptual coverage; incorporate remaining core terms.")
    else:
        missing_sample = ", ".join(list(missing_kws)[:3])
        feedback_points.append(f"Missing key technical concepts: {missing_sample}.")

    if cosine_sim >= 70.0:
        feedback_points.append("High semantic similarity to reference answer.")
    elif cosine_sim < 40.0:
        feedback_points.append("Elaborate on core definitions and context.")

    if grammar_score < 60.0:
        feedback_points.append("Improve sentence structure and formatting.")

    feedback_str = " ".join(feedback_points)

    return {
        'keyword_ratio': kw_ratio,
        'cosine_sim': cosine_sim,
        'grammar_score': grammar_score,
        'length_score': length_score,
        'word_count': word_count,
        'feedback': feedback_str
    }
