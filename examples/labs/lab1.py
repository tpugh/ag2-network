import asyncio
from ag2 import Agent
from ag2.network import EV_CHANNEL_CLOSED, EV_TEXT, Hub
from ag2.network.testing import MemoryKnowledgeStore
from common import make_config

async def main():
    config = make_config()
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)
    alice = await hub.register(Agent("alice", prompt="Ask: what is 2+2?", config=config))
    bob = await hub.register(Agent("bob", prompt="Answer in one word.", config=config))
    channel = await alice.open(type="consulting", target="bob")
    await channel.send("What is 2+2?", audience=[bob.agent_id])
    close_env = await alice.wait_for_channel_event(channel_id=channel.channel_id,
        predicate=lambda e: e.event_type == EV_CHANNEL_CLOSED, timeout=60.0)
    print("closed:", close_env.event_data.get("reason"))
    await hub.close()
asyncio.run(main())