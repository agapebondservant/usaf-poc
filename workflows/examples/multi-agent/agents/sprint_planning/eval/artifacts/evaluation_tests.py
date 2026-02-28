import pytest
import csv
import os
import logging
logging.basicConfig(level=logging.INFO)

def pytest_addoption(parser):
    parser.addoption(
        "--evaluation_data",
        action="store",
        default="./spec/tmp/evaluation_data.csv",
        help='Specify evaluation data file path.'
    )

    parser.addoption(
        "--evaluation_threshold",
        action="store",
        default=0.7,
        help='Specify evaluation threshold.'
    )

@pytest.fixture
def evaluation_data(request):
    return request.config.getoption("--evaluation_data")

@pytest.fixture
def evaluation_threshold(request):
    return request.config.getoption("--evaluation_threshold")

def test_csv_row_data(evaluation_data, evaluation_threshold):
    """
    Evaluate the relevancy score of given rows and asserts that it meets a specified threshold.
    """
    with open(evaluation_data, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        rows = [row for row in reader]

        for row in rows:

            if 'eval_scores_relevancy' in row:

                assert (row['eval_scores_relevancy'] >= int(evaluation_threshold))

    assert True