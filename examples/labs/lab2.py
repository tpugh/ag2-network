import asyncio
from ag2 import Agent
from ag2.network import EV_TEXT, Hub
from ag2.network.testing import MemoryKnowledgeStore
from common import make_config

async def main():
    config = make_config()
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)
    a = await hub.register(Agent("optimist", prompt="You are an optimist.", config=config))
    b = await hub.register(Agent("skeptic", prompt="You are a skeptic.", config=config))
    c = await hub.register(Agent("pragmatist", prompt="You are a pragmatist.", config=config))
    channel = await a.open(type="discussion", target=["skeptic", "pragmatist"])
    await channel.send("Topic: microservices?", audience=[b.agent_id, c.agent_id])
    await asyncio.sleep(15)
    await channel.close(reason="done")
    await asyncio.sleep(1)
    wal = await hub.read_wal(channel.channel_id)
    for env in wal:
        if env.event_type == EV_TEXT:
            print(env.sender_id[-6:], env.event_data["text"][:60])
    await hub.close()
asyncio.run(main())