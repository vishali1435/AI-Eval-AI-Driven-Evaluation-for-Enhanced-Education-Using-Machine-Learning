import os
import sys

# Get absolute path to WebApp directory
curr_dir = os.path.dirname(os.path.abspath(__file__))
webapp_dir = os.path.join(curr_dir, 'WebApp')

if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)
if webapp_dir not in sys.path:
    sys.path.insert(0, webapp_dir)

os.chdir(webapp_dir)

from WebApp.app import app

if __name__ == '__main__':
    print("================================================================")
    print("  AI Eval: AI Driven Evaluation for Enhanced Education")
    print("  Starting Flask Server on http://127.0.0.1:5000")
    print("  Default Instructor Login: username=instructor, password=instructor123")
    print("  Default Student Login:    username=student, password=student123")
    print("================================================================")
    app.run(debug=False, host='0.0.0.0', port=5000)
