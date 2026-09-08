import re

def generate_reply(message):
    """
    Chatbot logic responding to questions about scores, evaluation algorithms,
    feedback, manual review requests, and academic integrity.
    Directly matches Figure 5.5 in the project documentation.
    """
    if not message:
        return "Please ask a question regarding your evaluation, scores, or feedback!"

    message = message.lower().strip()

    # Feedback about a specific answer / Why only X marks? (Matches Figure 5.5)
    if re.search(r"\bwhy.*(wrong|incorrect|lost marks|only.*marks|\b[0-9]+\s*marks?)\b", message):
        return "The evaluation is based on key concepts and clarity. Some important points might have been missing in your answer."

    # How does the system work? (Matches Figure 5.5)
    elif re.search(r"\b(how.*(work|system|evaluate|check|graded|algorithm|calculate))\b", message):
        return "The system uses keyword matching, semantic similarity, and grammar checks to evaluate your answer."

    # Plagiarism check queries
    elif re.search(r"\b(plagiarism|plagiarized|plagiarised|plagiar|copied|copying|cheat|cheating|similarity|integrity)\b", message):
        return "The system checks student scripts for copied content using string and semantic matching, with the similarity score capped at 50%."

    # Score-related questions
    elif re.search(r"\b(score|mark|grade|how many|total|result)\b", message):
        return "You can view your marks per question in the result section. If you'd like, I can help explain specific ones."

    # Asking if the answer was correct
    elif re.search(r"\bwas.*(correct|right|okay|good)\b", message):
        return "Your answer may be partially correct, but it lacked the required keywords or detail."

    # Asking how to improve an answer
    elif re.search(r"\b(improve|better|full marks|rewrite|tips|study)\b", message):
        return "To improve, try to include all keywords, explain in your own words, and keep answers concise yet complete."

    # Who checked the paper
    elif re.search(r"\bwho.*(checked|evaluated|graded|evaluator|teacher)\b", message):
        return "Your answers were evaluated automatically by our AI-based system."

    # Greetings
    elif re.search(r"\b(hi|hello|hey|greetings|good morning|good evening)\b", message):
        return "Hi there! How can I help with your paper evaluation?"

    # Thank you
    elif re.search(r"\b(thanks|thank you|thx)\b", message):
        return "You're welcome! Let me know if you have more questions."

    # Disagreement / Manual review request
    elif re.search(r"\b(wrong|not fair|disagree|mistake|manual review|re-evaluat|recheck)\b", message):
        return "I'm sorry you feel that way. You can request a manual review from your instructor if needed."

    # Default fallback
    else:
        return "I'm here to help with your answer evaluations. You can ask me why you got a certain score, how to improve, or how the system works!"
