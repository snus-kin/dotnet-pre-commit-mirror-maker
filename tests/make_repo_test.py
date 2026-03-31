from __future__ import annotations

import subprocess
from unittest import mock

import pytest
import yaml

from dotnet_pre_commit_mirror_maker.languages import LIST_VERSIONS
from dotnet_pre_commit_mirror_maker.make_repo import (
    _commit_version,
    format_files,
    make_repo,
)


def _cmd(*cmd):
    return subprocess.check_output(cmd).strip().decode()


def test_format_files(tmpdir):
    src = tmpdir.join("src").ensure_dir()
    dest = tmpdir.join("dest").ensure_dir()

    src.join("file1.txt").write("{foo} bar {baz}")
    src.join("file2.txt").write("hello world")
    src.join("file3.txt").write("foo bar {baz}")

    format_files(src, dest, foo="herp", baz="derp")

    assert dest.join("file1.txt").read() == "herp bar derp"
    assert dest.join("file2.txt").read() == "hello world"
    assert dest.join("file3.txt").read() == "foo bar derp"


def test_skips_directories(tmpdir):
    src = tmpdir.join("src").ensure_dir()
    dest = tmpdir.join("dest").ensure_dir()

    src.join("__pycache__").ensure_dir()
    src.join("file.txt").write("hello")

    format_files(src, dest)

    assert dest.join("file.txt").read() == "hello"


@pytest.fixture
def in_git_dir(tmpdir):
    git_path = tmpdir.join("gits")
    subprocess.check_call(("git", "init", git_path))
    with git_path.as_cwd():
        yield git_path


def test_commit_version(in_git_dir):
    _commit_version(
        ".",
        version="1.0.0",
        language="dotnet",
        name="csharpier",
        description="",
        entry="csharpier",
        id="csharpier",
        match_key="files",
        match_val=r"\.cs$",
        args="[]",
        additional_dependencies="[]",
        require_serial="false",
        minimum_pre_commit_version="0",
    )

    # Assert that our things got copied over
    assert in_git_dir.join(".pre-commit-hooks.yaml").exists()
    # Assert that we set the version file correctly
    assert in_git_dir.join(".version").read().strip() == "1.0.0"

    # Assert some things about the gits
    assert _cmd("git", "status", "-s") == ""
    assert _cmd("git", "tag", "-l") == "v1.0.0"
    assert _cmd("git", "log", "--oneline").split()[1:] == ["Mirror:", "1.0.0"]


def test_arguments(in_git_dir):
    _commit_version(
        ".",
        version="0.29.2",
        language="dotnet",
        name="csharpier",
        description="An opinionated code formatter for C#.",
        entry="csharpier",
        id="csharpier",
        match_key="files",
        match_val=r"\.cs$",
        args="[]",
        additional_dependencies='["csharpier:0.29.2"]',
        require_serial="false",
        minimum_pre_commit_version="0",
    )
    contents = in_git_dir.join(".pre-commit-hooks.yaml").read()
    assert yaml.safe_load(contents) == [
        {
            "id": "csharpier",
            "name": "csharpier",
            "description": "An opinionated code formatter for C#.",
            "entry": "csharpier",
            "language": "dotnet",
            "files": r"\.cs$",
            "args": [],
            "require_serial": False,
            "additional_dependencies": ["csharpier:0.29.2"],
            "minimum_pre_commit_version": "0",
        }
    ]


@pytest.fixture
def fake_versions():
    fns = {"dotnet": lambda _: ("0.29.0", "0.29.1", "0.29.2")}
    with mock.patch.dict(LIST_VERSIONS, fns):
        yield


def test_make_repo_starting_empty(in_git_dir, fake_versions):
    make_repo(
        ".",
        language="dotnet",
        name="csharpier",
        description="",
        entry="csharpier",
        id="csharpier",
        match_key="files",
        match_val=r"\.cs$",
        args="[]",
        require_serial="false",
        minimum_pre_commit_version="0",
    )

    # Assert that our things got copied over
    assert in_git_dir.join(".pre-commit-hooks.yaml").exists()
    # Assert that we set the version file correctly
    assert in_git_dir.join(".version").read().strip() == "0.29.2"

    # Assert some things about the gits
    assert _cmd("git", "status", "--short") == ""
    expected = ["v0.29.0", "v0.29.1", "v0.29.2"]
    assert _cmd("git", "tag", "-l").split() == expected
    log_lines = _cmd("git", "log", "--oneline").splitlines()
    log_lines_split = [log_line.split() for log_line in log_lines]
    assert log_lines_split == [
        [mock.ANY, "Mirror:", "0.29.2"],
        [mock.ANY, "Mirror:", "0.29.1"],
        [mock.ANY, "Mirror:", "0.29.0"],
    ]


def test_make_repo_starting_at_version(in_git_dir, fake_versions):
    # Write a version file (as if we've already run this before)
    in_git_dir.join(".version").write("0.29.0")
    # make sure this is gone afterwards
    in_git_dir.join("hooks.yaml").ensure()

    make_repo(
        ".",
        language="dotnet",
        name="csharpier",
        description="",
        entry="csharpier",
        id="csharpier",
        match_key="files",
        match_val=r"\.cs$",
        args="[]",
        require_serial="false",
        minimum_pre_commit_version="0",
    )

    assert not in_git_dir.join("hooks.yaml").exists()

    # Assert that we only got tags / commits for the stuff we added
    assert _cmd("git", "tag", "-l").split() == ["v0.29.1", "v0.29.2"]
    log_lines = _cmd("git", "log", "--oneline").splitlines()
    log_lines_split = [log_line.split() for log_line in log_lines]
    assert log_lines_split == [
        [mock.ANY, "Mirror:", "0.29.2"],
        [mock.ANY, "Mirror:", "0.29.1"],
    ]


def test_dotnet_integration(in_git_dir):
    make_repo(
        ".",
        language="dotnet",
        name="csharpier",
        description="",
        entry="csharpier",
        id="csharpier",
        match_key="files",
        match_val=r"\.cs$",
        args="[]",
        require_serial="false",
        minimum_pre_commit_version="0",
    )
    # Our files should exist
    assert in_git_dir.join(".version").exists()
    assert in_git_dir.join(".pre-commit-hooks.yaml").exists()

    # Should have made _some_ tags
    assert _cmd("git", "tag", "-l")
    # Should have made _some_ commits
    assert _cmd("git", "log", "--oneline")
