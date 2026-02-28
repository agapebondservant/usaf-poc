"""Tools for handling reference-based, LLM-as-judge and benchmark
evaluations."""

from crewai.tools import tool
from tools import unittest_util
import logging

logging.basicConfig(level=logging.INFO)

@tool("Run test suite")
def run_test_suite(eval_data_file_path: str, evaluation_cutoff: float = 0.7):
    """
    Runs test suite associated with the test data in
    the given file path.
    Args:
        eval_data_file_path: Path to the evaluation data file.
        evaluation_cutoff: Threshold used to determine a cutoff score for
        passing evaluations. Defaults to 0.7.
    """
    return unittest_util.run_test_suite(eval_data_file_path, evaluation_cutoff)

