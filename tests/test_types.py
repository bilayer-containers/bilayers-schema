"""Keep schema.yaml and types.py in sync.

The LinkML schema (schema.yaml) is the source of truth for validation; the
TypedDicts in types.py are the Python-side mirror used by bilayers/targets.
These tests fail loudly if the two drift apart.

  T1 - every mapped LinkML class has exactly the same field set as its TypedDict
  T2 - every TypedDict and every concrete LinkML class is accounted for
       (either mapped, or on an explicit allowlist) so the mapping can't go stale
  T3 - schema.yaml compiles as valid LinkML
"""

from importlib.resources import files
from typing import get_type_hints

import pytest
from linkml_runtime import SchemaView

import bilayers_schema.types as bt

SCHEMA_PATH = str(files("bilayers_schema").joinpath("schema.yaml"))


@pytest.fixture(scope="module")
def sv() -> SchemaView:
    return SchemaView(SCHEMA_PATH)


# LinkML class name -> its types.py TypedDict counterpart.
MAPPING = {
    "SpecContainer": bt.Config,
    "TypeInput": bt.Input,
    "TypeOutput": bt.Output,
    "TypeParameter": bt.Parameter,
    "TypeDisplayOnly": bt.DisplayOnly,
    "ExecFunction": bt.ExecFunction,
    "DockerImage": bt.DockerImage,
    "TypeCitations": bt.Citations,
    "HiddenArgs": bt.HiddenArgs,
}

# LinkML classes intentionally without a TypedDict counterpart.
SCHEMA_ONLY = {
    "Any",                       # utility class
    "RadioOptions",              # modeled loosely as list[dict[str, str]] in `options`
    "AbstractWorkflowDetails",   # abstract base, flattened into Type{Input,Output}
    "AbstractUserInterface",     # abstract base, flattened into Type{Parameter,DisplayOnly}
}

# TypedDicts intentionally without a LinkML counterpart.
TYPES_ONLY = {
    "InputOutputBase",  # shared base for Input/Output (mirrors AbstractWorkflowDetails)
    "InterfaceInput",   # runtime payload (output_dir, cli_sequence) - not part of the spec
}


def linkml_fields(sv: SchemaView, class_name: str) -> set:
    """Effective field names for a LinkML class, including inherited slots/attributes."""
    return {s.name for s in sv.class_induced_slots(class_name)}


def typeddict_fields(td) -> set:
    """All keys of a TypedDict, including inherited ones."""
    return set(get_type_hints(td).keys())


def all_typeddicts() -> dict:
    """Every TypedDict defined in types.py, keyed by class name."""
    return {
        name: obj
        for name in dir(bt)
        if isinstance(obj := getattr(bt, name), type)
        and hasattr(obj, "__required_keys__")  # marks a TypedDict
        and obj.__module__ == bt.__name__
    }


# --- T1: field parity ---------------------------------------------------------


@pytest.mark.parametrize("linkml_class, td", list(MAPPING.items()), ids=list(MAPPING))
def test_schema_types_field_parity(sv: SchemaView, linkml_class: str, td) -> None:
    schema_fields = linkml_fields(sv, linkml_class)
    type_fields = typeddict_fields(td)

    missing_in_types = schema_fields - type_fields
    extra_in_types = type_fields - schema_fields

    assert not missing_in_types and not extra_in_types, (
        f"{linkml_class} <-> {td.__name__} field mismatch:\n"
        f"  in schema.yaml but missing from {td.__name__}: {sorted(missing_in_types)}\n"
        f"  in {td.__name__} but missing from schema.yaml: {sorted(extra_in_types)}"
    )


# --- T2: completeness guard ---------------------------------------------------


def test_every_typeddict_is_accounted_for() -> None:
    mapped = {td.__name__ for td in MAPPING.values()}
    unaccounted = set(all_typeddicts()) - mapped - TYPES_ONLY
    assert not unaccounted, (
        f"TypedDicts in types.py not in MAPPING or TYPES_ONLY: {sorted(unaccounted)}. "
        "Add a mapping (and matching LinkML class) or allowlist it in TYPES_ONLY."
    )


def test_every_concrete_class_is_accounted_for(sv: SchemaView) -> None:
    defined = set(sv.all_classes(imports=False))
    unaccounted = defined - set(MAPPING) - SCHEMA_ONLY
    assert not unaccounted, (
        f"LinkML classes in schema.yaml not in MAPPING or SCHEMA_ONLY: {sorted(unaccounted)}. "
        "Add a mapping (and matching TypedDict) or allowlist it in SCHEMA_ONLY."
    )


# --- T3: schema compiles as valid LinkML --------------------------------------


def test_schema_compiles_as_valid_linkml(sv: SchemaView) -> None:
    assert sv.all_classes(imports=False), "schema defines no classes"
    assert sv.all_slots(imports=False), "schema defines no slots"
    # induced-slot resolution raises if a class/slot/range is malformed
    for name, cls in sv.all_classes(imports=False).items():
        if not cls.abstract:
            sv.class_induced_slots(name)
