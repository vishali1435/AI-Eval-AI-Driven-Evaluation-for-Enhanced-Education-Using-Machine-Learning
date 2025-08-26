import re

def generate_reply(message):
    message = message.lower()

    # Score-related questions
    if re.search(r"\b(score|mark|grade|how many)\b", message):
        return "You can view your marks per question in the result section. If you'd like, I can help explain specific ones."

    # Feedback about a specific answer
    elif re.search(r"\bwhy.*(wrong|incorrect|lost marks|only.*marks)\b", message):
        return "The evaluation is based on key concepts and clarity. Some important points might have been missing in your answer."

    # Asking if the answer was correct
    elif re.search(r"\bwas.*(correct|right|okay)\b", message):
        return "Your answer may be partially correct, but it lacked the required keywords or detail."

    # Asking how to improve an answer
    elif re.search(r"\b(improve|better|full marks|rewrite)\b", message):
        return "To improve, try to include all keywords, explain in your own words, and keep answers concise yet complete."

    # Asking how the system works
    elif re.search(r"\b(how.*work|system|evaluate|check|graded|algorithm)\b", message):
        return "The system uses keyword matching, semantic similarity, and grammar checks to evaluate your answer."

    # Who checked the paper
    elif re.search(r"\bwho.*(checked|evaluated|graded)\b", message):
        return "Your answers were evaluated automatically by our AI-based system."

    # Greetings
    elif re.search(r"\b(hi|hello|hey)\b", message):
        return "Hi there! How can I help with your paper evaluation?"

    # Thank you
    elif re.search(r"\b(thanks|thank you)\b", message):
        return "You're welcome! Let me know if you have more questions."

    # Disagreement
    elif re.search(r"\b(wrong|not fair|disagree|mistake)\b", message):
        return "I'm sorry you feel that way. You can request a manual review if needed."

    # Default fallback
    else:
        return "I'm here to help with your answer evaluations. You can ask me why you got a certain score, how to improve, or how the system works!"
