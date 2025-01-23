import json
import re
from collections import defaultdict
from pprint import pprint, pformat
from typing import Union, Dict, List, Type
import requests

from DOIModels import MainObject

JSON = Union[Dict[str, 'JSON'], List['JSON'], int, str, float, bool, Type[None]]


def get_info(doi: str) -> JSON:
    doi_response = requests.get(f"https://dx.doi.org/{doi}", headers={'Accept': 'application/json'})
    return doi_response.json() if doi_response.ok else {'error_status_code': doi_response.status_code}


def process_doi(doi: str, link_dict: dict[str, str]) -> str:
    doi_info = get_info(doi)
    if 'error_status_code' in doi_info:
        return f"- *ERROR* DOI {doi} gave a response code of {doi_info['error_status_code']}."

    from pydantic import ValidationError

    try:
        obj = MainObject(**doi_info)
        return obj.to_tana(link_dict)
    except ValidationError as err:
        return str(err)


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    doi = event['queryStringParameters']['doi']
    body = process_doi(doi)

    return {
        "statusCode": 200,
        "body": body,
    }


def lambda_post_handler(event, context):
    formatted_body: str = event['body'].strip('"').replace(r'\\n', '\n').replace(r'\n', '\n')
    print(formatted_body)
    link_regex = re.compile(r'\[\[(.+)\^(.+)]]')
    links_by_name = {k: v for k, v in link_regex.findall(formatted_body)}

    doi = event['queryStringParameters']['doi']
    body = process_doi(doi, links_by_name)

    return {
        "statusCode": 200,
        "body": body,
    }


if __name__ == '__main__':
    doc_info = get_info('10.1074/jbc.M204252200')

    from pydantic import ValidationError

    try:
        mo = MainObject(**doc_info)
        print(mo.to_tana())
    except ValidationError as e:
        print(e)
