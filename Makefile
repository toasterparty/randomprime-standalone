.PHONY: install run upgrade release clean
.DEFAULT_GOAL := run

ICON_DIR := randomprime_standalone/assets
ifeq ($(OS),Windows_NT)
    SHELL := C:/Program Files/Git/bin/bash.exe
    ASSET := randomprime-standalone.exe
    NUITKA_OS_FLAGS := --windows-console-mode=disable --windows-icon-from-ico=$(ICON_DIR)/icon.ico
else ifeq ($(shell uname -s),Darwin)
    SHELL := bash
    ASSET := randomprime-standalone-macos
    NUITKA_OS_FLAGS := --macos-app-icon=$(ICON_DIR)/icon.png
else
    SHELL := bash
    ASSET := randomprime-standalone-linux
    NUITKA_OS_FLAGS := --linux-icon=$(ICON_DIR)/icon.png
endif

.SHELLFLAGS := -euo pipefail -c
export PATH := $(HOME)/.local/bin:$(PATH)
export UV_PROJECT_ENVIRONMENT := build/.venv
export PYTHONPYCACHEPREFIX := build/pycache
UV := uv self update -q && uv
UV_RUN := $(UV) run --locked

install:
	@./tools/install.sh

run: install
	@$(UV_RUN) randomprime

upgrade: install
	@$(UV) lock --upgrade

release: install
	@$(UV) run --locked --no-editable python -m nuitka \
		--onefile \
		--python-flag=-m \
		--enable-plugin=tk-inter \
		--assume-yes-for-downloads \
		--output-dir=build/dist \
		--output-filename=$(ASSET) \
		--include-distribution-metadata=randomprime-standalone \
		--include-package-data=randomprime_standalone \
		$(NUITKA_OS_FLAGS) \
		randomprime_standalone

clean:
	@rm -rf build
