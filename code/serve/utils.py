import os
import json
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import requests
from post_operations.parsing import (
    parse_output,
)


class QuestionIdManager:
    """
    A class that manages question IDs and their associated data.

    Args:
        filename (str): The name of the external JSON file to initialize the question ID dictionary from.

    Attributes:
        questionid_obj_dict (dict): A dictionary that stores question IDs and their associated data.
        filename (str): The name of the external JSON file.

    Methods:
        __init__(self, filename="external_file.json"): Initializes the QuestionIdManager object.
        initialize_questionid_obj_dict(self, json_path_file): Initializes the question ID dictionary from an external JSON file.
        add_questionid(self, questionid, prompt_file, pydantic_category, included="True"): Adds a new question ID and its associated data to the dictionary.
        get_questionid(self, questionid): Retrieves the data associated with a given question ID.
        remove_questionid(self, questionid): Removes a question ID and its associated data from the dictionary.
        update_json_file(self): Writes the question ID dictionary back to the external JSON file.
        get_all_questionids(self): Returns the entire question ID dictionary.
    """

    def __init__(self, filename="external_file.json"):
        self.questionid_obj_dict = {}
        self.filename = filename

        # Initialize questionid_obj_dict from an external file
        self.initialize_questionid_obj_dict(json_path_file=self.filename)

    def initialize_questionid_obj_dict(self, json_path_file):
        """
        Initializes the question ID dictionary from an external JSON file.

        Args:
            json_path_file (str): The path to the JSON file.

        Raises:
            ValueError: If the file is not a JSON file or if the file is not found.
        """
        if json_path_file is None:
            pass
        else:
            if not json_path_file.endswith(".json"):
                raise ValueError(f"File {json_path_file} is not a JSON file.")
            if not os.path.exists(json_path_file):
                raise ValueError(f"File {json_path_file} not found.")
            self.filename = json_path_file
        # Read values from an external JSON file
        with open(self.filename, "r") as file:
            data = json.load(file)

        # Parse the data and populate questionid_obj_dict

        for questionid, question_data in data.items():
            prompt_file = question_data["prompt_file"]
            pydantic_object = question_data["pydantic_object"]
            included = question_data["included"]
            self.questionid_obj_dict[questionid] = {
                "prompt_file": prompt_file,
                "pydantic_object": pydantic_object,
                "included": included,
            }

    def add_questionid(
        self, questionid, prompt_file, pydantic_category, included="True"
    ):
        """
        Adds a new question ID and its associated data to the dictionary.

        Args:
            questionid (str): The question ID.
            prompt_file (str): The file containing the prompt for the question.
            pydantic_category (str): The Pydantic category of the question.
            included (str, optional): Whether the question is included or not. Defaults to "True".
        """
        # Use the function to append new data to a JSON file
        self.questionid_obj_dict[questionid] = {
            "prompt_file": prompt_file,
            "pydantic_object": pydantic_category,
            "included": included,
        }
        self.update_json_file()

    def get_questionid(self, questionid):
        """
        Retrieves the data associated with a given question ID.

        Args:
            questionid (str): The question ID.

        Returns:
            dict: The data associated with the question ID, or None if the question ID is not found.
        """
        return self.questionid_obj_dict.get(questionid, None)

    def remove_questionid(self, questionid):
        """
        Removes a question ID and its associated data from the dictionary.

        Args:
            questionid (str): The question ID.

        Raises:
            ValueError: If the question ID is not found.
        """
        if questionid in self.questionid_obj_dict:
            del self.questionid_obj_dict[questionid]
            self.update_json_file()
        else:
            raise ValueError(f"Questionid {questionid} not found.")

    def update_json_file(self):
        """
        Writes the question ID dictionary back to the external JSON file.
        """
        # Write everything back to the file

        with open(self.filename, "w") as file:
            json.dump(self.questionid_obj_dict, file)

    def get_all_questionids(self):
        """
        Returns the entire question ID dictionary.

        Returns:
            dict: The question ID dictionary.
        """
        return self.questionid_obj_dict


