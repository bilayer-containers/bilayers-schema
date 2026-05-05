
from importlib.resources import files
from pprint import pprint

import yaml


with files("bilayers_schema").joinpath("schema.yaml").open("r") as f:
    schema = yaml.safe_load(f)


def print_schema(as_yaml=True):
    if as_yaml:
        print(yaml.dump(schema, sort_keys=False))
    else:
        pprint(schema)