from dotenv import load_dotenv
from livekit.agents import AgentSession, JobContext, WorkerOptions, cli, inference, Agent
from livekit.plugins import sarvam, silero

import logging

load_dotenv()

logger = logging.getLogger("livekit-practice")
logger.setLevel(logging.INFO)


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
        logger.info(f"User turn completed! Transcript: {new_message.text_content}")
        logger.info(f"Turn context: {turn_ctx.to_dict()}")
  
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

    await session.start(agent=agent, room=ctx.room)  
    

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
