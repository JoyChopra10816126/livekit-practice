from livekit.agents import get_job_context
from .types import Question
from .question_state_machine import QuestionStateMachine
from .logger_utils import log_state_transition, log_action

class Node():
    def __init__(self):
        pass

    async def process(self):
        pass

    def move_to_next_node(self):
        pass

    def pretty_print(self):
        return self.__class__.__name__

class QuestionNode(Node):
    def __init__(self, question: Question):
        # Create a state machine which will conduct the question
        self.question = question
        self.question_state_machine = QuestionStateMachine(question)

    async def process(self):
        log_action("QuestionNode", f"Processing question {self.question.id}")
        has_message_to_say, should_move_to_next_node = await self.question_state_machine.process()
        return has_message_to_say, should_move_to_next_node

    def pretty_print(self):
        return f"QuestionNode(id={self.question.id})"

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
        log_state_transition("AssessmentStateMachine", None, self.current_node, f"Starting assessment with question {self.current_question_index}")
    
    async def process(self):
        has_message_to_say = False
        # Pause process if agent needs to say to user
        while self.current_node is not None and not has_message_to_say:
            has_message_to_say, should_move_to_next_node = await self.current_node.process()
            if should_move_to_next_node:
                self._move_to_next_node()    
        return has_message_to_say        

    def _move_to_next_node(self):
        # Move to next question
        old_node = self.current_node
        self.current_question_index += 1

        # Create node for next question if exists
        if self.current_question_index < self.number_of_questions:
            question = self.questions[self.current_question_index]
            self.current_node = QuestionNode(question)
            log_state_transition("AssessmentStateMachine", old_node, self.current_node, f"Moving to question {self.current_question_index}")
        # Else, end assessment
        else:
            self.current_node = None
            log_state_transition("AssessmentStateMachine", old_node, None, "Assessment completed")
            print("Assessment completed!")
