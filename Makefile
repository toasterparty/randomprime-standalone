.PHONY: install run test upgrade release publish clean
.DEFAULT_GOAL := run

ifeq ($(OS),Windows_NT)
    # tools/find-bash.ps1 locates Git bash via the registry PATH, so it is found
    # even in a terminal opened before install-bash.ps1 ran (no restart needed).
    # Guard via BASH (not SHELL): make refuses to leave SHELL empty, so an empty
    # result would silently fall back to cmd.exe instead of failing loudly here.
    BASH := $(shell powershell -NoProfile -File tools/find-bash.ps1)
    ifeq ($(BASH),)
        $(error Could not locate Git bash - run tools/install-bash.ps1 (open a new terminal if you just installed it))
    endif
    SHELL := $(BASH)
else
    SHELL := bash
endif
.SHELLFLAGS := -euo pipefail -c

# install.sh puts uv on PATH; here we only keep its venv and bytecode cache
# inside build/ without exporting those globally.
UV_ENV := UV_PROJECT_ENVIRONMENT=build/.venv PYTHONPYCACHEPREFIX=build/pycache
UV := $(UV_ENV) uv
UV_RUN := $(UV) run --locked

install:
	@./tools/install.sh

run: install
	@$(UV_RUN) randomprime

test: install
	@$(UV_RUN) pytest

upgrade: install
	@$(UV) lock --upgrade

release: install
	@$(UV_ENV) tools/release.sh

publish: install
	@$(UV_ENV) uv build --out-dir build/pypi
	@$(UV_ENV) uv publish build/pypi/*

clean:
	@rm -rf build
