import os
import sys
import unittest

# Ensure WebApp is in sys.path
webapp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'WebApp'))
if webapp_dir not in sys.path:
    sys.path.insert(0, webapp_dir)

from ocr_engine import extract_text_from_image
from nlp_evaluator import (
    clean_and_tokenize,
    calculate_keyword_match,
    calculate_semantic_similarity,
    calculate_grammar_score,
    evaluate_single_answer
)
from ml_model import predict_marks
from plagiarism_detector import calculate_pairwise_plagiarism
from chatbot_logic import generate_reply

class TestAIEvalCore(unittest.TestCase):

    def test_ocr_extraction(self):
        # Test known sample USN 520 answer 1
        text = extract_text_from_image('520/a1.png')
        self.assertIn("Artificial Intelligence", text)
        self.assertIn("smart machines", text)

        # Test empty/unattempted answer sheet
        text_d = extract_text_from_image('520/d1.png')
        self.assertEqual(text_d, "")

    def test_nlp_keyword_matching(self):
        student_text = "Artificial intelligence enables smart machines and computer algorithms to learn from data."
        keywords = "artificial intelligence, machines, algorithms, learning, data"
        ratio, missing = calculate_keyword_match(student_text, keywords)
        self.assertGreaterEqual(ratio, 80.0)

    def test_nlp_semantic_similarity(self):
        text1 = "Supervised learning trains machine learning models on labeled data to predict outputs."
        key1 = "In supervised learning, models learn from labeled datasets to predict output variables."
        sim = calculate_semantic_similarity(text1, key1)
        self.assertGreaterEqual(sim, 50.0)

    def test_grammar_scoring(self):
        good_text = "Natural Language Processing enables computers to understand human language."
        score = calculate_grammar_score(good_text)
        self.assertGreaterEqual(score, 60.0)

    def test_ml_scoring_model(self):
        # High quality answer features -> high marks
        marks_high = predict_marks(cosine_sim=85.0, keyword_ratio=90.0, word_count=50, grammar_score=90.0, max_marks=10)
        self.assertGreaterEqual(marks_high, 8.0)

        # Empty answer -> 0 marks
        marks_zero = predict_marks(cosine_sim=0.0, keyword_ratio=0.0, word_count=0, grammar_score=0.0, max_marks=10)
        self.assertEqual(marks_zero, 0.0)

    def test_plagiarism_cap_enforcement(self):
        # Exact identical text
        t1 = "Supervised learning maps inputs to targets using labeled datasets with linear regression and support vector machines."
        t2 = "Supervised learning maps inputs to targets using labeled datasets with linear regression and support vector machines."
        sim = calculate_pairwise_plagiarism(t1, t2)
        # MUST BE CAPPED AT 50.0%
        self.assertLessEqual(sim, 50.0)
        self.assertEqual(sim, 50.0)

        # Completely different text -> near 0
        diff_text = "Quantum computing uses qubits and quantum entanglement."
        sim_low = calculate_pairwise_plagiarism(t1, diff_text)
        self.assertLess(sim_low, 20.0)

    def test_chatbot_intent_matching(self):
        # Check "Why did I get only 2 marks?" (Figure 5.5)
        reply1 = generate_reply("Why did I get only 2 marks?")
        self.assertIn("evaluation is based on key concepts and clarity", reply1)

        # Check "How does the system work?" (Figure 5.5)
        reply2 = generate_reply("How does the system work?")
        self.assertIn("keyword matching, semantic similarity, and grammar checks", reply2)

        # Check score inquiry
        reply3 = generate_reply("What is my score?")
        self.assertIn("result section", reply3)

        # Check plagiarism query
        reply4 = generate_reply("How is plagiarism detected?")
        self.assertIn("capped at 50%", reply4)

if __name__ == '__main__':
    unittest.main()
