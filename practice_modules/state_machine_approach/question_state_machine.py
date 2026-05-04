from .sub_question_state_machine import SubQuestionStateMachine
from .logger_utils import log_state_transition, log_action

class SubQuestionNode():
    def __init__(self, current_sub_question, next_sub_question):
        self.current_sub_question = current_sub_question
        self.next_sub_question = next_sub_question

    async def process(self):
        pass

    def get_next_node(self):
        pass

    def pretty_print(self):
        return self.__class__.__name__

class SubQuestion1Node(SubQuestionNode):
    def __init__(self, current_sub_question, next_sub_question):
        super().__init__(current_sub_question, next_sub_question)
        self.sub_question_state_machine = SubQuestionStateMachine(self.current_sub_question)

    async def process(self):
        log_action("SubQuestion1Node", f"Processing sub-question 1: {self.current_sub_question.sub_question_text[:30]}...")
        has_message_to_say, should_move_to_next_question = await self.sub_question_state_machine.process()
        return has_message_to_say, should_move_to_next_question

    def get_next_node(self):
        if self.next_sub_question is None:
            return None
        return SubQuestion2Node(self.next_sub_question, None)


class SubQuestion2Node(SubQuestionNode):
    def __init__(self, current_sub_question, next_sub_question):
        super().__init__(current_sub_question, next_sub_question)
        self.sub_question_state_machine = SubQuestionStateMachine(self.current_sub_question)

    async def process(self):
        log_action("SubQuestion2Node", f"Processing sub-question 2: {self.current_sub_question.sub_question_text[:30]}...")
        has_message_to_say, should_move_to_next_question = await self.sub_question_state_machine.process()
        return has_message_to_say, should_move_to_next_question

    def get_next_node(self):
        return None

class QuestionStateMachine():
    def __init__(self, question):
        self.current_node = SubQuestion1Node(question.sub_question1, question.sub_question2)
        log_state_transition("QuestionStateMachine", None, self.current_node, f"Starting question {question.id}")
    
    async def process(self):
        has_message_to_say = False
        while self.current_node is not None and not has_message_to_say:
            has_message_to_say, should_move_to_next_node = await self.current_node.process()
            if should_move_to_next_node:
                is_complete = self.move_to_next_node()
                if is_complete:
                    return has_message_to_say, True
        return has_message_to_say, False

    def move_to_next_node(self):
        old_node = self.current_node
        self.current_node = self.current_node.get_next_node()
        log_state_transition("QuestionStateMachine", old_node, self.current_node)
        if self.current_node is None:
            print("Completing question")
            return True
        return False
