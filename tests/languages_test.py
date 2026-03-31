from __future__ import annotations

from dotnet_pre_commit_mirror_maker.languages import dotnet_get_package_versions


def assert_all_text(versions):
    for version in versions:
        assert type(version) is str


def test_dotnet_get_package_version_output():
    ret = dotnet_get_package_versions("csharpier")
    assert ret
    assert_all_text(ret)
