###############################################################################
#  Provides methods for performing reference-based, reference-free and
#  benchmark evaluations using DeepEval.
###############################################################################

##############################################
# Imports
##############################################
import os
import traceback
from openai import OpenAI
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval import assert_test, evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric
from evaluate import load
from deepeval.metrics import ArenaGEval
from deepeval.test_case import ArenaTestCase
from deepeval import compare
import nltk
import pandas as pd
import matplotlib.pyplot as plt
import logging
logging.basicConfig(level=logging.INFO)
from data_models.data_models import EvalDetails

from dotenv import load_dotenv
load_dotenv()

##############################################
# Set Up Metric Instances
##############################################
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('punkt_tab')
bleu_metric = load("bleu")
rouge_metric = load("rouge")
meteor_metric = load("meteor")
bertscore_metric = load("bertscore")


##############################################
# Utilities
##############################################
def get_file_content(filepath: str) -> str:
    """Retrieves the contents of a file."""
    with open(filepath, "r") as file:
        return file.read()

def get_test_records_as_dataframe(test_data_file_path: str):
    """
    Converts the provided test data file into a Dataframe of test records.
    :param test_data_file_path: Path to the test data source file.
    :return: The test records represented as a DataFrame.
    """

    try:
        file_content = get_file_content(test_data_file_path)

        EvalDetails.model_validate_json(file_content)

        df = pd.read_json(test_data_file_path).fillna("")

        df = pd.json_normalize(df['data'])

        return df

    except Exception as e:
        logging.error(f"Could not extract data: {e}")

        logging.error(traceback.format_exc())

##############################################
# Evaluator Tools
##############################################
class CustomLLM(DeepEvalBaseLLM):
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def load_model(self):
        return self.client

    def generate(self, prompt: str, schema=None):
        if schema:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            return schema.model_validate_json(response.choices[0].message.content)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    async def a_generate(self, prompt: str, schema=None):
        return self.generate(prompt, schema=schema)

    def get_model_name(self):
        return self.model_name


##############################################
# Reference-Based Evaluation Methods
# using standard metrics from the
# evaluate framework
##############################################
def compute_reference_based_eval_scores(test_data_file_path: str):
    """
    Computes the reference based evaluation scores.
    :param test_data_file_path: Path to the test data source file.
    :return: The reference based evaluation scores in CSV format.
    """
    def compute_bleu4_scores(predictions, references):
        """
        Computes BLEU-4 Scores
        """
        results = bleu_metric.compute(predictions=predictions, references=references)
        return results["bleu"]

    def compute_rouge_scores(predictions, references):
        """
        Computes ROUGE Scores
        """
        results = rouge_metric.compute(predictions=predictions, references=references)
        return results["rougeL"]

    def compute_meteor_scores(predictions, references):
        """
        Computes METEOR Scores
        """
        results = meteor_metric.compute(predictions=predictions, references=references)
        return results["meteor"]


    def compute_bert_scores(predictions, references):
        """
        Computes BERT Scores
        """
        results = bertscore_metric.compute(predictions=predictions, references=references, lang="en")
        return results["f1"]

    data = get_test_records_as_dataframe(test_data_file_path)

    predictions = data["predictions"].tolist()

    references = data["references"].tolist()

    references = [[reference] for reference in references]

    results = {
        "bleu4": compute_bleu4_scores(predictions, references),
        "rougel": compute_rouge_scores(predictions, references),
        "meteor": compute_meteor_scores(predictions, references),
        "bert": compute_bert_scores(predictions, references)
    }

    results = {f"{key}_{suffix}": value.get(suffix) for suffix in ['score', 'reason'] for key, value in results.items() }

    eval_df = pd.DataFrame(results, index=data.index)

    data[eval_df.columns.tolist()] = eval_df

    return data.to_csv()

##############################################
# Reference-Free Evaluation Methods
##############################################
def compute_reference_free_eval_scores(test_data_file_path: str,
                                       model_prefix: str,
                                       threshold: float = 0.7):
    """
    Computes reference-free evaluation scores based on test data using
    DeepEval framework and LLM-as-Judge metrics.
    Currently only supports AnswerRelevancy metric.
    :param test_data_file_path: Test data file path.
    :param model_prefix: The prefix of the model name.
    :param threshold: The threshold to use for computing scores.
    :return: CSV-formatted version of the dataframe containing the scores.
    """
    try:

        data = get_test_records_as_dataframe(test_data_file_path)

        records = data.to_dict(orient='records')

        evaluatorLlm = CustomLLM(client = OpenAI(
            api_key=os.getenv(f"{model_prefix}_LLM_TOKEN"),
            base_url=os.getenv(f"{model_prefix}_LLM_API_BASE")),
            model_name = os.getenv(f"{model_prefix}_LLM_ID"))

        test_cases = [LLMTestCase(input=str(record["baseline"]),
                                  actual_output=str(record["candidate"]))
                      for record in records]

        metrics = [AnswerRelevancyMetric(threshold=threshold,
                                         model=evaluatorLlm,
                                         verbose_mode=False)]

        results = evaluate(test_cases=test_cases, metrics=metrics)

        result_scores_relevancy = [metric.score for result in results.test_results for metric in result.metrics_data if metric.name=="Answer Relevancy"]

        result_reasons_relevancy = [metric.reason for result in results.test_results for metric in result.metrics_data if metric.name=="Answer Relevancy"]

        data["eval_scores_relevancy"] = result_scores_relevancy

        data["eval_reasons_relevancy"] = result_reasons_relevancy

        return data.to_csv()

    except Exception as e:
        logging.error(f"Error processing evaluations from {test_data_file_path}: {e}")

        logging.error(traceback.format_exc())

##############################################
# Benchmark Evaluation Methods
##############################################
def compute_benchmark_eval_scores(benchmark_file_path: str,
                                  model_prefix: str,
                                  threshold: float):
    """
    Computes benchmark evaluation scores based on test data using
    DeepEval framework and LLM-as-Judge metrics.
    The benchmark file should have the following columns:
    baseline: Represents data that will be used as a baseline for the
    evaluation, ex. input questions, context data, etc.
    candidate: Represents the data to be evaluated in CSV format.
    """
    try:

        return compute_reference_free_eval_scores(benchmark_file_path,
                                                  model_prefix,
                                                  threshold=threshold)

    except Exception as e:
        logging.error(f"Error processing benchmark evaluations from {benchmark_file_path}: {e}")

        logging.error(traceback.format_exc())

