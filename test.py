# -----------------------------------------------------------
# NOTE: This code does not work. It was used to help learn and test the LiveKit API. The main.py file is the one that actually works.
# -----------------------------------------------------------

import asyncio # Enables asynchronous programming in Python (EDIT: No it doesn't, you can still use await without asyncio imported)

from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
#from livekit.agents.voice import VoiceAssistant
from livekit.plugins import openai, silero
from livekit.agents import AgentSession, Agent, RoomInputOptions

# Load environment variables from .env file so that we can use them in the code
load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

async def entrypoint(ctx: JobContext):
    # This is where I can add in some context to start the AI voice assistant, the same way we give a templated prompt to OpenAI or some LLM
    # initial_ctx = llm.ChatContext().append(
    #     role="system",
    #     text=(
    #         "You are a voice assistant. "
    #         "You can answer questions, provide information, and assist with tasks. "
    #         "You should use short and concise responses, and avoid usage of unpronouncable punctuation."
    #     ),
    # )
    # Specifying that we only want to connect to the audio tracks, we don't care about the video tracks
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create a voice assistant instance / Define the voice assistant
    assistant = AgentSession(
        vad=silero.VAD.load(), # vad stands for Voice Activity Detection. Here we specify what kind of model we're using to detect if the user is speaking or not so we know when to cut them off
        stt=openai.STT(), # stt stands for Speech to Text
        llm=openai.LLM(), # llm stands for Large Language Model
        tts=openai.TTS(), # tts stands for Text to Speech
        #chat_ctx=initial_ctx # chat_ctx is the context that we defined above
    )

    # Start the voice assistant
    await assistant.start(room=ctx.room,
                    agent=Assistant()) 
    # The voice assistants in LiveKit can connect to a room and listen to the audio tracks in that room. We can have multiple rooms going at the same time. These voice assistants can connect to one of them, all of them, they can scale infinitely. We are saying here that we want to connect to the room that's being provided by this job context
    # Our agent is going to connect to the LiveKit server. The LiveKit server is then going to send the agent a job. When that job is sent, it's going to have a room associated with it
    # This line says we want to start the voice assistant and connect it to the room that was provided by the job context. The job context is a wrapper around the room that was provided by LiveKit. The room is a place where we can send and receive audio tracks. The job context is a wrapper around the room that provides us with some additional functionality, like connecting to the room and sending and receiving audio tracks.

    await asyncio.sleep(1) # Sleep for 1 second to give the assistant time to connect to the room
    #await assistant.say("Hey, how can I help you today?", allow_interruptions=True) # Say something to the user. This is the first thing that the assistant will say when it connects to the room. The allow_interruptions parameter specifies whether or not the user can interrupt the assistant while it's speaking. If it's set to True, the user can interrupt the assistant. If it's set to False, the user can't interrupt the assistant.
    # This is how you send a manual message with the voice assistant

    await assistant.generate_reply(
        instructions="Greet the user and offer your assistance."
    )

if __name__ == "__main__":
    # Run a new application. That application is going to be a worker and that worker is going to be the entrypoint function.
    # entrypoint_fnc is the function that will be called when the agent is started
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))