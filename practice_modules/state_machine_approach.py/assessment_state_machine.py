from types import Question
from question_state_machine import QuestionStateMachine

class Node():
    def __init__(self):
        pass

    def process(self):
        pass

    def move_to_next_node(self):
        pass

class QuestionNode(Node):
    def __init__(self, question: Question):
        self.question = question
        self.question_state_machine = QuestionStateMachine(question)

    def process(self):
        should_move_to_next_node = self.question_state_machine.process()
        return should_move_to_next_node

class AssessmentStateMachine():
    def __init__(self, questions):
        # Load questions to be asked in assessment
        self.questions = questions
        
        # Calculate number of questions
        self.number_of_questions = len(questions)
        
        # Initialize variable to keep track of current question
        self.current_question_index = 0

        # Create first node
        question = self.questions[self.current_question_index]
        self.current_node = QuestionNode(question)
    
    def process(self):
        should_move_to_next_node = self.current_node.process()
        if should_move_to_next_node:
            self.move_to_next_node()

    def move_to_next_node(self):
        # Move to next question
        self.current_question_index += 1

        # Create node for next question if exists
        if self.current_question_index < self.number_of_questions:
            question = self.questions[self.current_question_index]
            self.current_node = QuestionNode(question)
        # Else, end assessment
        else:
            self.current_node = None
            print("Assessment completed!")
