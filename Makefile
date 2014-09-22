CODEDIR=teiler
UNITTESTS=tests
BASE=./main.py

run:
	python ${BASE}

check:	clean lint test

test:
	`which trial` ${UNITTESTS}

lint:
	find . -name '*.py' | xargs flake8

install-dev:
	pip install -e ".[dev]"

cover:
	coverage run --source=${CODEDIR} --branch `which trial` ${UNITTESTS} && coverage html -d _trial_coverage --omit="${UNITTESTS}/*"

open-cover:
	open ./_trial_coverage/index.html

clean:
	find . -name '*.pyc' -delete
	find . -name '.coverage' -delete
	find . -name '_trial_coverage' -print0 | xargs rm -rf
	find . -name '_trial_temp' -print0 | xargs rm -rf
	find . -name 'htmlcov' -print0 | xargs rm -rf
