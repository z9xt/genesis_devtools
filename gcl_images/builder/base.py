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

import abc
import typing as tp


class AbstractBuilder(abc.ABC):
    """Abstract image builder.

    This class defines the interface for building images.
    """

    @abc.abstractmethod
    def pre_build(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Actions to prepare the environment for building the image."""

    @abc.abstractmethod
    def build(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Actions to build the image."""

    @abc.abstractmethod
    def post_build(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Actions to perform after building the image."""

    def run(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Run the image builder."""
        self.pre_build(image_dir, base)
        self.build(image_dir, base)
        self.post_build(image_dir, base)


class DummyBuilder(AbstractBuilder):
    """Dummy image builder.

    Dummy builder that does nothing.
    """

    def pre_build(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Actions to prepare the environment for building the image."""
        return None

    def build(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Actions to build the image."""
        return None

    def post_build(self, image_dir: str, base: tp.Optional[str]) -> None:
        """Actions to perform after building the image."""
        return None
