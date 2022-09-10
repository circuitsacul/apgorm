from __future__ import annotations

import asyncio
from typing import Generator

import pytest


@pytest.fixture(scope="package")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
