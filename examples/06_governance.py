"""Example 06 — governance: Rule + audit log.

Sets a per-agent Rule restricting channel types, then reads the hub's
audit log to see what happened.
"""
import asyncio

from ag2 import Agent
from ag2.network import Hub
from ag2.network.rule import AccessBlock, LimitsBlock, Rule
from ag2.network.testing import MemoryKnowledgeStore

from common import make_config


async def main() -> None:
    config = make_config()
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)
    alice = await hub.register(Agent("alice", prompt="hi", config=config))
    bob = await hub.register(Agent("bob", prompt="hi", config=config))

    # Restrict bob: only consulting channels allowed outbound.
    rule = Rule(access=AccessBlock(channel_types=[]), limits=LimitsBlock())
    await hub.set_rule(bob.agent_id, rule)
    print("rule set for bob:", (await hub.get_rule(bob.agent_id)).to_dict())

    # Audit log captures registration + rule set.
    entries = await hub.audit_log.read_all()
    print("audit entries:", len(entries))
    for e in entries[-5:]:
        print(" -", e.get("kind") if isinstance(e, dict) else e)

    await hub.close()


if __name__ == "__main__":
    asyncio.run(main())