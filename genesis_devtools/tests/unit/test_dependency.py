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
import os
import shutil
import typing as tp

from genesis_devtools.builder import dependency as deps


class TestDependency:

    def test_local_path_from_config(
        self, build_config: tp.Dict[str, tp.Any]
    ) -> None:
        work_dir = "/tmp/work_dir"
        dep = deps.LocalPathDependency.from_config(
            build_config["deps"][0],
            work_dir,
        )

        assert dep.img_dest == "/opt/genesis_core"
        assert dep._path == "/tmp/genesis_core_test_dir"
        assert dep.local_path is None

    def test_local_path_fetch(
        self, build_config: tp.Dict[str, tp.Any]
    ) -> None:
        os.makedirs("/tmp/genesis_core_test_dir", exist_ok=True)

        dep = deps.LocalPathDependency.from_config(
            build_config["deps"][0],
            "/tmp",
        )

        os.makedirs("/tmp/___deps_dir", exist_ok=True)
        dep.fetch("/tmp/___deps_dir")

        try:
            assert os.path.exists("/tmp/___deps_dir/genesis_core_test_dir")
        finally:
            shutil.rmtree("/tmp/genesis_core_test_dir")
            shutil.rmtree("/tmp/___deps_dir")

    def test_local_path_fetch_with_exclude(
        self, build_config: tp.Dict[str, tp.Any]
    ) -> None:

        # aliases block
        def join_path(*parts):
            return os.path.join(*parts)

        def make_dir(*parts):
            os.makedirs(join_path(*parts), exist_ok=True)

        def write_file(path, content):
            with open(path, "w") as f:
                f.write(content)

        def exists(*parts):
            return os.path.exists(join_path(*parts))

        def not_exists(*parts):
            return not os.path.exists(join_path(*parts))

        # Test directory structure
        src_dir = "/tmp/genesis_core_test_dir"
        make_dir(src_dir)

        # Folder structure
        make_dir(src_dir, "build1")
        make_dir(src_dir, "build2")
        make_dir(src_dir, "build3", "build2")  # build2 inside build3
        make_dir(src_dir, "nested", "build2")

        write_file(join_path(src_dir, "build1", "file1.txt"), "include build1")
        write_file(join_path(src_dir, "build2", "file2.txt"), "exclude build2")
        write_file(join_path(src_dir, "build3", "file3.txt"), "include build3")
        write_file(
            join_path(
                src_dir, "build3", "build2", "file_in_build3_build2.txt"
            ),
            "include nested build2 in build3",
        )
        write_file(
            join_path(src_dir, "nested", "build2", "file_nested.txt"),
            "exclude nested/build2",
        )

        # Multiple exclude by pattern test
        make_dir(src_dir, "files")
        write_file(join_path(src_dir, "files", "file1.test"), "to delete")
        write_file(join_path(src_dir, "files", "file2.test"), "to delete")
        write_file(join_path(src_dir, "files", "file3.test"), "to delete")
        write_file(join_path(src_dir, "files", "life.test"), "to keep")

        # Exclude config
        dep_config = dict(build_config["deps"][0])
        dep_config["exclude"] = [
            "build2",  # exclude 1-lvl build2 folder
            "nested/build2",  # exclude 2-lvl nested/build2
            "/files/file*",  # exclude all file*.test
        ]

        dep = deps.LocalPathDependency.from_config(dep_config, "/tmp")

        target_dir = "/tmp/deps_dir_exclude_test"
        make_dir(target_dir)

        dep.fetch(target_dir)

        try:
            base_target = join_path(target_dir, "genesis_core_test_dir")

            # Checks
            assert exists(base_target, "build1", "file1.txt")
            assert not_exists(base_target, "build2")
            assert exists(
                base_target, "build3", "build2", "file_in_build3_build2.txt"
            )
            assert not_exists(base_target, "nested", "build2")
            assert exists(base_target, "files")
            assert exists(base_target, "files", "life.test")
            assert not_exists(base_target, "files", "file1.test")
            assert not_exists(base_target, "files", "file2.test")
            assert not_exists(base_target, "files", "file3.test")

        finally:
            shutil.rmtree(src_dir)
            shutil.rmtree(target_dir)

    def test_http_fetch(self, build_config: tp.Dict[str, tp.Any]) -> None:
        dep = deps.HttpDependency.from_config(
            build_config["deps"][1],
            "/tmp",
        )

        os.makedirs("/tmp/___deps_dir", exist_ok=True)
        dep.fetch("/tmp/___deps_dir")

        try:
            assert os.path.exists("/tmp/___deps_dir/undionly.kpxe")
        finally:
            shutil.rmtree("/tmp/___deps_dir")

    def test_git_from_config(
        self, build_git_config: tp.Dict[str, tp.Any]
    ) -> None:
        work_dir = "/tmp/work_dir"
        dep = deps.GitDependency.from_config(
            build_git_config["deps"][0],
            work_dir,
        )

        assert dep.img_dest == "/opt/genesis_templates"
        assert (
            dep._repo_url
            == "https://github.com/infraguys/genesis_templates.git"
        )
        assert dep.local_path is None

    def test_git_fetch(self, build_git_config: tp.Dict[str, tp.Any]) -> None:
        dep = deps.GitDependency.from_config(
            build_git_config["deps"][0],
            "/tmp",
        )

        os.makedirs("/tmp/___deps_dir", exist_ok=True)
        dep.fetch("/tmp/___deps_dir")

        try:
            assert os.path.exists("/tmp/___deps_dir/genesis_templates")
        finally:
            shutil.rmtree("/tmp/___deps_dir")

    def test_env_path_from_config(
        self, build_env_config: tp.Dict[str, tp.Any]
    ) -> None:
        work_dir = "/tmp/work_dir"
        dep = deps.LocalEnvPathDependency.from_config(
            build_env_config["deps"][0],
            work_dir,
        )

        assert dep.img_dest == "/opt/genesis_devtools"
        assert dep._env_path == "PATH_FROM_ENV"
        assert dep.local_path is None

    def test_env_path_fetch(
        self, build_env_config: tp.Dict[str, tp.Any]
    ) -> None:
        os.makedirs("/tmp/genesis_core_test_dir", exist_ok=True)
        os.environ["PATH_FROM_ENV"] = "/tmp/genesis_core_test_dir"

        dep = deps.LocalEnvPathDependency.from_config(
            build_env_config["deps"][0],
            "/tmp",
        )

        os.makedirs("/tmp/___deps_dir", exist_ok=True)
        dep.fetch("/tmp/___deps_dir")

        try:
            assert os.path.exists("/tmp/___deps_dir/genesis_core_test_dir")
        finally:
            shutil.rmtree("/tmp/genesis_core_test_dir")
            shutil.rmtree("/tmp/___deps_dir")
