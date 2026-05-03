class Question():
    def __init__(self, id, diagnostic_goal, expected_fields, sub_question1, sub_question2):
        self.id = id
        self.diagnostic_goal = diagnostic_goal
        self.expected_fields = expected_fields
        self.sub_question1 = sub_question1
        self.sub_question2 = sub_question2
