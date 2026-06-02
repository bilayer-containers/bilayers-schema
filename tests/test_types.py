def test_schema_loads():
    from bilayers_schema import schema
    assert isinstance(schema, dict)

def test_print_schema_yaml(capsys):
    from bilayers_schema import print_schema
    print_schema(as_yaml=True)
    assert "TypeInput" in capsys.readouterr().out

def test_print_schema_pprint(capsys):
    from bilayers_schema import print_schema
    print_schema(as_yaml=False)
    assert "TypeInput" in capsys.readouterr().out
