from livekit.agents import get_job_context
from baml_client import b
from logger_utils import log_state_transition, log_action

class Node():
    def __init__(self):
        pass

    def process(self, userdata):
        pass

    def get_next_node(self):
        pass

    def pretty_print(self):
        return self.__class__.__name__

class AskQuestionNode(Node):
    def __init__(self, sub_question, follow_up_question = None):
        self.sub_question = sub_question
        self.follow_up_question = follow_up_question

    def process(self, userdata):
        if self.follow_up_question:
            log_action("AskQuestionNode", f"Asking follow-up: {self.follow_up_question[:30]}...")
            userdata["text_to_say"] = self.follow_up_question
        else:
            log_action("AskQuestionNode", f"Asking sub-question: {self.sub_question.sub_question_text[:30]}...")
            userdata["text_to_say"] = self.sub_question.sub_question_text
        return True

    def pretty_print(self):
        text = self.follow_up_question if self.follow_up_question else self.sub_question.sub_question_text
        return f"AskQuestionNode({text[:30]}...)"

    def get_next_node(self):
        return Evaluation1Node(self.sub_question)

class Evaluation1Node(Node):
    def __init__(self, sub_question):
        self.sub_question = sub_question

    def process(self, userdata):
        log_action("Evaluation1Node", f"Evaluating topic status for: {self.sub_question.sub_question_text[:30]}...")
        self.evaluation: b.EvaluationLayerModel1 = b.EvaluationLayer1(
            chat_history=userdata["chat_history"], current_question=self.sub_question.sub_question_text)
        return True

    def get_next_node(self):
        if self.evaluation.on_topic_status == b.ON_TOPIC_STATUS_1.ON_TOPIC:
            return Evaluation2Node(self.sub_question)
        else:
            return AskQuestionNode(self.sub_question, "Please focus on the assessment Prabhu.")

class Evaluation2Node(Node):
    def __init__(self, sub_question):
        self.sub_question = sub_question

    def process(self, userdata):
        log_action("Evaluation2Node", f"Evaluating user intent for: {self.sub_question.sub_question_text[:30]}...")
        self.evaluation: b.EvaluationLayerModel2 = b.EvaluationLayer2(
            chat_history=userdata["chat_history"], current_question=self.sub_question.sub_question_text)
        return True

    def get_next_node(self):
        if self.evaluation.user_intent == "REPEAT_QUESTION":
            return AskQuestionNode(self.sub_question)
        elif self.evaluation.user_intent == "REPHRASE_QUESTION":
            return AskQuestionNode(self.sub_question, self.evaluation.rephrased_question)
        elif self.evaluation.user_intent == "PROVIDED_RESPONSE":
            return Evaluation3Node(self.sub_question)

class Evaluation3Node(Node):
    def __init__(self, sub_question):
        self.sub_question = sub_question

    def process(self, userdata):
        log_action("Evaluation3Node", f"Evaluating diagnostic goal for: {self.sub_question.sub_question_text[:30]}...")
        self.evaluation: b.EvaluationLayerModel3 = b.EvaluationLayer3(
            chat_history=userdata["chat_history"],
            diagnostic_goal=self.sub_question.diagnostic_goal,
            expected_fields=self.sub_question.expected_fields, 
            current_question=self.sub_question.sub_question_text)
        return True

    def get_next_node(self):
        if self.evaluation.is_diagnostic_goal_met == b.IS_DIAGNOSTIC_GOAL_MET_1.TRUE:
            return CompleteQuestionNode(self.evaluation.acknowledgement)
        else:
            return AskQuestionNode(self.sub_question, self.evaluation.probe_question)

class CompleteQuestionNode(Node):
    def __init__(self, acknolwedgement):
        self.acknolwedgement = acknolwedgement

    def process(self, userdata):
        log_action("CompleteQuestionNode", f"Acknowledging: {self.acknolwedgement[:30]}...")
        userdata["text_to_say"] = self.acknolwedgement
        return True

    def get_next_node(self):
        return None

class SubQuestionStateMachine():
    def __init__(self, sub_question):
        self.sub_question = sub_question
        self.current_node = AskQuestionNode(sub_question)

        ctx = get_job_context()  
        self.userdata = ctx.proc.userdata
        log_state_transition("SubQuestionStateMachine", None, self.current_node, f"Starting sub-question: {sub_question.sub_question_text[:30]}...")
        
    def process(self):
        should_move_to_next_node = self.current_node.process(self.userdata)
        if should_move_to_next_node:
            is_complete = self.move_to_next_node()
            return is_complete
        return False
    
    def move_to_next_node(self):
        old_node = self.current_node
        self.current_node = self.current_node.get_next_node()
        log_state_transition("SubQuestionStateMachine", old_node, self.current_node)
        if self.current_node is None:
            print("Completed sub question")
            return True
        return False
