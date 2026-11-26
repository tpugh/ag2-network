"""Example 02 — free-form two-party conversation.

`conversation` adapter: exactly 2 participants, free turn order, explicit
close (or TTL)."""
import asyncio

from ag2 import Agent
from ag2.network import EV_CHANNEL_CLOSED, EV_TEXT, Hub
from ag2.network.testing import MemoryKnowledgeStore

from common import make_config


async def main() -> None:
    config = make_config()
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)
    alice = await hub.register(Agent("alice", prompt="You are curious and ask follow-ups.", config=config))
    bob = await hub.register(Agent("bob", prompt="You answer helpfully and concisely.", config=config))

    channel = await alice.open(type="conversation", target="bob")
    await channel.send("Hi Bob, what makes a good API design?", audience=[bob.agent_id])

    # Wait for Bob's reply, then Alice follows up, then close.
    await alice.wait_for_channel_event(
        channel_id=channel.channel_id,
        predicate=lambda e: e.event_type == EV_TEXT and e.sender_id == bob.agent_id,
        timeout=120.0,
    )
    await channel.send("Thanks — can you give one concrete example?", audience=[bob.agent_id])
    await alice.wait_for_channel_event(
        channel_id=channel.channel_id,
        predicate=lambda e: e.event_type == EV_TEXT and e.sender_id == bob.agent_id,
        timeout=120.0,
    )

    await channel.close(reason="done")
    # allow close to propagate
    await asyncio.sleep(0.5)

    wal = await hub.read_wal(channel.channel_id)
    for env in wal:
        if env.event_type == EV_TEXT:
            speaker = "alice" if env.sender_id == alice.agent_id else "bob"
            print(f"{speaker}: {env.event_data['text']}")
    await hub.close()


if __name__ == "__main__":
    asyncio.run(main())