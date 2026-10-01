from catalog.data import NO_DATA, channel_attributes, data_dir, find_product, load_cases, load_schemas

REAL = data_dir("real")
MOCK = data_dir("mock")


def test_load_cases_reads_both_datasets():
    assert len(load_cases(REAL)) == 30
    assert len(load_cases(MOCK)) == 10


def test_real_schemas_have_names_from_reference_category():
    schemas = load_schemas(REAL)
    assert "urn:category:102273:vendor:shopee" in schemas
    assert all(s["name"] for s in schemas.values())


def test_mock_schema_is_the_single_calotas_category():
    schemas = load_schemas(MOCK)
    assert list(schemas) == ["urn:category:102529:vendor:shopee"]
    assert schemas["urn:category:102529:vendor:shopee"]["name"] == "Calotas"


def test_channel_attributes_by_urn_and_empty_for_unknown_category():
    schemas = load_schemas(MOCK)
    attrs = channel_attributes(schemas, "urn:category:102529:vendor:shopee")
    assert attrs["urn:attribute:101638:vendor:shopee"]["mandatory"] is True
    assert channel_attributes(schemas, "urn:category:999:vendor:shopee") == {}
    assert channel_attributes(schemas, None) == {}


def test_find_product_normalizes_the_sku_and_searches_in_order():
    sku = load_cases(REAL)[0]["product"]["sku"]
    product, directory = find_product(f"  {sku} ", [REAL, MOCK])
    assert product["sku"] == sku and directory == REAL
    assert find_product(int(sku) if str(sku).isdigit() else sku, [REAL, MOCK]) is not None
    assert find_product("does-not-exist", [REAL, MOCK]) is None


def test_no_data_values():
    assert NO_DATA == frozenset({"-1", "N/A", ""})
