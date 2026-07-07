from importlib import metadata

__all__ = ["DIST_NAME", "VERSION"]

try:
    DIST_NAME = metadata.metadata(__name__)["Name"]
    VERSION = metadata.version(__name__)
except metadata.PackageNotFoundError:
    DIST_NAME = __name__
    VERSION = ""
