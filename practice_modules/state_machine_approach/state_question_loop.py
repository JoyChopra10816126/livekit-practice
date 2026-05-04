import logging
from typing import AsyncGenerator
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli, inference, llm, get_job_context
from livekit.plugins import sarvam, silero
from dotenv import load_dotenv

from .types import Question, SubQuestion
from .assessment_state_machine import AssessmentStateMachine

# Import the generated BAML client
# Note: You must run `npx baml-cli generate` first
from baml_client import b

load_dotenv()


QUESTIONS = [
  {
    "id": "intro",
    "diagnostic_goal": "Collect the user's introduction",
    "expected_fields": ["USER_NAME", "USER_LOCATION", "CURRENT_SERVICE"],
    "sub_question1": "Hare Krishna! I am here to help you practice English so we can serve Srila Prabhupada and the mission together. To start, could you please introduce yourself? You can tell me your name, where you are from, and what service you currently do.",
  },
  {
    "id": "history",
    "diagnostic_goal": "Understand how the user first came in contact\nwith the Hare Krishna movement",
    "expected_fields": ["CONTACT_STORY"],
    "sub_question1": "I am curious to know about your journey. How did you first come in contact with the Hare Krishna Movement or the temple? Please tell me that story.",
  },
  {
    "id": "purpose",
    "diagnostic_goal": "Understand the user's motivation for improving spoken English",
    "expected_fields": ["ENGLISH_MOTIVATION", "PREACHING_BENEFIT"],
    "sub_question1": "I want to ask why do you feel it is important for you to improve your spoken English? How will it help you in your preaching service?",
  }
]

logger = logging.getLogger("baml-agent")
logger.setLevel(logging.INFO)

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
            ctx = get_job_context()
            userdata = ctx.proc.userdata
            userdata["chat_history"] = history_str

            assessment_state_machine = userdata["assessment_state_machine"]
            has_message_to_say = await assessment_state_machine.process()
            
            if has_message_to_say:
                messages = userdata.get("messages_to_say", [])
                combined_message = " ".join(messages)
                userdata["messages_to_say"] = [] # Clear for next time
                yield f"{combined_message}"
        except Exception as e:
            logger.error(f"BAML call failed: {e}", exc_info=True)
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
    userdata = ctx.proc.userdata
    
    agent = BamlStructuredAgent()
    
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=sarvam.STT(**STT_CONFIG),
        llm=inference.LLM(model="openai/gpt-4o-mini"), 
        tts=sarvam.TTS(**TTS_CONFIG),
    )
    await session.start(agent=agent, room=ctx.room)
    await session.say("Hare Krishna Prabhu.")

    question_objects = []
    for q in QUESTIONS:
        sub_q1 = SubQuestion(q["sub_question1"], q["diagnostic_goal"], q["expected_fields"])
        # Support optional sub_question2 if present in the data
        sub_q2 = None
        if "sub_question2" in q:
            sub_q2 = SubQuestion(q["sub_question2"], q["diagnostic_goal"], q["expected_fields"])
        
        question_objects.append(Question(q["id"], sub_q1, sub_q2))

    assessment_state_machine = AssessmentStateMachine(question_objects)
    userdata["assessment_state_machine"] = assessment_state_machine
    userdata["messages_to_say"] = []
        
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
