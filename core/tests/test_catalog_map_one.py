import asyncio

from catalog.map_one import build, run
from catalog.data import data_dir
from catalog.v1 import MappingV1
from catalog.v2 import MappingV2


def test_unknown_sku_exits_with_error_before_calling_the_model(capsys):
    assert asyncio.run(run("NO-SUCH-SKU", "v2", "mock")) == 1
    assert "not in the mock dataset" in capsys.readouterr().err


def test_build_picks_the_workflow_of_each_version():
    directory = data_dir("mock")
    assert isinstance(build("v1", directory, llm=None), MappingV1)
    assert isinstance(build("v2", directory, llm=None), MappingV2)
