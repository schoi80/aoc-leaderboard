#!/usr/bin/make -f

env:
	poetry env use python3
	poetry install

clean:
	rm -rf dist

lint:
	poetry run flake8 . --exclude .venv --count --select=E9,F63,F7,F82 --show-source --statistics
	poetry run flake8 . --exclude .venv --count --exit-zero --max-complexity=15 --max-line-length=150 --ignore=E203,W503 --statistics

streamlit: env
	poetry run python3 -m streamlit run aoc_leaderboard/app.py --theme.base "dark"