.PHONY: install run test lint format upgrade release publish clean
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

UV := ./tools/uv.sh
UV_RUN := $(UV) run --locked

INSTALL_STAMP := build/.install-stamp

$(INSTALL_STAMP): uv.lock pyproject.toml tools/install.sh
	@./tools/install.sh
	@mkdir -p $(@D) && touch $@

install: $(INSTALL_STAMP)

run: install
	@$(UV_RUN) randomprime

lint: install
	@$(UV_RUN) ruff check
	@$(UV_RUN) ruff format --check
	@$(UV_RUN) ty check

test: install lint
	@$(UV_RUN) pytest

format: install
	@$(UV_RUN) ruff check --fix
	@$(UV_RUN) ruff format

upgrade: install
	@./tools/install.sh --update
	@$(UV) lock --upgrade

release: install
	@./tools/release.sh

publish: install
	@$(UV) build --out-dir build/pypi
	@$(UV) publish build/pypi/*

clean:
	@rm -rf build
