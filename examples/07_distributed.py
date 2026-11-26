"""Example 07 — distributed deployment (single machine, two processes simulated).

Runs a hub server and a remote agent in the same process via asyncio to
demonstrate WsLink. For real deployments, split these into separate
processes/machines.
"""
import asyncio

from ag2 import Agent
from ag2.network import EV_TEXT, Hub, HubClient, WsLink, serve_ws
from ag2.network.testing import MemoryKnowledgeStore

from common import make_config


async def hub_server(ready: asyncio.Event, port_box: dict) -> None:
    hub = await Hub.open(MemoryKnowledgeStore())
    async with serve_ws(hub, "127.0.0.1", 0, allow_unauthenticated=True) as server:
        port = server.sockets[0].getsockname()[1]
        port_box["port"] = port
        ready.set()
        with __import__("contextlib").suppress(asyncio.CancelledError):
            await asyncio.Future()
        await hub.close()


async def remote_agent(port: int) -> None:
    config = make_config()
    hc = HubClient(WsLink(f"ws://127.0.0.1:{port}"))
    await hc.open()
    agent = Agent("bob", prompt="Answer in one short sentence.", config=config)
    bob = await hc.register(agent)
    print("remote bob registered:", bob.agent_id)
    await asyncio.Future()  # stay connected
    await hc.close()


async def main() -> None:
    ready = asyncio.Event()
    port_box: dict = {}
    server_task = asyncio.create_task(hub_server(ready, port_box))
    await ready.wait()
    port = port_box["port"]
    print("hub listening on", port)

    # connect an in-process coordinator via WsLink too
    config = make_config()
    hc = HubClient(WsLink(f"ws://127.0.0.1:{port}"))
    await hc.open()
    alice = await hc.register(Agent("alice", prompt="coordinator", config=config))

    # start remote bob
    bob_task = asyncio.create_task(remote_agent(port))
    await asyncio.sleep(2)

    channel = await alice.open(type="consulting", target="bob")
    await channel.send("What is 2 + 2?")

    await asyncio.sleep(5)
    await hc.close()
    bob_task.cancel()
    server_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())