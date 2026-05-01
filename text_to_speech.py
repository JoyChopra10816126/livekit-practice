from dotenv import load_dotenv
from livekit.agents import AgentSession, JobContext, WorkerOptions, cli, inference, Agent
from livekit.plugins import sarvam, silero

load_dotenv()


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

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # Handles personality and capabilities
    agent = Agent(  
        instructions="You are a helpful assistant.",  
    )  
    
    # Handles infrastructure
    session = AgentSession(  
        vad=silero.VAD.load(),  
        stt=sarvam.STT(**STT_CONFIG),  
        llm=inference.LLM(model=LLM_MODEL),  
        tts=sarvam.TTS(**TTS_CONFIG),  
    )  
  
    await session.start(agent=agent, room=ctx.room)  
    await session.say("Hare Krishna, Prabhu. Please accept my humble obeisances.")
    

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
