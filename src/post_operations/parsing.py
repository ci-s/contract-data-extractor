import sys

sys.path.append("../")

import json
from qa.qualitycheck import validate_date
from langchain.pydantic_v1 import BaseModel, Field, validator


class StartDate(BaseModel):
    start_date: str = Field(
        description="The start date of the employment contract in DD.MM.YYYY format"
    )

    # You can add custom validation logic easily with Pydantic.
    @validator("start_date")
    def validate_start_date(cls, field):
        if not validate_date(field):
            raise ValueError("Not a date!")
        return field


# Helper classes for StartDate validation
class SignDate(BaseModel):
    sign_date: str = Field(
        description="The sign date of the employment contract in DD.MM.YYYY format"
    )

    # You can add custom validation logic easily with Pydantic.
    @validator("sign_date")
    def validate_sign_date(cls, field):
        if not validate_date(field):
            raise ValueError("Not a date!")
        return field


class EmployerName(BaseModel):
    employer_name: str = Field(description="The name of the employer")


class EmployeeName(BaseModel):
    employee_name: str = Field(description="The name of the employee")


# Generic classes for extraction


class ExtractedName(BaseModel):
    name: str = Field(description="The name of the found entity")


class ExtractedNumber(BaseModel):
    number: int = Field(description="The extracted number")

    @validator("number")
    def validate_number(cls, field):
        if not cls.validate_integer(field):
            raise ValueError("Not an integer!")
        return field

    def validate_integer(value):
        try:
            int(value)
            return True
        except ValueError:
            return False


class ExtractedFloat(BaseModel):
    number: float = Field(description="The extracted number")

    @validator("number")
    def validate_number(cls, field):
        if not cls.validate_float(field):
            raise ValueError("Not a float!")
        return field

    def validate_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False


class ExtractedDate(BaseModel):
    date_found: str = Field(description="Extracted date in DD.MM.YYYY format")

    # You can add custom validation logic easily with Pydantic.
    @validator("date_found")
    def validate_date_found(cls, field):
        if not validate_date(field):
            raise ValueError("Not a date!")
        return field


def parse_responses(results_anti, parser, field=None):
    if field is None:
        # If there is only one field in the pydantic object, use that
        available_fields = list(parser.pydantic_object.__fields__.keys())
        if len(available_fields) == 1:
            field = available_fields[0]
        else:
            raise ValueError(
                f"Please specify the field to extract from the pydantic object. Available fields: {available_fields}"
            )
    parsed_results = []
    for result in results_anti:
        sub = []
        for start_date in result:
            try:
                aa = json.loads(start_date)
                sub.append(parser.parse(aa).__getattribute__(field))
            except:
                sub.append("N/A")
        parsed_results.append(sub)
    return parsed_results


def parse_output(output, parser, field=None):
    if field is None:
        # If there is only one field in the pydantic object, use that
        available_fields = list(parser.pydantic_object.__fields__.keys())
        if len(available_fields) == 1:
            field = available_fields[0]
        else:
            raise ValueError(
                f"Please specify the field to extract from the pydantic object. Available fields: {available_fields}"
            )
    try:
        return parser.parse(output).__getattribute__(field)
    except:
        return "N/A"
