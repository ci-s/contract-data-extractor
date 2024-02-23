from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI
from langchain.llms import VLLM
import time
import uvicorn
from langchain.output_parsers import PydanticOutputParser
from langchain.evaluation import load_evaluator, StringDistance
import sys

sys.path.append("../")
# from model.ModelOps import ModelOps
from post_operations.parsing import (
    ExtractedDate,
    ExtractedName,
    ExtractedNumber,  # Generic classes
    ExtractedFloat,
)
from prompts.generate_prompts import partial_format
from data.FileReader import FileReader
from utils import (
    QuestionIdManager,
    PydanticCategoryManager,
    WebhookManager,
    include_new_question,
    execute_prompt_and_parse,
    process_single_question,
    load_template,
)
from eval.evaluation import evaluate_string_similarity, evaluate_number_similarity
from textract.TextractHelper import TextractHelper

############## SETUP ##############
# Move to config file,
model_id = "mistralai/Mistral-7B-Instruct-v0.2"
PROMPT_FOLDER = "../prompts/"
PROMPT_TEMPLATE_FILE = "exp3_template_prompt.txt"
question_id_list_file = "question_id_list.json"
STRING_DISTANCE_THRESHOLD = 0.1  # TODO: RECONSIDER VALUE
S3_PROFILE_NAME = "cisem.altan"
S3_BUCKET_NAME = "cis-idp"
data_folder = "../../data"

llm = VLLM(
    model=model_id,
    trust_remote_code=True,  # mandatory for hf models
    max_new_tokens=128,
    top_k=10,
    top_p=0.95,
    temperature=0.1,
    vllm_kwargs={"max_model_len": 16000},
)

question_id_manager = QuestionIdManager(question_id_list_file)
pydantic_category_manager = PydanticCategoryManager(
    {
        "string": ExtractedName,
        "number": ExtractedNumber,  # integer
        "date": ExtractedDate,
        "float": ExtractedFloat,
    }
)

filereader = FileReader()
textract = TextractHelper(S3_PROFILE_NAME, S3_BUCKET_NAME)
distance_evaluator = load_evaluator(
    "string_distance", distance=StringDistance.LEVENSHTEIN
)
webhook_manager = WebhookManager(
    url="https://webhook.site/c14b751e-3823-48ea-b30b-77c840760188"
)

app = FastAPI()


############## ENDPOINTS ##############
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/v1/ask_single_question")
async def ask_single_question(request: Request) -> Response:
    request_dict = await request.json()
    # Read contract
    file_url = request_dict.pop("file_url")
    questionid = request_dict.pop("questionid")

    contract = filereader.read_contract_from_url(file_url)
    return process_single_question(
        llm,
        contract,
        questionid,
        question_id_manager,
        pydantic_category_manager,
        PROMPT_FOLDER,
    )


@app.post("/v1/process_contract")
async def process_contract(request: Request) -> Response:
    print("Processing contract..")
    start_time = time.time()

    request_dict = await request.json()

    # Read contract
    file_url = request_dict.pop("file_url")

    contract = filereader.read_contract_from_url(file_url)

    # Create output dictionary
    parsed_output = {}
    for questionid in question_id_manager.get_all_questionids():
        if not question_id_manager.get_questionid(questionid)["included"]:
            continue
        # parsed_output[questionid] = []
        print("*" * 20)
        print("Questionid: ", questionid)

        outputs = process_single_question(
            llm,
            contract,
            questionid,
            question_id_manager,
            pydantic_category_manager,
            PROMPT_FOLDER,
        )

        parsed_output[questionid] = outputs

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken for processContract: {elapsed_time} seconds")
    print("Done!")
    webhook_manager.send_results(parsed_output)
    return JSONResponse(parsed_output)


