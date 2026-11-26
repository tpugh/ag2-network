"""Example 04 — declarative workflow (pipeline).

`workflow` adapter driven by a `TransitionGraph`. Uses the `sequence`
convenience factory: alice -> bob -> carol -> terminate.
"""
import asyncio

from ag2 import Agent
from ag2.network import EV_CHANNEL_CLOSED, EV_TEXT, Hub, TransitionGraph
from ag2.network.testing import MemoryKnowledgeStore

from common import make_config


async def main() -> None:
    config = make_config()
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)
    alice = await hub.register(Agent("alice", prompt="You are step 1: restate the problem.", config=config))
    bob = await hub.register(Agent("bob", prompt="You are step 2: propose a solution.", config=config))
    carol = await hub.register(Agent("carol", prompt="You are step 3: critique the solution.", config=config))

    graph = TransitionGraph.sequence([alice.agent_id, bob.agent_id, carol.agent_id])

    channel = await alice.open(
        type="workflow",
        target=[bob.agent_id, carol.agent_id],
        knobs={"graph": graph.to_dict()},
    )
    await channel.send("Design a rate limiter for an API.", audience=[bob.agent_id, carol.agent_id])

    # Wait for the graph to terminate the channel.
    close_env = await alice.wait_for_channel_event(
        channel_id=channel.channel_id,
        predicate=lambda e: e.event_type == EV_CHANNEL_CLOSED,
        timeout=180.0,
    )
    print("closed:", close_env.event_data.get("reason"))

    wal = await hub.read_wal(channel.channel_id)
    for env in wal:
        if env.event_type == EV_TEXT:
            aid = env.sender_id
            name = "alice" if aid == alice.agent_id else ("bob" if aid == bob.agent_id else "carol")
            print(f"{name}: {env.event_data['text'][:150]}")
    await hub.close()


if __name__ == "__main__":
    asyncio.run(main())