class PydanticCategoryManager:
    """
    A class that manages Pydantic categories and provides methods to retrieve information about them.

    Args:
        pydantic_category_dict (dict): A dictionary containing Pydantic categories as keys and corresponding Pydantic objects as values.

    Methods:
        _verify_category(pydantic_category): Verifies if the given Pydantic category is defined in the pydantic_category_dict.
        get_pydantic_field(category): Retrieves the field name from the Pydantic object associated with the given category.
        get_pydantic_object(category): Retrieves the Pydantic object associated with the given category.
    """

    def __init__(self, pydantic_category_dict):
        self.pydantic_category_dict = pydantic_category_dict

    def _verify_category(self, pydantic_category):
        """
        Verifies if the given Pydantic category is defined in the pydantic_category_dict.

        Args:
            pydantic_category (str): The name of the Pydantic category to verify.

        Raises:
            ValueError: If the given Pydantic category is not defined in the pydantic_category_dict.
        """
        if pydantic_category not in self.pydantic_category_dict.keys():
            raise ValueError(
                f"pydantic_category {pydantic_category} is not defined in pydantic_category_dict"
            )

    def get_pydantic_field(self, category):
        """
        Retrieves the field name from the Pydantic object associated with the given category.

        Args:
            category (str): The name of the category.

        Returns:
            str: The name of the field.

        Raises:
            ValueError: If more than one field is found in the Pydantic object.
        """
        self._verify_category(category)
        fields = list(self.pydantic_category_dict[category].__fields__.keys())
        if len(fields) > 1:
            print("Warning: More than one field found in pydantic object.")
            raise ValueError(
                f"Please specify the field to extract from the pydantic object. Available fields: {fields}"
            )
        return fields[0]

    def get_pydantic_object(self, category):
        """
        Retrieves the Pydantic object associated with the given category.

        Args:
            category (str): The name of the category.

        Returns:
            PydanticModel: The Pydantic object associated with the category.

        Raises:
            ValueError: If the given Pydantic category is not defined in the pydantic_category_dict.
        """
        self._verify_category(category)
        return self.pydantic_category_dict[category]


def load_template(template_folder, template_name):
    template_path = template_folder + template_name

    with open(template_path, "r") as f:
        template = f.read()

    return template


def include_new_question(
    prompt, name_of_entity, pydantic_category, template_folder, question_id_manager
):
    prompt_file = os.path.join(template_folder, f"exp4_{name_of_entity}.txt")  # rename
    with open(prompt_file, "w") as file:
        file.write(prompt)

    # Add questionid to included_questionid_list
    question_id_manager.add_questionid(
        name_of_entity, f"exp4_{name_of_entity}.txt", pydantic_category
    )


def process_single_question(
    llm,
    contract,
    questionid,
    question_id_manager: QuestionIdManager,
    pydantic_category_manager: PydanticCategoryManager,
    template_folder: str,
):
    print("Questionid: ", questionid)
    obj_dict = question_id_manager.get_questionid(questionid)
    if obj_dict is not None:
        prompt = load_template(
            template_name=obj_dict["prompt_file"], template_folder=template_folder
        )

        prompt_template = PromptTemplate(
            template=prompt,
            input_variables=["contract"],
        )
        prompt = prompt_template.format(contract=contract)
        outputs = llm(prompt)

        print("Output: ", outputs)
        print("*" * 20)
        # Parse
        parser = PydanticOutputParser(
            pydantic_object=pydantic_category_manager.get_pydantic_object(
                obj_dict["pydantic_object"]
            )
        )
        return parse_output(outputs, parser)
    else:
        raise ValueError(f"Questionid {questionid} not found.")


def execute_prompt_and_parse(llm, prompt, contract, parser):
    prompt_template = PromptTemplate(
        template=prompt,
        input_variables=["contract"],
    )
    prompt = prompt_template.format(contract=contract)
    outputs = llm(prompt)

    print("Output: ", outputs)
    print("*" * 20)
    # Parse
    return parse_output(outputs, parser)


class WebhookManager:
    def __init__(self, url):
        self.url = url
        self.check_webhook_url()

    def check_webhook_url(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                print("Webhook URL is valid.")
                return True
        except requests.exceptions.RequestException:
            raise ValueError("Webhook URL is not valid.")

    def send_results(self, data):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")

        response = requests.post(self.url, json=data)
        return response
