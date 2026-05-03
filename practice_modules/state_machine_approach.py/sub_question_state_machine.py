
class Node():
    def __init__(self):
        self.does_need_to_say = False
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class AskQuestionNode(Node):
    def __init__(self):
        pass

    def process(self):
        yield "question"
        should_move_to_next_node = True
        return should_move_to_next_node

    def get_next_node(self):
        pass

class Evaluation1Node(Node):
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class Evaluation2Node(Node):
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class Evaluation3Node(Node):
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class OffTopicNode(Node):
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class DiagnosticNotMetNode(Node):
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class CompleteQuestionNode(Node):
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class SubQuestionStateMachine():
    def __init__(self):
        self.local_state_manager = StateManager()
        self.populate_local_state()
        self.current_node = AskQuestionNode()
    
    def populate_local_state(self):
        for question in QUESTIONS:
            self.local_state_manager.set_state(question["id"], {
                "is_question_1_asked": False,
                "is_question_2_asked": False,
                "is_feedback_given": False,
                "current_sub_question": 1,
                "expected_fields": question["expected_fields"],
                "diagnostic_goal": question["diagnostic_goal"],
            })
    
    def process(self):
        should_move_to_next_node = yield from self.current_node.process()
        if should_move_to_next_node:
            self.move_to_next_node()
        should_move_to_next_question = True
        return should_move_to_next_question
    
    def move_to_next_node(self):
        self.current_node = self.current_node.get_next_node()
