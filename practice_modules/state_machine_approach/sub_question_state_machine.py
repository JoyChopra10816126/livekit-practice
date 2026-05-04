from livekit.agents import get_job_context
from baml_client import b, types
from .logger_utils import log_state_transition, log_action

class Node():
    def __init__(self):
        pass

    async def process(self, userdata):
        pass

    def get_next_node(self):
        pass

    def pretty_print(self):
        return self.__class__.__name__

class AskQuestionNode(Node):
    def __init__(self, sub_question, follow_up_question = None):
        self.sub_question = sub_question
        self.follow_up_question = follow_up_question

    async def process(self, userdata):
        if self.follow_up_question:
            log_action("AskQuestionNode", f"Asking follow-up: {self.follow_up_question[:30]}...")
            userdata["messages_to_say"].append(self.follow_up_question)
        else:
            log_action("AskQuestionNode", f"Asking sub-question: {self.sub_question.sub_question_text[:30]}...")
            userdata["messages_to_say"].append(self.sub_question.sub_question_text)
        return True, True

    def pretty_print(self):
        text = self.follow_up_question if self.follow_up_question else self.sub_question.sub_question_text
        return f"AskQuestionNode({text[:30]}...)"

    def get_next_node(self):
        return Evaluation1Node(self.sub_question)

class Evaluation1Node(Node):
    def __init__(self, sub_question):
        self.sub_question = sub_question

    async def process(self, userdata):
        log_action("Evaluation1Node", f"Evaluating topic status for: {self.sub_question.sub_question_text[:30]}...")
        self.evaluation: types.EvaluationLayerModel1 = await b.EvaluationLayer1(
            chat_history=userdata["chat_history"], current_question=self.sub_question.sub_question_text)
        return False, True

    def get_next_node(self):
        if self.evaluation.on_topic_status == types.ON_TOPIC_STATUS_1.ON_TOPIC:
            return Evaluation2Node(self.sub_question)
        else:
            return AskQuestionNode(self.sub_question, "Please focus on the assessment Prabhu.")

class Evaluation2Node(Node):
    def __init__(self, sub_question):
        self.sub_question = sub_question

    async def process(self, userdata):
        log_action("Evaluation2Node", f"Evaluating user intent for: {self.sub_question.sub_question_text[:30]}...")
        self.evaluation: types.EvaluationLayerModel2 = await b.EvaluationLayer2(
            chat_history=userdata["chat_history"], current_question=self.sub_question.sub_question_text)
        return False, True

    def get_next_node(self):
        if self.evaluation.user_intent == types.USER_INTENT.REPEAT_QUESTION:
            return AskQuestionNode(self.sub_question)
        elif self.evaluation.user_intent == types.USER_INTENT.REPHRASE_QUESTION:
            return AskQuestionNode(self.sub_question, self.evaluation.rephrased_question)
        elif self.evaluation.user_intent == types.USER_INTENT.PROVIDED_RESPONSE:
            return Evaluation3Node(self.sub_question)

class Evaluation3Node(Node):
    def __init__(self, sub_question):
        self.sub_question = sub_question

    async def process(self, userdata):
        log_action("Evaluation3Node", f"Evaluating diagnostic goal for: {self.sub_question.sub_question_text[:30]}...")
        self.evaluation: types.EvaluationLayerModel3 = await b.EvaluationLayer3(
            chat_history=userdata["chat_history"],
            diagnostic_goal=self.sub_question.diagnostic_goal,
            expected_fields=self.sub_question.expected_fields, 
            current_question=self.sub_question.sub_question_text)
        return False, True

    def get_next_node(self):
        if self.evaluation.is_diagnostic_goal_met == types.DiagnosticGoalMetStatus1.YES:
            return CompleteQuestionNode(self.evaluation.acknowledgement)
        else:
            return AskQuestionNode(self.sub_question, self.evaluation.probe_question)

class CompleteQuestionNode(Node):
    def __init__(self, acknolwedgement):
        self.acknolwedgement = acknolwedgement

    async def process(self, userdata):
        log_action("CompleteQuestionNode", f"Acknowledging: {self.acknolwedgement[:30]}...")
        userdata["messages_to_say"].append(self.acknolwedgement)
        return False, True

    def get_next_node(self):
        return None

class SubQuestionStateMachine():
    def __init__(self, sub_question):
        self.sub_question = sub_question
        self.current_node = AskQuestionNode(sub_question)

        ctx = get_job_context()  
        self.userdata = ctx.proc.userdata
        log_state_transition("SubQuestionStateMachine", None, self.current_node, f"Starting sub-question: {sub_question.sub_question_text[:30]}...")
        
    async def process(self):
        has_message_to_say = False
        while self.current_node is not None and not has_message_to_say:
            has_message_to_say, should_move_to_next_node = await self.current_node.process(self.userdata)
            if should_move_to_next_node:
                is_complete = self.move_to_next_node()
                if is_complete:
                    return has_message_to_say, True
        return has_message_to_say, False
    
    def move_to_next_node(self):
        old_node = self.current_node
        self.current_node = self.current_node.get_next_node()
        log_state_transition("SubQuestionStateMachine", old_node, self.current_node)
        if self.current_node is None:
            print("Completed sub question")
            return True
        return False
