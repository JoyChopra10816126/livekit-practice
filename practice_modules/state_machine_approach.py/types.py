class SubQuestion():
    def __init__(self, sub_question_text, diagnostic_goal, expected_fields):
        self.sub_question_text = sub_question_text
        self.diagnostic_goal = diagnostic_goal
        self.expected_fields = expected_fields

class Question():
    def __init__(self, id, sub_question1_text, sub_question2_text, diagnostic_goal1, diagnostic_goal2, expected_fields1, expected_fields2):
        self.id = id
        self.sub_question1 = SubQuestion(sub_question1_text, diagnostic_goal1, expected_fields1)
        self.sub_question2 = SubQuestion(sub_question2_text, diagnostic_goal2, expected_fields2)
