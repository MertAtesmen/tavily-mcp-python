import asyncio

from .server import run_server


def run_sse() -> None:
    asyncio.run(run_server('sse'))

def run_stdio() -> None:
    asyncio.run(run_server('stdio'))

if __name__ == '__main__':
    run_sse()
