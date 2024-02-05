import re

def eliminate_unnecessary_spaces(text):
    # This regular expression matches parts of the text where characters are separated by spaces
    pattern = r'(\b(?:\w\s)+\b)'

    # This function is applied to each match
    def process_match(match):
        # Remove spaces from the matched string if it occurs more than once
        if match.group().count(' ') > 2:
            return match.group().replace(' ', '')
        else:
            return match.group()

    # Use re.sub() to find all matches and apply the function to each one
    return re.sub(pattern, process_match, text)

def remove_extra_whitespaces(contract_text):

    contract_text = re.sub(r'\n', ' ', contract_text)
    contract_text = re.sub(r'\s+', ' ', contract_text)
    return contract_text    

def preprocess(contract_text):
    """
    Preprocesses the given contract text by eliminating unnecessary spaces and removing extra whitespaces.
    
    Args:
        contract_text (str): The contract text to be preprocessed.
    
    Returns:
        str: The preprocessed contract text.
    """
    contract_text = eliminate_unnecessary_spaces(contract_text)
    contract_text = remove_extra_whitespaces(contract_text)
    return contract_text