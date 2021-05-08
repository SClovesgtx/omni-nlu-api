# The present file, 'Makefile' has been modified from the original at
# https://github.com/NeowayLabs/data-science-template
# under the folllowing license:
#
# MIT License
#
# Copyright (c) 2019 Neoway Business Solution
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

BUILD = docker-compose build
RUN = docker-compose run
UP = docker-compose up
DOWN = docker-compose down
VERSION = $(shell awk -F ' = ' '$$1 ~ /version/ { gsub(/[\"]/, "", $$2); printf("%s",$$2) }' version.toml)

help:
	@echo "USAGE"
	@echo
	@echo "    make <command>"
	@echo "    Include 'sudo' when necessary."
	@echo "    To avoid using sudo, follow the steps in"
	@echo "    https://docs.docker.com/engine/install/linux-postinstall/"
	@echo
	@echo
	@echo "COMMANDS"
	@echo
	@echo "    build           build image using cache"
	@echo "    build-no-cache  build image from scratch, and not from cache"
	@echo "    up              run the images"
	@echo "    build-up        build images services from scratch and after run them up"
	@echo "    down            stop the services"
	@echo "    version         show the corrent version"
	@echo "    bash            bash REPL (Read-Eval-Print loop), suitable for debugging"
	@echo "    python          access Python through the REPL (Read-Eval-Print loop)"
	@echo "    jupyter         access Python through the Jupyter Notebook"
	@echo "    test            run all tests using pytest"
	@echo "    release         Release on the dev branch"

#################
# User Commands #
#################

install-requirements:
	# https://pre-commit.com/
	# https://github.com/pre-commit/pre-commit-hooks
	pip3 install pre-commit
	pre-commit install
	pre-commit migrate-config
	pre-commit autoupdate
build:
	$(BUILD); python3 -m chime
build-no-cache:
	$(BUILD) --no-cache; python3 -m chime
up:
	$(UP)
build-up:
	$(UP) --build
down:
	$(DOWN)
bash:
	$(RUN) bash
python3:
	$(RUN) python3
jupyter:
	$(RUN) jupyter
version:
	echo $(VERSION)
test:
	$(RUN) -e ELASTICSEARCH_HOST="testing" test; python3 -m chime
release:
	git tag -a $(VERSION) -m "VERSION=$(VERSION) read from `version.toml`"
	git push origin HEAD:dev tag $(VERSION); python3 -m chime