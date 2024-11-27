import deepeval
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.dataset import EvaluationDataset
import pytest

dataset = EvaluationDataset()

dataset.add_test_cases_from_csv_file(
    # file_path is the absolute path to you .csv file
    file_path=r"C:\Users\bhull\Desktop\UCLA Grad\Spring 2024\CS 219\219_final_project\LLM-assisted_mobile_trace_analysis\inner_dataset.csv",
    input_col_name="input",
    actual_output_col_name="actual_output",
    expected_output_col_name="expected_output"
)

@pytest.mark.parametrize(
    "test_case",
    dataset,
)
def test_customer_chatbot(test_case: LLMTestCase):
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
    assert_test(test_case, [answer_relevancy_metric])


@deepeval.on_test_run_end
def function_to_be_called_after_test_run():
    print("Test finished!")