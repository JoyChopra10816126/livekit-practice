from dotenv import load_dotenv
from livekit.agents import AgentSession, JobContext, WorkerOptions, cli, inference, Agent
from livekit.plugins import sarvam, silero
import json
import logging
import datetime

load_dotenv()

logger = logging.getLogger("livekit-practice")
logger.setLevel(logging.INFO)

class TranscriptManager:
    def __init__(self):
        self.transcript = []
        self.is_complete = False
        
        # Local file report name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_file = f"conversation_report_{timestamp}.json"

    def append_event(self, event: dict) -> None:
        """Append an event to the transcript."""
        self.transcript.append(event)

    def save_local(self):
        """Save the transcript to a local JSON file."""
        try:
            with open(self.report_file, "w") as f:
                json.dump(self.transcript, f, indent=2)
            logger.info(f"Saved transcript locally to {self.report_file}")
        except Exception as e:
            logger.error(f"Failed to save local transcript: {e}")

    def mark_complete(self):
        """Mark the session as complete."""
        self.is_complete = True
        logger.info(f"Session {self.session_id} marked as complete.")


# Configuration Constants
LLM_MODEL = "openai/gpt-4o-mini"

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

class EchoAgent(Agent):  
    def __init__(self):  
        super().__init__(  
            instructions="You are an echo assistant.",  
        )  
      
    async def on_user_turn_completed(self, turn_ctx, new_message):  
        # Echo back what the user said  
        self.session.say(f"Captured: {new_message.text_content}")  
        

tm = TranscriptManager()

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    
    # Handles personality and capabilities
    agent = EchoAgent()
    
    # Handles infrastructure
    session = AgentSession(  
        vad=silero.VAD.load(),  
        stt=sarvam.STT(**STT_CONFIG),  
        llm=inference.LLM(model=LLM_MODEL),  
        tts=sarvam.TTS(**TTS_CONFIG),  
    )  

    def _extract_text_from_message(message) -> str | None:
        text = getattr(message, "text_content", None)
        if text:
            return text
        content = getattr(message, "content", None) or []
        for c in content:
            transcript_text = getattr(c, "transcript", None)
            if transcript_text:
                return transcript_text
        return None

    @session.on("conversation_item_added")
    def on_conversation_item_added(ev):
        message = getattr(ev, "item", None)
        if message is None:
            return
        role = getattr(message, "role", None)
        
        text = _extract_text_from_message(message)
        if text is None:
            return
        tm.append_event({
            "role": role,
            "text": text,
            "timestamp": str(datetime.datetime.now()),
        })
        tm.save_local()


    await session.start(agent=agent, room=ctx.room)  
    

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
