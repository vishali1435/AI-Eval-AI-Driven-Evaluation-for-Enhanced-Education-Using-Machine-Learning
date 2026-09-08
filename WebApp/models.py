from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), default='instructor') # 'instructor' or 'student'
    full_name = db.Column(db.String(120), default='Faculty Evaluator')
    avatar_url = db.Column(db.String(255), default='/static/images/avatar_default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_instructor(self):
        return self.user_type.lower() == 'instructor'

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    qno = db.Column(db.Integer, unique=True, nullable=False)
    question = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=True) # comma or space-separated keywords
    totalmarks = db.Column(db.Integer, default=10)
    category = db.Column(db.String(20), default='theory') # 'theory' or 'program'
    textpic = db.Column(db.String(255), nullable=True) # reference image path
    key_answer_text = db.Column(db.Text, nullable=True) # standard key answer text

class StudentAnswer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(50), unique=True, nullable=False)
    # File paths for answer scans
    q1 = db.Column(db.Text, nullable=True)
    q2 = db.Column(db.Text, nullable=True)
    q3 = db.Column(db.Text, nullable=True)
    q4 = db.Column(db.Text, nullable=True)
    q5 = db.Column(db.Text, nullable=True)
    q6 = db.Column(db.Text, nullable=True)
    # Extracted OCR text
    q1_text = db.Column(db.Text, nullable=True)
    q2_text = db.Column(db.Text, nullable=True)
    q3_text = db.Column(db.Text, nullable=True)
    q4_text = db.Column(db.Text, nullable=True)
    q5_text = db.Column(db.Text, nullable=True)
    q6_text = db.Column(db.Text, nullable=True)
    # Marks per question & total
    m1 = db.Column(db.Float, default=0.0)
    m2 = db.Column(db.Float, default=0.0)
    m3 = db.Column(db.Float, default=0.0)
    m4 = db.Column(db.Float, default=0.0)
    m5 = db.Column(db.Float, default=0.0)
    m6 = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    evaluated = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)

class EvaluationResult(db.Model):
    __tablename__ = 'evaluation_result'
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(50), nullable=False)
    m1 = db.Column(db.Float, default=0.0)
    m2 = db.Column(db.Float, default=0.0)
    m3 = db.Column(db.Float, default=0.0)
    m4 = db.Column(db.Float, default=0.0)
    m5 = db.Column(db.Float, default=0.0)
    m6 = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    breakdown_json = db.Column(db.Text, nullable=True) # JSON with detailed criteria scores
    feedback_json = db.Column(db.Text, nullable=True) # JSON with constructive advice
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

class PlagiarismRecord(db.Model):
    __tablename__ = 'plagiarism_record'
    id = db.Column(db.Integer, primary_key=True)
    usn1 = db.Column(db.String(50), nullable=False)
    usn2 = db.Column(db.String(50), nullable=False)
    qno = db.Column(db.Integer, nullable=False)
    similarity_pct = db.Column(db.Float, default=0.0) # capped at 50.0%
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

class SubjectDetails(db.Model):
    __tablename__ = 'subject_details'
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), default='18CS71')
    subject_name = db.Column(db.String(100), default='Artificial Intelligence & Machine Learning')
    internal = db.Column(db.String(20), default='IA-1')
