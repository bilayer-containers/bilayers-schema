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


def test_display_only_has_no_interactive(schema):
    slots = schema["classes"]["TypeDisplayOnly"].get("slots", [])
    assert "interactive" not in slots


def test_parameter_has_interactive(schema):
    slots = schema["classes"]["TypeParameter"].get("slots", [])
    assert "interactive" in slots


def test_required_top_level_slots(schema):
    assert schema["slots"]["inputs"]["required"] is True
    assert schema["slots"]["outputs"]["required"] is True
    assert schema["slots"]["exec_function"]["required"] is True


def test_type_enum_has_expected_values(schema):
    values = schema["enums"]["TypeEnum"]["permissible_values"]
    for expected in ["image", "measurement", "checkbox", "dropdown", "radio", "textbox"]:
        assert expected in values


def test_config_has_required_top_level_keys(classical_segmentation_config):
    config = classical_segmentation_config
    assert "inputs" in config
    assert "outputs" in config
    assert "parameters" in config
    assert "exec_function" in config
    assert "docker_image" in config
    assert "citations" in config
    assert "algorithm_folder_name" in config


def test_input_image_type_has_image_fields(classical_segmentation_config):
    inputs = classical_segmentation_config["inputs"]
    image_input = next(i for i in inputs if i["type"] == "image")
    assert "subtype" in image_input
    assert "depth" in image_input
    assert "timepoints" in image_input
    assert "tiled" in image_input
    assert "pyramidal" in image_input


def test_radio_parameter_has_options(classical_segmentation_config):
    params = classical_segmentation_config["parameters"]
    radio_param = next(p for p in params if p["type"] == "radio")
    assert "options" in radio_param
    assert len(radio_param["options"]) > 0
