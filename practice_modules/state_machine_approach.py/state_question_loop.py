import logging
from typing import AsyncGenerator
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli, inference, llm
from livekit.plugins import sarvam, silero
from dotenv import load_dotenv

# Import the generated BAML client
# Note: You must run `npx baml-cli generate` first
from baml_client import b

load_dotenv()

class StateManager():

    def __init__(self):
        self.state = {}

    def get_state(self, key):
        return self.state.get(key)

    def set_state(self, key, value):
        self.state[key] = value

    def print_state(self):
        logger.info("Printing state:")
        logger.info(self.state)

global_state_manager = StateManager()


QUESTIONS = [
  {
    "id": "intro",
    "diagnostic_goal": "Collect the user's introduction",
    "expected_fields": ["USER_NAME", "USER_LOCATION", "CURRENT_SERVICE"],
    "question1": "Hare Krishna! I am here to help you practice English so we can serve Srila Prabhupada and the mission together. To start, could you please introduce yourself? You can tell me your name, where you are from, and what service you currently do.",
  },
  {
    "id": "history",
    "diagnostic_goal": "Understand how the user first came in contact\nwith the Hare Krishna movement",
    "expected_fields": ["CONTACT_STORY"],
    "question1": "I am curious to know about your journey. How did you first come in contact with the Hare Krishna Movement or the temple? Please tell me that story.",
  },
  {
    "id": "purpose",
    "diagnostic_goal": "Understand the user's motivation for improving spoken English",
    "expected_fields": ["ENGLISH_MOTIVATION", "PREACHING_BENEFIT"],
    "question1": "I want to ask why do you feel it is important for you to improve your spoken English? How will it help you in your preaching service?",
  }
]

logger = logging.getLogger("baml-agent")
logger.setLevel(logging.INFO)
question_state_machine = QuestionStateMachine()

class BamlStructuredAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful assistant that provides structured responses.",
        )

    def complete_question(self, acknolwedgement, current_question_index):
        self.session.say(f"{acknolwedgement}")
        logger.info(f"Acknowledgement: {acknolwedgement}")
        global_state_manager.set_state("current_question_index", current_question_index + 1)

    async def llm_node(
        self,
        chat_ctx: llm.ChatContext,
        tools: list[llm.Tool],
        model_settings,
    ) -> AsyncGenerator[str, None]:
        """Override llm_node to use BAML for structured output."""


        # 1. Prepare history for BAML
        history_str = ""
        for msg in chat_ctx.messages():
            role = "User" if msg.role == "user" else "Assistant"
            if msg.role == "system":
                role = "System"
            
            # Handle content which could be a string or list of blocks
            content = msg.content
            if isinstance(content, list):
                content = " ".join([block.text if hasattr(block, 'text') else str(block) for block in content])
            
            history_str += f"{role}: {content}\n"

        try:
            yield from question_state_machine.process()

            current_question_index = global_state_manager.get_state("current_question_index")
            current_question = QUESTIONS[current_question_index]
            current_question_id = current_question["id"]
            current_question_state = global_state_manager.get_state(current_question_id)

            current_sub_question = current_question_state["current_sub_question"]
            expected_fields = current_question["expected_fields"]
            diagnostic_goal = current_question["diagnostic_goal"]

            if not current_question_state["is_question_1_asked"]:
                yield current_question["question1"]
                current_question_state["is_question_1_asked"] = True
                global_state_manager.set_state(current_question_id, current_question_state)
                return
                

            structured4 = await b.GetResponse4(chat_history=history_str, current_question=current_sub_question)
            if structured4.on_topic_status == "ON_TOPIC":
                if structured4.turn_decision == "REPEAT_QUESTION":
                    yield current_question["question1"]
                elif structured4.turn_decision == "PARAPHRASE_QUESTION":
                    yield structured4.rephrased_question
                elif structured4.turn_decision == "ANALYSE_RESPONSE":
                    structured3 = await b.GetResponse3(chat_history=history_str, diagnostic_goal=diagnostic_goal, expected_fields=expected_fields, current_question=current_sub_question)

                    if structured3.is_diagnostic_goal_met:
                        self.complete_question(structured3.acknowledgement, current_question_index)
                        yield "Thank you Prabhu, let me know when you want to move to next question"

                    else:
                        yield structured3.probe_question
            else:
                yield "Please focus on the assessment Prabhu."
        except Exception as e:
            logger.error(f"BAML call failed: {e}")
            yield "I'm sorry, I encountered an error processing that request."

STT_CONFIG = {
    "language": "en-IN",
    "model": "saaras:v3",
    "mode": "transcribe"
}

TTS_CONFIG = {
    "target_language_code": "en-IN",
    "model": "bulbul:v3",
    "speaker": "manan",
    "pace": 0.85
}

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    agent = BamlStructuredAgent()
    
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=sarvam.STT(**STT_CONFIG),
        llm=inference.LLM(model="openai/gpt-4o-mini"), 
        tts=sarvam.TTS(**TTS_CONFIG),
    )
    question_index = 0
    while question_index < len(QUESTIONS):
        question = QUESTIONS[question_index]
        question_state = {
            "current_sub_question": 1,
            "is_question_1_answered": False, 
            "is_question_1_asked": False
        }
        if question_index == len(QUESTIONS) - 1:
            question_state["next_question_id"] = None
        else:
            question_state["next_question_id"] = QUESTIONS[question_index + 1]["id"]

        global_state_manager.set_state(question["id"], question_state)
        question_index += 1
        
    global_state_manager.set_state("current_question_index", 0)

    await session.start(agent=agent, room=ctx.room)
    await session.say("Hare Krishna Prabhu.")
        
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
