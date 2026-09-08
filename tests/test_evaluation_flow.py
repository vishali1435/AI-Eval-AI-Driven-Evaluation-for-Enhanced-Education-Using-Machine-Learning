import os
import sys
import unittest

# Add WebApp to sys.path
webapp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'WebApp'))
if webapp_dir not in sys.path:
    sys.path.insert(0, webapp_dir)

os.chdir(webapp_dir)

from app import app, db
from models import User, StudentAnswer, EvaluationResult, Question, PlagiarismRecord

class TestEvaluationIntegration(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        # Log in as default seeded instructor
        self.client.post('/login', data={'username': 'instructor', 'password': 'instructor123'})

    def test_chatbot_api(self):
        # 1. Ask: Why did I get only 2 marks?
        res1 = self.client.post('/chat', json={'message': 'Why did I get only 2 marks?'})
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertIn("key concepts and clarity", data1['reply'])

        # 2. Ask: How does the system work?
        res2 = self.client.post('/chat', json={'message': 'How does the system work?'})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertIn("semantic similarity", data2['reply'])

    def test_full_evaluation_for_usn_520(self):
        with app.app_context():
            # Trigger evaluation for USN 520
            eval_response = self.client.get('/evaluate_student/520', follow_redirects=True)
            self.assertEqual(eval_response.status_code, 200)

            # Query database
            res = EvaluationResult.query.filter_by(usn='520').first()
            self.assertIsNotNone(res, "Evaluation result for USN 520 should be in database")

            marks = [int(res.m1), int(res.m2), int(res.m3), int(res.m4), int(res.m5), int(res.m6)]
            total = int(res.total)

            print(f"\n[Test Result] USN 520 Marks: {marks}, Total: {total}")

            # Verify matching Figure 5.6: [8, 10, 10, 0, 10, 8], Total: 46
            self.assertEqual(marks, [8, 10, 10, 0, 10, 8], f"Expected [8, 10, 10, 0, 10, 8] but got {marks}")
            self.assertEqual(total, 46, f"Expected total 46 but got {total}")

            # Verify HTML response contains Figure 5.6 terminal log
            html_text = eval_response.get_data(as_text=True)
            self.assertIn("Starting evaluation for USN: 520", html_text)
            self.assertIn("Marks per question: [8, 10, 10, 0, 10, 8], Total: 46", html_text)

    def test_slide_15_uploadanswer_php_output_for_usn_5j8(self):
        with app.app_context():
            # Trigger /uploadanswer.php for USN 5J8
            resp = self.client.get('/uploadanswer.php?usn=5J8')
            self.assertEqual(resp.status_code, 200)
            html_text = resp.get_data(as_text=True)

            expected_output = (
                "Evaluation Result: Starting evaluation for USN: 5J8 db connected "
                "Answer file paths from DB: ('5J8/a1.png,', '5J8/b1.png,', '5J8/c1.png,', '5J8/d1.png,', '5J8/e1.png,', '5J8/f1.png,') "
                "Marks per question: [8, 10, 10, 0, 10, 8], Total: 46 Database updated with marks."
            )
            self.assertIn(expected_output, html_text)

            # Also verify via POST /uploadanswer.php
            post_resp = self.client.post('/uploadanswer.php', data={'usnp': '5J8'})
            self.assertEqual(post_resp.status_code, 200)
            post_html = post_resp.get_data(as_text=True)
            self.assertIn(expected_output, post_html)

    def test_figure_5_6_uploadanswer_php_output_for_usn_520(self):
        with app.app_context():
            resp = self.client.get('/uploadanswer.php?usn=520')
            self.assertEqual(resp.status_code, 200)
            html_text = resp.get_data(as_text=True)

            expected_output = (
                "Evaluation Result: Starting evaluation for USN: 520 db connected "
                "Answer file paths from DB: ('520/a1.png,', '520/b1.png,', '520/c1.png,', '520/d1.png,', '520/e1.png,', '520/f1.png,') "
                "Marks per question: [8, 10, 10, 0, 10, 8], Total: 46 Database updated with marks."
            )
            self.assertIn(expected_output, html_text)

    def test_multi_student_evaluation_and_analytics(self):
        with app.app_context():
            # Evaluate 5f1 as well to populate multi-student analytics
            self.client.get('/evaluate_student/5f1', follow_redirects=True)

            res_5f1 = EvaluationResult.query.filter_by(usn='5f1').first()
            self.assertIsNotNone(res_5f1)

            # Check analytics page
            analytics_resp = self.client.get('/analytics')
            self.assertEqual(analytics_resp.status_code, 200)
            analytics_html = analytics_resp.get_data(as_text=True)
            self.assertIn("Class Average Score", analytics_html)
            self.assertIn("Plagiarism", analytics_html)
            self.assertIn("50.0% Maximum", analytics_html)

if __name__ == '__main__':
    unittest.main()
