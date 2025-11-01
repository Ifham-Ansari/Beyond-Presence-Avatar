import argparse
import os
import sys

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    WorkerType,
    cli,
)
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import bey, openai
from livekit.plugins import silero


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    voice_agent_session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral",  
        ),
        vad=silero.VAD.load(),
    )

    voice_agent = Agent(
        instructions="You are English helpful assistance with a visual presence."
    )

    bey_avatar_session = bey.AvatarSession(
        avatar_id="694c83e2-8895-4a98-bd16-56332ca3f449"
    )

    await voice_agent_session.start(agent=voice_agent, room=ctx.room)
    await bey_avatar_session.start(voice_agent_session, room=ctx.room)

    await voice_agent_session.generate_reply(
        instructions="You should start by speaking in English. Greet the user saying **Welcome to the bots how can i help you**"
    )


if __name__ == "__main__":
    load_dotenv()
    sys.argv = [sys.argv[0], "dev"]  
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
        )
    )