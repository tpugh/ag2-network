"""Example 01 — smallest end-to-end AG2 network.

One in-process hub, two agents, a `consulting` channel that auto-closes
after a single question/answer pair. Mirrors the official Quick Start.
"""
import asyncio

from ag2 import Agent
from ag2.network import EV_CHANNEL_CLOSED, EV_TEXT, Hub
from ag2.network.testing import MemoryKnowledgeStore

from common import make_config


async def main() -> None:
    config = make_config()

    # 1. Boot an in-process hub. The KnowledgeStore persists audit log,
    #    registry and write-ahead logs (here: in memory).
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)

    # 2. Register agents. hub.register attaches each Agent directly and
    #    returns an AgentClient whose agent_id is hub-stamped.
    alice = await hub.register(Agent("alice", prompt="Ask one focused question and stop.", config=config))
    bob = await hub.register(Agent("bob", prompt="Answer in one short sentence.", config=config))

    # 3. Open a consulting channel (strict 1Q1R; auto-closes on reply).
    channel = await alice.open(type="consulting", target="bob")

    # 4. Alice sends the question.
    await channel.send(
        "What's the single most important property of a distributed system?",
        audience=[bob.agent_id],
    )

    # 5. Wait for the adapter to close the channel after Bob's reply.
    close_env = await alice.wait_for_channel_event(
        channel_id=channel.channel_id,
        predicate=lambda e: e.event_type == EV_CHANNEL_CLOSED,
        timeout=120.0,
    )
    print(f"closed: {close_env.event_data.get('reason')!r}")

    # 6. Replay the conversation from the hub's write-ahead log.
    wal = await hub.read_wal(channel.channel_id)
    for env in wal:
        if env.event_type == EV_TEXT:
            speaker = "alice" if env.sender_id == alice.agent_id else "bob"
            print(f"{speaker}: {env.event_data['text']}")

    await hub.close()


if __name__ == "__main__":
    asyncio.run(main())