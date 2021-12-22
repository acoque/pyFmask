# Copyright 2021 Arthur Coqué
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains various useful functions and classes."""

from pathlib import Path

import click
import yaml

root = Path(__file__).parent.resolve()


def load_config():
    with open(root / 'config.yaml', 'r') as f:
        config = yaml.full_load(f)
    for key, val in config.items():
        config[key] = str(Path(val).expanduser())
    return config


def update_config(config, key, val):
    config[key] = val
    with open(root / 'config.yaml', 'w') as f:
        print(root, config)
        yaml.dump(config, f)


class PathPath(click.Path):
    """A Click path argument that returns a pathlib Path, not a string."""
    def convert(self, value, param, ctx):
        return Path(super().convert(value, param, ctx))
