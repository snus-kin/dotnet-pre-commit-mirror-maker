from __future__ import annotations

import json
import urllib.request


def dotnet_get_package_versions(package_name: str) -> list[str]:
    """Get all versions of a .NET tool from NuGet."""
    # NuGet V3 API - get package versions
    package_name_lower = package_name.lower()
    url = f"https://api.nuget.org/v3-flatcontainer/{package_name_lower}/index.json"
    resp = json.load(urllib.request.urlopen(url))
    versions_list = resp.get("versions", [])
    # Filter out pre-release versions (those containing '-')
    stable_versions = [v for v in versions_list if "-" not in v]
    # Return stable versions if available, otherwise all versions
    return stable_versions if stable_versions else versions_list


def dotnet_get_additional_dependencies(
    package_name: str,
    package_version: str,
) -> list[str]:
    """Return additional dependencies for dotnet tools."""
    return [f"{package_name}:{package_version}"]


LIST_VERSIONS = {
    "dotnet": dotnet_get_package_versions,
}

ADDITIONAL_DEPENDENCIES = {
    "dotnet": dotnet_get_additional_dependencies,
}
