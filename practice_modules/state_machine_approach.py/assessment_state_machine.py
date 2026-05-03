class Node():
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class QuestionNode(Node):
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass

class MapNode(Node):
    def __init__(self):
        pass

    def process(self):
        pass

    def get_next_node(self):
        pass


class AssessmentStateMachine():
    def __init__(self):
        self.context = {}
        self.current_node = QuestionNode()
    
    def process(self):
        should_move_to_next_sub_question = yield from self.current_node.process()
        if should_move_to_next_sub_question:
            self.move_to_next_question()

    def move_to_next_node(self):
        self.current_node = self.current_node.get_next_node()
    
    def get_next_node(self):
        return self.current_node.get_next_node()
