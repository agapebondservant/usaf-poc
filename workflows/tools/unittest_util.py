import pytest
import csv
import os
import logging
logging.basicConfig(level=logging.INFO)

@pytest.fixture
def set_env_variables(monkeypatch):
    """Reads data from a CSV file and returns a list of dictionaries."""
    filepath = os.path.join(os.path.dirname(__file__), "evaluation_data.csv")

    with open(filepath, 'r', encoding='utf-8') as csvfile:

        reader = csv.DictReader(csvfile)

        monkeypatch.setenv("_TEST_ROWS", str([row for row in reader]))

        monkeypatch.setenv("_EVALUATION_CUTOFF", "0.7")

def test_csv_row_data():
    """
    Evaluate the relevancy score of given rows and asserts that it meets a specified threshold.
    """
    for row in ",".split(os.getenv("_TEST_ROWS")):

        if 'eval_scores_relevancy' in row:

            assert (row['eval_scores_relevancy'] >= int(os.getenv("_EVALUATION_CUTOFF")))