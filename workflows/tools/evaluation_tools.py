"""Tools for handling reference-based, LLM-as-judge and benchmark
evaluations."""

from crewai.tools import tool
from tools import evaluation_util
import logging

logging.basicConfig(level=logging.INFO)

@tool("Get reference-based evaluation scores")
def get_reference_based_eval_scores(test_data_file_path: str):
    """
    Gets reference-based evaluation scores associated with the test data in
    the given file path.
    Args:
        test_data_file_path: Path to the test data file.
    Returns:
        Evaluation results in CSV format.
    """
    return evaluation_util.compute_reference_based_eval_scores(test_data_file_path)

@tool("Get LLM-as-judge evaluation scores")
def get_llm_as_judge_evaluation_scores(test_data_file_path: str,
                                       model_prefix: str = "REFERENCE",
                                       threshold: float = 0.7):
    """
    Gets LLM-as-judge evaluation scores associated with the test data in the given file path.
    Args:
        test_data_file_path: Path to the test data file.
        model_prefix: Model prefix used to identify the evaluation results.
        Defaults to "REFERENCE".
        threshold: Threshold used to determine a cutoff for evaluations. Defaults to 0.7.
    Returns:
        Evaluation results in CSV format.
    """
    return evaluation_util.compute_reference_free_eval_scores(
        test_data_file_path=test_data_file_path,
        model_prefix=model_prefix,
        threshold=threshold)

@tool("Get benchmark evaluation scores")
def get_benchmark_eval_scores(benchmark_file_path: str,
                                  model_prefix: str = "REFERENCE",
                                  threshold: float = 0.7):
    """
    Gets benchmark evaluation scores associated with the test data in the given file path.
    Args:
        benchmark_file_path: Path to the benchmark data file.
        model_prefix: Model prefix used to identify the evaluation results. Defaults to "REFERENCE".
        threshold: Threshold used to determine a cutoff for evaluations. Defaults to 0.7.
    Returns:
        Evaluation results in CSV format.
    """
    return evaluation_util.compute_benchmark_eval_scores(benchmark_file_path=benchmark_file_path,
                                                         model_prefix=model_prefix,
                                                         threshold=threshold,
                                                         multiple_rows=True)

