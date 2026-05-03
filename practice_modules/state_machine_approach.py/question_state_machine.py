
class SubQuestionNode():
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class SubQuestion1Node(SubQuestionNode):
    def __init__(self):
        self.is_sub_question_asked = False
        self.is_sub_question_done = False
        self.sub_question_state_machine = SubQuestionStateMachine()

    def process(self):
        should_move_to_next_question = yield from self.sub_question_state_machine.process()
        return should_move_to_next_question

    def move_to_next_node(self):
        self.sub_question_state_machine.move_to_next_node()


class SubQuestion2Node(SubQuestionNode):
    def __init__(self):
        self.is_sub_question_asked = False
        self.is_sub_question_done = False
        sub_question_state_machine = SubQuestionStateMachine()

    def process(self):
        current_node = self.sub_question_state_machine.get_next_node()
        current_node.process()

    def move_to_next_node(self):
        self.sub_question_state_machine.move_to_next_node()

class QuestionStateMachine():
    def __init__(self):
        self.context = {}
        self.current_node = SubQuestion1Node()
    
    def process(self):
        should_move_to_next_sub_question = yield from self.current_node.process()
        if should_move_to_next_sub_question:
            self.move_to_next_question()

    def move_to_next_node(self):
        self.current_node = self.current_node.get_next_node()
    
    def get_next_node(self):
        return self.current_node.get_next_node()
