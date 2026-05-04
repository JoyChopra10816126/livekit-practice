class SubQuestion():
    def __init__(self, sub_question_text, diagnostic_goal, expected_fields):
        self.sub_question_text = sub_question_text
        self.diagnostic_goal = diagnostic_goal
        self.expected_fields = expected_fields

class Question():
    def __init__(self, id, sub_question1, sub_question2=None):
        self.id = id
        self.sub_question1 = sub_question1
        self.sub_question2 = sub_question2
