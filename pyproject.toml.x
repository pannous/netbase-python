# setup.py is deprecated, use pyproject.toml and `python -m build` instead

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[tool.poetry]
name = "Netbase"
version = "0.1.23"
description = "Netbase : Wikidata World Graph"
authors = [{ name = "Pannous", email = "info@pannous.com" }]
license = "Apache2 license"
dependencies = { "dill"= "*" }
url = "https://github.com/pannous/netbase-python"

[tool.poetry.scripts]
netbase = "netbase.py"

[tool.poetry.dependencies.angle]
git = "http://github.com/pannous/netbase-python.git"
