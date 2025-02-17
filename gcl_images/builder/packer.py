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

import subprocess
import typing as tp
import shutil
from importlib.resources import files

from gcl_images.builder.base import DummyBuilder
from gcl_images import constants as c


def _get_base_files(base: str) -> str:
    """Get base files for the image."""
    base_files = []
    for bfile in files(f"{c.PKG_NAME}.packer.{base}").iterdir():
        base_files.append(bfile)

    return base_files


class PackerBuilder(DummyBuilder):
    """Packer image builder.

    Packer image builder that uses Packer tools to build images.
    """

    def pre_build(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Actions to prepare the environment for building the image."""
        # Copy base files to image_dir if base is not None
        if base is not None:
            base_files = _get_base_files(base)
            for bfile in base_files:
                shutil.copy(bfile, image_dir)

        subprocess.run(["packer", "init", image_dir], check=True)

    def build(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Actions to build the image."""
        subprocess.run(
            ["packer", "build", "-parallel-builds=1", image_dir], check=True
        )
