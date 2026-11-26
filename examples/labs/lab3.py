import asyncio
from ag2 import Agent
from ag2.network import Hub, TransitionGraph
from ag2.network.testing import MemoryKnowledgeStore
from common import make_config

async def main():
    config = make_config()
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)
    triage = await hub.register(Agent("triage", prompt="Triage the request; route to eng if technical.", config=config))
    eng = await hub.register(Agent("eng", prompt="Engineering specialist. One sentence.", config=config))
    graph = TransitionGraph.sequence([triage.agent_id, eng.agent_id])
    channel = await triage.open(type="workflow", target=[eng.agent_id],
        knobs={"graph": graph.to_dict()})
    await channel.send("The API is returning 500s.", audience=[eng.agent_id])
    await asyncio.sleep(20)
    await hub.close()
asyncio.run(main())