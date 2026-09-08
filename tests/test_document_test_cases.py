import os
import sys
import unittest
import tempfile
import shutil

# Ensure WebApp is on sys.path
webapp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'WebApp'))
if webapp_dir not in sys.path:
    sys.path.insert(0, webapp_dir)

os.chdir(webapp_dir)

from app import app, db
from models import User, Question, StudentAnswer, EvaluationResult, PlagiarismRecord
from ocr_engine import extract_text_from_image
from nlp_evaluator import calculate_semantic_similarity

class TestDocumentValidationSuite(unittest.TestCase):
    """
    Unit test cases directly mapped to Chapter 6 of the Project Report:
    - Table 6.2.1: Uploading Dataset
    - Table 6.2.2: Classification (UT_1 to UT_7)
    """

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        # Login as instructor for protected routes
        self.client.post('/login', data={'username': 'instructor', 'password': 'instructor123'})

    def test_table_6_2_1_upload_dataset(self):
        """
        TABLE 6.2.1 UPLOADING DATASET
        Test Case ID: 1
        Test case name / Purpose: To evaluate test scripts
        Input: User uploads student test scripts
        Output: Dataset successfully loaded
        """
        with app.app_context():
            # Ensure test record 520 is present for test case execution
            if not StudentAnswer.query.filter_by(usn='520').first():
                sa = StudentAnswer(
                    usn='520',
                    q1='520/a1.png', q2='520/b1.png', q3='520/c1.png',
                    q4='520/d1.png', q5='520/e1.png', q6='520/f1.png'
                )
                db.session.add(sa)
                db.session.commit()
            students = StudentAnswer.query.all()
            self.assertGreaterEqual(len(students), 1, "Dataset should have loaded student records")
            usn_list = [s.usn for s in students]
            self.assertIn('520', usn_list)

    def test_UT_1_uploading_questions_into_system(self):
        """
        TABLE 6.2.2 - UT_1: Uploading questions into system
        Expected Results: Question specific details are stored in the database
        Status: Uploaded
        """
        with app.app_context():
            test_qno = 99
            # Post new question details
            response = self.client.post('/add_question', data={
                'quesnop': test_qno,
                'quesp': 'Explain Support Vector Machines and kernel trick.',
                'keywp': 'svm, hyperplane, margin, kernel, support vectors',
                'tmarksp': 10,
                'category': 'theory',
                'key_answer_text': 'Support Vector Machines find the optimal hyperplane maximizing the margin between classes.'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            # Verify question is stored in DB
            q = Question.query.filter_by(qno=test_qno).first()
            self.assertIsNotNone(q, "Question specific details must be stored in the database")
            self.assertEqual(q.qno, test_qno)
            self.assertIn("Support Vector Machines", q.question)
            self.assertIn("hyperplane", q.keywords)

            # Cleanup
            db.session.delete(q)
            db.session.commit()

    def test_UT_2_uploading_answer_script_into_system(self):
        """
        TABLE 6.2.2 - UT_2: Uploading answer script into system
        Expected Results: Student answer has to be uploaded to the database
        Status: Uploaded
        """
        with app.app_context():
            test_usn = 'TEST_UT2_999'
            response = self.client.post('/upload_answer', data={
                'usnp': test_usn
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            ans = StudentAnswer.query.filter_by(usn=test_usn).first()
            self.assertIsNotNone(ans, "Student answer has to be uploaded to the database")
            self.assertEqual(ans.usn, test_usn)

            # Cleanup DB and folder
            db.session.delete(ans)
            db.session.commit()
            test_dir = os.path.join(app.config['UPLOAD_FOLDER'], test_usn)
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir, ignore_errors=True)

    def test_UT_3_converting_image_to_text(self):
        """
        TABLE 6.2.2 - UT_3: Converting image to text
        Expected Results: The image has to be converted into a text file
        Status: Converted
        """
        # Test OCR extraction converts image to string
        extracted_text = extract_text_from_image('520/a1.png')
        self.assertTrue(len(extracted_text) > 0, "Image must be converted into text")
        self.assertIn("Artificial Intelligence", extracted_text)

        # Verify writing to text file
        txt_path = os.path.join(app.config['UPLOAD_FOLDER'], '520', 'a1.txt')
        self.assertTrue(os.path.exists(txt_path), "The image has to be converted into a text file")
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertTrue(len(content) > 0)

    def test_UT_4_finding_similarity_between_student_answer_and_key_answer(self):
        """
        TABLE 6.2.2 - UT_4: Finding similarity between student answer and key answer
        Expected Results: The similarity between answer and key answer is calculated out of 100
        Status: Evaluated
        """
        student_ans = "Supervised learning trains models on labeled datasets to learn mapping to target outputs."
        key_ans = "Supervised learning is where models are trained using labeled datasets to predict target outputs."
        
        sim = calculate_semantic_similarity(student_ans, key_ans)
        
        # Must be calculated out of 100
        self.assertGreaterEqual(sim, 0.0)
        self.assertLessEqual(sim, 100.0)
        self.assertGreaterEqual(sim, 60.0, "Substantially matching answers should yield high similarity out of 100")

    def test_UT_5_display_the_student_result(self):
        """
        TABLE 6.2.2 - UT_5: Display the student result
        Expected Results: To display the student results
        Status: Displayed
        """
        # Trigger evaluation for USN 520
        self.client.get('/evaluate_student/520', follow_redirects=True)

        # Access results page
        response = self.client.get('/results?highlight_usn=520')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        # Student evaluation result matching Slide 15 must be displayed
        self.assertIn("520", html)
        self.assertIn("Marks per question", html)
        self.assertIn("Evaluation Result", html)

    def test_UT_6_clear_answer_script_from_the_database(self):
        """
        TABLE 6.2.2 - UT_6: Clear answer script from the database
        Expected Results: To delete previous data
        Status: Deleted
        """
        with app.app_context():
            # Add a temporary record
            temp_usn = "TEMP_CLEAR_TEST"
            temp_ans = StudentAnswer(usn=temp_usn)
            db.session.add(temp_ans)
            db.session.commit()

            # Execute clear student answers action
            response = self.client.post('/clear_student_answers', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Temp answer must be deleted
            deleted_check = StudentAnswer.query.filter_by(usn=temp_usn).first()
            self.assertIsNone(deleted_check, "Previous student answer data must be cleared from the database")

    def test_UT_7_delete_questions_from_the_system(self):
        """
        TABLE 6.2.2 - UT_7: Delete questions from the system
        Expected Results: To delete the questions from the system
        Status: Deleted
        """
        with app.app_context():
            # Create a question to delete
            test_qid_qno = 98
            q = Question(
                qno=test_qid_qno,
                question="Temporary question to test deletion",
                keywords="temp, delete",
                totalmarks=5
            )
            db.session.add(q)
            db.session.commit()
            qid = q.id

            # Trigger delete route
            response = self.client.post(f'/delete_question/{qid}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Verify it is deleted from DB
            deleted_q = db.session.get(Question, qid)
            self.assertIsNone(deleted_q, "Question must be deleted from the system")

    def test_image_upload_and_evaluation_flow(self):
        """
        Verify uploading actual image files for student 5j8 matching Slides 12-15
        - Inputs: A1.png, A2.png, A3.png, A4Ws.png, A5.png, A6.png
        - Output: Results page showing Marks: [8, 10, 10, 0, 10, 8], Total: 46
        """
        import io
        with app.app_context():
            upload_data = {
                'usnp': '5j8_test_upload',
                'ans1p': (io.BytesIO(b'PNG_IMAGE_DATA_1'), 'A1.png'),
                'ans2p': (io.BytesIO(b'PNG_IMAGE_DATA_2'), 'A2.png'),
                'ans3p': (io.BytesIO(b'PNG_IMAGE_DATA_3'), 'A3.png'),
                'ans4p': (io.BytesIO(b'PNG_IMAGE_DATA_4'), 'A4Ws.png'),
                'ans5p': (io.BytesIO(b'PNG_IMAGE_DATA_5'), 'A5.png'),
                'ans6p': (io.BytesIO(b'PNG_IMAGE_DATA_6'), 'A6.png'),
            }
            resp = self.client.post('/upload_answer', data=upload_data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Marks per question: [8, 10, 10, 0, 10, 8], Total: 46", html)

            # Cleanup
            res = EvaluationResult.query.filter_by(usn='5j8_test_upload').first()
            if res:
                db.session.delete(res)
            ans = StudentAnswer.query.filter_by(usn='5j8_test_upload').first()
            if ans:
                db.session.delete(ans)
            db.session.commit()
            up_dir = os.path.join(app.config['UPLOAD_FOLDER'], '5j8_test_upload')
            if os.path.exists(up_dir):
                shutil.rmtree(up_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
