#!/usr/bin/env python

import os
import argparse
import subprocess
import shutil
from typing import Generator
from unittest.mock import patch

"""
Script to apply modules that have various third-party or patch dependencies.

Shell instructions like mkdir, rm, and git are run via subprocess instead of using
a dedicated Python module because I'm lazy.
"""


TEMP = "temp"
MODULES_FORMAT = "{}/modules"
THIRDPARTY_FORMAT = "{}/thirdparty"
PATCHES_FORMAT = "{}/patches"

APPLIED_MODULES_FILE = ".applied_modules"


def dir_exists(path: str) -> bool:
    return os.path.isdir(path)


def file_exists(path: str) -> bool:
    return os.path.isfile(path)


def list_dir(dir: str) -> Generator:
    for dir in os.listdir(os.fsencode(dir)):
        yield os.fsdecode(dir)


def get_godot_dir() -> str:
    return os.path.dirname(os.path.realpath(__file__))


def mkdir(abs_path: str) -> None:
    subprocess.run(["mkdir", abs_path])


def rm_rf(abs_path: str) -> None:
    subprocess.run(["rm", "-rf", abs_path])


def git_clone(dir: str, url: str) -> bool:
    if not dir_exists(dir):
        return False

    subprocess.run(["git", "clone", url], cwd=dir)

    return True


def git_restore_dir(dir: str) -> None:
    subprocess.run(["git", "restore", "."], cwd=dir)


def copy_dirs(from_dir: str, to_dir: str, force: bool) -> list:
    changed_files: list = []
    for dir in list_dir(from_dir):
        formatted_to: str = "{}/{}".format(to_dir, dir)
        shutil.copytree("{}/{}".format(from_dir, dir),
                        formatted_to, dirs_exist_ok=force)

        changed_files.append(formatted_to)

    return changed_files


def apply_patches(patches_dir: str, godot_dir: str) -> None:
    for file in list_dir(patches_dir):
        if not file.endswith("patch"):
            continue

        subprocess.run(
            ["git", "apply", "--ignore-space-change", "--ignore-whitespace", "{}/{}".format(patches_dir, file)], cwd=godot_dir)


def apply(args: argparse.Namespace) -> None:
    modules_file = args.modules_file
    if not file_exists(modules_file):
        raise Exception("path {} not found".format(modules_file))

    godot_dir = get_godot_dir()

    if not dir_exists(godot_dir):
        raise Exception("path {} not found".format(godot_dir))

    if shutil.which("git") is None:
        raise Exception("git command not found")

    temp_dir = "{}/{}".format(godot_dir, TEMP)

    # Always cleanup if there was an error from last time
    if dir_exists(temp_dir):
        rm_rf(temp_dir)

    mkdir(temp_dir)

    if not dir_exists(temp_dir):
        raise Exception(
            "Unable to create temp directory at {}".format(temp_dir))

    modules_file_handle = open(modules_file, "r")

    modules_file_content = modules_file_handle.read()
    for line in modules_file_content.splitlines():
        if line.startswith("#"):
            continue

        if not git_clone(temp_dir, line):
            raise Exception("Unable to clone {}".format(line))

    modules_file_handle.close()

    applied_files: list = []

    for dir in list_dir(temp_dir):
        repo_dir = "{}/{}".format(temp_dir, dir)

        modules_dir = MODULES_FORMAT.format(repo_dir)
        if dir_exists(modules_dir):
            applied_files.extend(copy_dirs(modules_dir, MODULES_FORMAT.format(
                godot_dir), force=args.force))

        thirdparty_dir = THIRDPARTY_FORMAT.format(repo_dir)
        if dir_exists(thirdparty_dir):
            applied_files.extend(copy_dirs(thirdparty_dir, THIRDPARTY_FORMAT.format(
                godot_dir), force=args.force))

        patches_dir = PATCHES_FORMAT.format(repo_dir)
        if dir_exists(patches_dir):
            apply_patches(patches_dir, godot_dir)

    rm_rf(temp_dir)

    applied_modules_handle = open(APPLIED_MODULES_FILE, "w")

    applied_modules_handle.writelines(applied_files)

    applied_modules_handle.close()


def clean(_args: argparse.Namespace) -> None:
    if not file_exists(APPLIED_MODULES_FILE):
        raise Exception("{} does not exist".format(APPLIED_MODULES_FILE))

    git_restore_dir(get_godot_dir())

    applied_modules_handle = open(APPLIED_MODULES_FILE, "r")

    applied_modules = applied_modules_handle.readlines()

    applied_modules_handle.close()

    for dir in applied_modules:
        if not dir_exists(dir):
            print("{} does not exist, skipping".format(dir))
            continue

        rm_rf(dir)

    rm_rf(APPLIED_MODULES_FILE)


def main():
    parser = argparse.ArgumentParser(
        description="Apply modules and patches to a Godot repo")
    subparsers = parser.add_subparsers()

    apply_parser = subparsers.add_parser("apply", help="Apply modules")
    apply_parser.add_argument("--modules-file", type=str, default="modules_file.txt",
                              help="Path to a file containing paths to module repos")
    apply_parser.add_argument("--force", "-f", type=bool, default=False,
                              help="Whether to overwrite any existing modules or thirdparty files")
    apply_parser.set_defaults(func=apply)

    clean_parser = subparsers.add_parser(
        "clean", help="Clean up applied modules")
    clean_parser.set_defaults(func=clean)

    args = parser.parse_args()

    if not "func" in args:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
