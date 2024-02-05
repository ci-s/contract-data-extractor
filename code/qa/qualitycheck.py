from dateutil import parser
import re


def get_variations_of_date(date):
    """
    Returns a list of variations of the given date string in different formats.
    
    Args:
    date (str): A date string.
    
    Returns:
    list: A list of date strings in different formats.
    """
    parsed_date = parser.parse(date, dayfirst=True)
    variations = [
        parsed_date.strftime('%d.%m.%Y'),
        parsed_date.strftime('%d %B %Y'),
        parsed_date.strftime('%B %d %Y'),
        parsed_date.strftime('%B %d, %Y'),
        parsed_date.strftime('%d %b %Y'),
        parsed_date.strftime('%b %d %Y'),
        parsed_date.strftime('%b %d, %Y'),
        parsed_date.strftime('%Y-%m-%d'),
        parsed_date.strftime('%Y/%m/%d'),
        parsed_date.strftime('%Y.%m.%d'),
        parsed_date.strftime('%Y %B %d'),
        parsed_date.strftime('%Y %b %d'),
    ]
    return variations

def check_contract_includes_date(contract: str, answer_date: str) -> bool:
    """
    Check if the given contract includes the answer date.
    
    Args:
    contract (str): The contract to check.
    answer_date (str): The date to look for in the contract.
    
    Returns:
    bool: True if the contract includes the answer date, False otherwise.
    """
    
    variations = get_variations_of_date(answer_date)
    for variation in variations:
        if variation in contract:
            return True
    return False

def check_contract_includes_dates(extracted_date, contract):
    """
    Check if the contract includes any of the extracted dates.

    Args:
        extracted_date (list): A list of extracted dates.
        contract (str): The contract to check.

    Returns:
        bool: True if the contract includes any of the extracted dates, False otherwise.
    """
    if len(extracted_date) == 0:
        return False

    for answer in extracted_date:
        if check_contract_includes_date(contract, answer):
            return True
    return False

def check_contract_includes_salary(contract, answer_salary):
    if answer_salary in contract:
        return True
    return False

def check_contract_includes(contract, answer):
    answer = str(answer)
    if answer in contract:
        return True
    return False

def extract_date(text):
    """
    Extracts dates in the format of dd.mm.yyyy from the given text.
    
    Args:
        text (str): The text to extract dates from.
    
    Returns:
        list: A list of dates in the format of dd.mm.yyyy.
    """
    return re.findall(r'\d{2}\.\d{2}\.\d{4}', text)

def validate_date(text):
    """
    Validates the given date string.
    
    Args:
        text (str): The date string to validate.
    
    Returns:
        bool: True if the date string is valid, False otherwise.
    """
    try:
        parser.parse(text, dayfirst=True)
        return True
    except:
        return False
    
def get_output_object_from_openai_response(response):
    """
    Returns the output object from the given response.
    
    Args:
        response (dict): The response from the API.
    
    Returns:
        Any: The output object from the response.
    """
    return response['function']