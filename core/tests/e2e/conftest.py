import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_E2E") == "1":
        return
    skip = pytest.mark.skip(reason="e2e: set RUN_E2E=1 (scripts/e2e.sh)")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip)
