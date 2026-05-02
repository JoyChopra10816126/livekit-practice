import logging
from typing import AsyncGenerator
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli, inference, llm
from livekit.plugins import sarvam, silero
from dotenv import load_dotenv

# Import the generated BAML client
# Note: You must run `npx baml-cli generate` first
from baml_client import b
from baml_client.types import Response

load_dotenv()

logger = logging.getLogger("baml-agent")
logger.setLevel(logging.INFO)

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


state_manager = StateManager()


class BamlStructuredAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful assistant that provides structured responses.",
        )

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
            # 2. Call BAML function
            logger.info("Calling BAML GetResponse...")
            structured: Response = await b.GetResponse(chat_history=history_str)
            logger.info(f"BAML Response: {structured}")

            # 3. Yield the parts to be spoken
            if structured.grammatical_errors_present:
                yield str(structured.grammatical_errors_present) + " "
            if structured.corrected_transcript:
                yield str(structured.corrected_transcript) + " "
            if structured.explanation_for_student:
                yield str(structured.explanation_for_student)

            errors = state_manager.get_state("errors")
            if errors is None:
                errors = []
            errors.append({
                "grammatical_errors_present": structured.grammatical_errors_present,
                "corrected_transcript": structured.corrected_transcript,
                "explanation_for_student": structured.explanation_for_student
            })
            state_manager.set_state("errors", errors)
            state_manager.print_state()

            yield("You can control what I say.")
                    
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

    await session.start(agent=agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
