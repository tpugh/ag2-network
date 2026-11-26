"""Example 05 — human-in-the-loop via HumanClient.

An agent consults a human; the human answers from the console.
"""
import asyncio

from ag2 import Agent
from ag2.network import CONVERSATION_TYPE, EV_TEXT, Hub, HubClient, LocalLink, Passport
from ag2.network.testing import MemoryKnowledgeStore

from common import make_config


async def main() -> None:
    config = make_config()
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)

    agent = await hub.register(Agent("expert", prompt="You are a helpful tutor.", config=config))

    hc = HubClient(LocalLink(hub), hub=hub)
    human = await hc.register_human(Passport(name="student"))

    channel = await human.open(type=CONVERSATION_TYPE, target=agent.agent_id)
    await channel.send("Hi — what's a good first ML concept to learn?")

    try:
        reply = await human.next_envelope(
            predicate=lambda e: e.event_type == EV_TEXT and e.sender_id == agent.agent_id,
            timeout=120.0,
        )
        print(f"expert> {reply.event_data['text']}")
    except TimeoutError:
        print("expert> (no reply within 120s)")

    await channel.close(reason="student_done")
    await human.disconnect()
    await hub.close()


if __name__ == "__main__":
    asyncio.run(main())