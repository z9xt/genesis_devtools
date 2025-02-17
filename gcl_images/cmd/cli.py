#    Copyright 2025 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import click
import typing as tp
import tempfile
import shutil
import os

import gcl_images.constants as c
from gcl_images import utils
from gcl_images.builder.base import AbstractBuilder


@click.group(invoke_without_command=True)
def main():
    pass


@main.command("build", help="Build Genesis images")
@click.option("-b", "--base", default="ubuntu_24", help="Base image to use")
@click.option(
    "-d",
    "--driver",
    default="PackerBuilder",
    help="Image builder driver",
    show_default=True,
)
@click.option(
    "-o", "--output", default=None, help="Output directory", type=click.Path()
)
@click.argument("image_dirs", nargs=-1, type=click.Path())
def build_cmd(base: str, driver: str, output: str, image_dirs: tp.List[str]):
    if not image_dirs:
        raise click.UsageError("No image directories specified")

    # Load the image builder driver
    try:
        builder_class = utils.load_from_entry_point(
            c.EP_GCL_IMAGE_BUILDER_GROUP, driver
        )
        builder: AbstractBuilder = builder_class()
    except RuntimeError:
        raise click.ClickException(
            f"Invalid driver: {driver}, not found in entry points "
            f"{c.EP_GCL_IMAGE_BUILDER_GROUP}"
        )

    click.echo(click.style(f"Image builder driver: {driver}", fg="green"))

    # Build each image into a temporary directory
    for image_dir in image_dirs:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy all contents from image_dir to temp_dir
            for item in os.listdir(image_dir):
                s = os.path.join(image_dir, item)
                d = os.path.join(temp_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, False, None)
                else:
                    shutil.copy2(s, d)

            builder.run(temp_dir, base)
