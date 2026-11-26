"""Example 03 — round-robin multi-party discussion.

`discussion` adapter: 2+ participants, round-robin turn order, explicit close.
"""
import asyncio

from ag2 import Agent
from ag2.network import EV_CHANNEL_CLOSED, EV_TEXT, Hub
from ag2.network.testing import MemoryKnowledgeStore

from common import make_config


async def main() -> None:
    config = make_config()
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)
    alice = await hub.register(Agent("alice", prompt="You are an optimist.", config=config))
    bob = await hub.register(Agent("bob", prompt="You are a skeptic.", config=config))
    carol = await hub.register(Agent("carol", prompt="You are a pragmatist.", config=config))

    channel = await alice.open(type="discussion", target=["bob", "carol"])
    await channel.send("Topic: should we adopt microservices?", audience=[bob.agent_id, carol.agent_id])

    # Let a couple of rounds happen, then close.
    await asyncio.sleep(20)
    await channel.close(reason="rounds_complete")
    await asyncio.sleep(1)

    wal = await hub.read_wal(channel.channel_id)
    for env in wal:
        if env.event_type == EV_TEXT:
            name = "alice" if env.sender_id == alice.agent_id else ("bob" if env.sender_id == bob.agent_id else "carol")
            print(f"{name}: {env.event_data['text'][:120]}")
    await hub.close()


if __name__ == "__main__":
    asyncio.run(main())