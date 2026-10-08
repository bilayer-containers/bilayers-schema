"""Structural check for the secret/default rules in schema.yaml.

The behaviour (a secret with a default is rejected, a non-secret without one is
rejected) needs the LinkML validator and a full config, so it is tested in
bilayers/tests/test_config/test_secret_validation.py.
"""


def test_rules_are_declared_on_the_shared_base_class(schema) -> None:
    # Declared on AbstractUserInterface so `parameters` and `display_only` both inherit them
    descriptions = [rule["description"] for rule in schema["classes"]["AbstractUserInterface"]["rules"]]
    assert "A secret must not have a default" in descriptions
    assert "Default value is required for every type except secret" in descriptions
