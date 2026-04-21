# /!\ /!\ /!\ /!\ /!\ /!\ /!\ DISCLAIMER /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\/!\ /!\ /!\/!\
#
# This Makefile is only meant to be used for DEVELOPMENT purpos
#
# PLEASE DO NOT USE IT FOR YOUR PRODUCTION... but adapt it eventually
#
# /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\/!\ /!\ /!\/!\
#
# Original Reference: https://github.com/NetCarapace/url-checker
########################################################################################
# How-to use
########################################################################################
# Run the make with as follow:
#
# ```bash
# make ${make_target} \
#      + optional variable definitions depending on the target, see ```make help``
# ```

BOLD := \033[1m
RESET := \033[0m
GREEN := \033[1;32m
RED := \033[31m
BOLD_GREEN := \033[1;32m

########################################################################################
# PREAMBLE - OS AND DEPENDENCY CHECKS
########################################################################################
# Detect OS
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    $(info ✅ Running on Linux)
    OS := Linux
	# Detect package manager
    ifneq (,$(shell command -v apt 2> /dev/null))
        PKG_MANAGER := apt
    else ifneq (,$(shell command -v dnf 2> /dev/null))
        PKG_MANAGER := dnf
    else ifneq (,$(shell command -v yum 2> /dev/null))
        PKG_MANAGER := yum
    else ifneq (,$(shell command -v zypper 2> /dev/null))
        PKG_MANAGER := zypper
    else ifneq (,$(shell command -v pacman 2> /dev/null))
        PKG_MANAGER := pacman
    else
        $(error ❌ Unable to detect package manager (apt, dnf, yum, zypper, or pacman))
    endif
    $(info ✅ Package manager detected: $(PKG_MANAGER))
else ifeq ($(UNAME_S),Darwin)
    $(info ✅ Running on macOS)
    OS := macOS
else
    $(error ❌ Unsupported OS: $(UNAME_S). Only Linux and macOS are supported.)
endif
UNAME_S :=

# Check for bash

ifeq (,$(shell command -v bash 2> /dev/null))
    $(error ❌ bash not found. Please install bash.)
else
    $(info ✅ bash found: $(shell command -v bash))
endif

# Check for uv
ifeq (,$(shell command -v uv 2> /dev/null))
    $(error ❌ uv not found. Please install uv, ideally with your package manager, or from https://github.com/astral-sh/uv)
else
    UV_VERSION := $(shell uv --version 2>/dev/null)
    $(info ✅ uv found: $(UV_VERSION))
endif
UV_VERSION :=


########################################################################################
# VARIABLES
########################################################################################

# Use Bash and its facilities
SHELL := /bin/bash

# Setup environments
# We include files if they exists, or create them from templates for init_repo recipe
ifneq ($(wildcard ./.envinit),)
include .envinit
export $(shell sed 's/=.*//' .envinit)
endif

# Check for the presence of envfiles
envfiles := .env
env_file_non_present := 0

define check_envfile
ifeq ($$(wildcard ./$(1)),)
$$(info $(1) file was created from template.)
$$(shell cp $(1).template $(1))
$$(eval env_file_non_present := 1)
endif
endef

$(foreach envfile,$(envfiles),$(eval $(call check_envfile,$(envfile))))

ifeq ($(env_file_non_present),1)
$(shell echo -e "$(RED)$(BOLD)At least one envfile was recreated from template, please modify varenvs: run configure_repo_dev or manually.$(RESET)" >&2)
$(error ❌ Please correct and run again. ❌)
endif
env_file_non_present :=
envfile :=

# Include their content on next runs
-include $(envfiles)
$(foreach file,$(envfiles),$(eval export $(shell sed 's/=.*//' $(file))))

# Build intermediary variables
# We currently use the debian convention at some level
# Even if our package is not really a debian package yet
PACKAGE_VERSION = $(shell cat VERSION)
PACKAGE_SUFFIX = deployment-bundle.tar.gz
PACKAGE_FULLNAME = ${PACKAGE_NAME}_v${PACKAGE_VERSION}_Python${PACKAGE_PYTHON}-${PACKAGE_SUFFIX}

# Houskeeping forcing variables
# We reserve normally automation for CI/CD - Experimental in this repo
automatic = "N"
#
# this one is to bump version, different from PACKAGE_VERSION which only reads Version state
version_repo = "0.0.0"
#
tag_message = ""
venv_dir = ".venv"
venv_command = ". $(venv_dir)/bin/activate"
#
new_package = ""

export PATH := $(shell pwd):$(VIRTUAL_ENV):$(PATH)

########################################################################################
# RULES
########################################################################################

.SILENT:
.PHONY: configure_repo_dev \
		clean \
		testclean \
		distclean \
		coverageclean \
		run_dev_infra \
		migrate_db \
		run \
		nuke

# Init
########################################################################################
configure_repo_dev: install-dev
# TODO Help the User to create the .envdev and .env files
	# Use it when we have a pyproject.toml file \
	# uv sync --locked; \
	# \
	echo "${venv_command}"; \
	uv run --python $(VIRTUAL_ENV)/bin/python pip3 list; \
	go_to_install="N"; \
	if [ ${automatic} = "N" ]; then \
		echo "Reply Y if and only if the pip3 list output above is consistent and does not display system packages !"; \
		echo "Ctrl+C to escape ..."; \
		read -p "Do you want to install other specific dependencies from specific requirement files with pip ? (Y/N) " go_to_install; \
	if [ $$go_to_install = "Y" ] || [ $$go_to_install = "y" ]; then \
		# Use it when we have a pyproject.toml file \
		# uv run --python $(VIRTUAL_ENV)/bin/python pip3 install -r requirements-dev.txt -e .; \
		# \
		uv run --python $(VIRTUAL_ENV)/bin/python pip3 install -r requirements.txt -r requirements-dev.txt; \
	else \
		echo "Tweak requirements-dev.txt skipped"; \
	fi \
	fi

	# For later \
	# uv run --python $(VIRTUAL_ENV)/bin/python pre-commit install; \
	# uv run --python $(VIRTUAL_ENV)/bin/python pre-commit autoupdate; \
	# echo "Initial pre-commit run"; \
	# uv run --python $(VIRTUAL_ENV)/bin/python pre-commit run --all-files; \
	# echo "Virtual environment created, local repo configured with pre-commit hooks."; \

	# cd /tmp;# \
	# git clone TODO ADD Github stuff

# Development lifecycle #
########################################################################################
# Dependencies
# -dev suffixes means we specifically manage dependencies present only in Dev Environment
install_deps:
	uv venv --seed $(VIRTUAL_ENV)
	# Use it when we have a pyproject.toml file \
	# uv sync --locked \
	# \


install-dev:
	uv venv --seed $(VIRTUAL_ENV)
	# Use it when we have a pyproject.toml file \
	# uv sync --dev --locked \
	# \
	uv pip install --python $(VIRTUAL_ENV)/bin/python pip

add_newdep:
	uv add $(new_package)

add_newdep-dev:
	uv add --dev $(new_package)

update_deps:
	uv lock --upgrade
	uv sync --locked
########################################################################################

# Run Application
run: run_dev_infra
	uv run --python $(VIRTUAL_ENV)/bin/python python start.py --from User --mission "MY-SAT-1" --description "..."

run_web: run_dev_infra
	uv run --python $(VIRTUAL_ENV)/bin/python python web/server.py
########################################################################################

# Various Helpers
run_dev_infra:
	echo "If you do not provide an API TOKEN to Claude API in Cloud, please run your own agents LLM."
	ollama pull $$LLM_MODEL
########################################################################################

################
# Housekeeping #
################
format_and_lint:
	uv run --python $(VIRTUAL_ENV)/bin/python pre-commit run --all-files --show-diff-on-failure --verbose;

bump_version: VERSION
ifeq (${version_repo},"0.0.0")
	@echo "❌ Provide version_repo=X.Y.Z on CLI"
	@echo "Usage: make bump_version version_repo=1.2.3"
else
	@echo "✅ Ensure clean working directory first"
	@if ! git diff-index --quiet HEAD --; then \
		echo "❌ Working directory is dirty. Commit or stash changes first."; \
		exit 1; \
	fi

	@echo "🔄 Pulling latest changes..."
	git pull

	@echo "📝 Bumping repo to version ${version_repo}"
	echo ${version_repo} > VERSION
	sed -i "s/.*__version__.*/__version__ = \"${version_repo}\"/" "src/$(PACKAGENAME)/__init__.py"
	sed -i "s/.*version =.*/version = \"${version_repo}\"/" "pyproject.toml"

	@echo "🔒 Updating uv.lock..."
	uv lock

	@echo "📦 Staging changes..."
	git add VERSION
	git add "src/$(PACKAGENAME)/__init__.py"
	git add "pyproject.toml"
	git add uv.lock

	@echo "💾 Committing changes..."
	git commit -m "BUMP to version ${version_repo}"

	@echo "🏷️  Creating tag ${version_repo}..."
	git tag ${version_repo} -m "${tag_message}"

	@echo "🚀 Pushing to remote..."
	git push
	git push --tags

	@echo "✅ Version bumped to ${version_repo}"
endif

clean:
	-find . -name __pycache__ -print0 | xargs -0 rm -rf
	-find . -name "*.pyc" -print0 | xargs -0 rm -rf
	-find . -name "*.egg-info" -print0 | xargs -0 rm -rf

coverageclean:
	-rm src/urlchecker/.coverage
	-rm src/urlchecker/.coverage.*
	-rm src/urlchecker/coverage.xml
	-rm -rf src/urlchecker/htmlcov

distclean:
	-rm -rf ./dist
	-rm -rf ./build
	-rm -rf $(VIRTUAL_ENV)

nuke: clean distclean testclean

testclean: coverageclean clean
	-rm -rf .tox

################
# Makefile Doc #
################

help :
	echo ""
	echo -e "${BLUE}${BOLD}### I am your quick and dirty Help file :) ###${RESET}"
	echo ""
	echo -e "${BOLD}# Run make with targets like:${RESET}"
	echo "make target someparameter=\"somevalue\""
	echo ""
	echo -e "${GREEN}# Available combinations arguments/targets/description:${RESET}"
	echo ""
	echo -e "${BOLD}🛠️  Initialize local dev environment:${RESET}"
	@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "configure_repo_dev" "/" "Configure local Python3 venv + pre-commit hooks"
	echo ""
	echo -e "${BOLD}📦 Development lifecycle:${RESET}"
		@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "run" "/"  "Run Dev Flask server (local venv) + Dev Infrastructure (docker-compose)"
		@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "format_and_lint" "/"  "Format + lint (pre-commit style)"
	@printf "  %-20s %s %-20s %s %s\n" "[new_package="package-name"]" "/" "add_newdep-dev" "/"  "Just add one new dep in dev mode"
	echo ""
	echo -e "${BOLD}🧹 Housekeeping:${RESET}"
	@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "format_and_lint" "/" "Run the formatter and linter our of pre-commit hooks"
	@printf "  %-20s %s %-20s %s %s\n" "[version_repo=X.Y.Z]" "/" "bump_version" "/" "Bump version + tag (use version_repo=X.Y.Z)"
	@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "clean" "/" "Clean Python artifacts"
	@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "coverageclean" "/" "Clean Coverage test artifacts"
	@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "distclean" "/" "Clean Build and Dist artifacts"
	@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "venvclean" "/" "Clean .venv artifacts"
	@printf "  %-20s %s %-20s %s %s\n" "[none]" "/" "nuke" "/" "Chain the cleaning steps above"
	echo ""
	echo -e "${BOLD}💡 Examples:${RESET}"
	echo "  make configure_repo_dev"
	echo "  make run"
	echo "  make bump_version version_repo=1.2.3 tag_message=\"Release v1.2.3\""
	echo ""
	echo -e "${BOLD}📝 Default arguments that can be superseded on CLI:${RESET}"
	echo "- automatic=\"N\""
	echo "- version_repo=\"0.0.0\""
	echo "-	tag_message=\"\""
	echo "- new_package=\"\""
	echo ""
