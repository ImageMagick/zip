#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Tools"))

from dependency_updater import Step, Updater

URL = "https://github.com/nih-at/libzip/archive/refs/tags/v{version}.tar.gz"


def update_source(updater):
    updater.replace_source()
    updater.remove(".github")
    updater.update_config()


def create_generated_files(updater):
    zlib_dir = updater.dependency_dir.parent / "zlib"
    updater.cmake(
        f"-DZLIB_INCLUDE_DIR:PATH={zlib_dir.as_posix()}",
        f"-DZLIB_LIBRARY:FILEPATH={(zlib_dir / 'foo.lib').as_posix()}",
        "-DLZMA_WINDOW_LIMIT=UINT64_MAX",
        "-DBUILD_SHARED_LIBS=false")
    updater.cmake_script(
        updater.dependency_dir / "cmake/GenerateZipErrorStrings.cmake",
        f"-DPROJECT_SOURCE_DIR={updater.dependency_dir.as_posix()}")
    updater.copy_from_build("", ["config.h", "zipconf.h"], "lib")
    updater.copy("zip_err_str.c", "lib/zip_err_str.c")
    updater.remove("zip_err_str.c")
    updater.remove_build()


def apply_patches(updater):
    updater.apply_patches()


updater = Updater(__file__, "libzip", URL)
updater.run([
    Step("Replace the source with the release and update Config.txt", update_source,
        "Updated libzip to {version}"),
    Step("Use cmake to generate the files", create_generated_files,
        "Added files that were generated with cmake."),
    Step("Apply the patches", apply_patches, "Changes to libzip."),
    updater.clone_dependencies_step(),
])
