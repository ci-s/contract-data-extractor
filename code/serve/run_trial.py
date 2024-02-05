from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI
from langchain.llms import VLLM
import time
import uvicorn

# from langchain.output_parsers import PydanticOutputParser
# from langchain.evaluation import load_evaluator, StringDistance
# import sys

# sys.path.append("../")
# # from model.ModelOps import ModelOps
# from post_operations.parsing import (
#     ExtractedDate,
#     ExtractedName,
#     ExtractedNumber,  # Generic classes
#     ExtractedFloat,
# )
# from prompts.generate_prompts import partial_format
# from data.FileReader import FileReader
# from utils import (
#     QuestionIdManager,
#     PydanticCategoryManager,
#     include_new_question,
#     execute_prompt_and_parse,
#     process_single_question,
#     load_template,
# )
# from eval.evaluation import evaluate_string_similarity, evaluate_number_similarity
# from textract.TextractHelper import TextractHelper

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


app = FastAPI()


############## ENDPOINTS ##############
@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    port_number = 5001
    uvicorn.run(app, host="0.0.0.0", port=port_number)
