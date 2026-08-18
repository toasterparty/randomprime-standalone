from importlib import metadata

__all__ = ["DESCRIPTION", "DIST_NAME", "PRODUCT_NAME", "VERSION"]

# The user-facing name, in the window title and the Windows version resource.
# pyproject.toml owns the distribution name; tools/release.sh reads this one.
PRODUCT_NAME = "Randomprime Standalone"


def _distribution() -> tuple[str, str, str]:
    try:
        meta = metadata.metadata(__name__)
        return meta["Name"], meta["Summary"], metadata.version(__name__)
    except metadata.PackageNotFoundError:
        return __name__, "", ""


DIST_NAME, DESCRIPTION, VERSION = _distribution()