@app.post("/v1/add_question")
async def add_question(request: Request) -> Response:
    # Receive 1-2 sentence question and create prompt template, add to file
    request_dict = await request.json()
    question = request_dict.pop("question")
    name_of_entity = request_dict.pop("name_of_entity")
    pydantic_category = request_dict.pop("pydantic_category")
    expected_format = request_dict.pop("expected_format")

    file_urls = request_dict.pop("file_urls", None)  # should be a list
    tolerated_difference_in_number_output = request_dict.pop(
        "tolerated_difference_in_number_output", 0
    )
    ground_truth = request_dict.pop(
        "ground_truth", None
    )  # should be a list, same length as filenames, ground truth corresponding to each file in order

    # Create format
    pydantic_field = pydantic_category_manager.get_pydantic_field(pydantic_category)

    parser = PydanticOutputParser(
        pydantic_object=pydantic_category_manager.get_pydantic_object(pydantic_category)
    )

    # Modify prompt template
    prompt = load_template(
        template_name=PROMPT_TEMPLATE_FILE, template_folder=PROMPT_FOLDER
    )

    prompt = partial_format(
        prompt,
        question=question,
        pydantic_field=pydantic_field,
        expected_format=expected_format,
    )

    if file_urls is not None:
        # Run evaluation
        evaluation = []
        for i, file_url in enumerate(file_urls):
            contract = filereader.read_contract_from_url(file_url)

            output = execute_prompt_and_parse(llm, prompt, contract, parser)
            print("File URL: ", file_url, "\nExtracted entity: ", output)

            if ground_truth is not None:
                print("Ground truth: ", ground_truth[i])
                if output == "N/A":
                    evaluation.append(False)
                elif type(output) == str:
                    evaluation.append(
                        evaluate_string_similarity(
                            ground_truth[i],
                            output,
                            distance_evaluator,
                            STRING_DISTANCE_THRESHOLD,
                        )
                    )
                elif type(output) == int or type(output) == float:
                    evaluation.append(
                        evaluate_number_similarity(
                            ground_truth[i],
                            output,
                            tolerated_difference_in_number_output,
                        )
                    )
                else:
                    raise ValueError(
                        f"Output type {type(output)} not supported for evaluation."
                    )

        if ground_truth is not None:
            print(
                "Evaluation result:\nAccuracy: %",
                sum(evaluation) / len(evaluation) * 100,
            )
            print(
                "Evaluation details: ",
                [f"{file_urls[i]}: {ev}" for i, ev in enumerate(evaluation)],
            )
    # Decide to include question or not
    include_question = input("Include question? (y/n): ")

    if include_question == "y":
        # Write prompt to file
        include_new_question(
            prompt=prompt,
            name_of_entity=name_of_entity,
            pydantic_category=pydantic_category,
            template_folder=PROMPT_FOLDER,
            question_id_manager=question_id_manager,
        )
        return JSONResponse("Question added")
    else:
        return JSONResponse("Question not added")


@app.post("/v1/remove_question")
async def remove_question(request: Request) -> Response:
    request_dict = await request.json()
    name_of_entity = request_dict.pop("name_of_entity")

    question_id_manager.remove_questionid(name_of_entity)
    return JSONResponse("Question removed")


@app.get("/v1/list_all_questions")
async def list_all_questions() -> Response:
    return JSONResponse(list(question_id_manager.get_all_questionids().keys()))


# Different than the rest of the endpoints, this one takes a list of questions as full sentences (instead of questionids)
# and operate on files in S3
@app.post("/v1/query_salary_slip")
async def query_single_page_s3_pdf(request: Request) -> Response:
    """
    Queries a single page PDF document stored in an S3 bucket using Amazon Textract.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: The HTTP response object containing the query results.
    """
    request_dict = await request.json()
    file_url = request_dict.pop("file_url")
    questions = request_dict.pop("questions")

    # read from url
    temp_file_path = filereader.read_url(file_url)
    # write s3
    filename_in_s3 = textract.upload_file_to_s3(temp_file_path)

    response = textract.sync_query_document(filename_in_s3, questions)
    query_dict = textract.get_query_results(response)

    # clean
    textract.delete_s3_file(filename_in_s3)
    filereader.delete_local_file(temp_file_path)
    return JSONResponse(query_dict)


if __name__ == "__main__":
    port_number = 5001
    uvicorn.run(app, host="0.0.0.0", port=port_number)
