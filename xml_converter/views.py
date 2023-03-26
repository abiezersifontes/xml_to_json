"""A module that provides functions for converting XML to JSON."""
import json
from typing import Any, Dict, List
import xmltodict
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response


def xml_to_json(xml_string: str) -> Dict[str, List[Dict[str, Any]]]:
    """Convert an XML string to a custom JSON object.

    Args:
        xml_string (str): The XML string to convert to JSON.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A custom JSON object with the top-level key
        as the root element and each child element as a list of dictionaries.

    """
    # parse the XML string into a dictionary using xmltodict
    xml_dict = xmltodict.parse(xml_string)
    # get the root key of the dictionary
    root_key = list(xml_dict.keys())[0]
    # if the root element is empty, return an empty dictionary
    if not xml_dict[root_key]:
        return {}
    # if the root element contains a single element, wrap it in a list
    if isinstance(xml_dict[root_key], dict):
        xml_dict[root_key] = [xml_dict[root_key]]
    # create a custom JSON object with the root key as the top-level key
    custom_json = {root_key: []}
    # iterate through each child element of the root element
    for child in xml_dict[root_key]:
        # create a dictionary to store the child element's key-value pairs
        child_json = {}
        # iterate through each key-value pair in the child element
        for key, value in child.items():
            # if the value is a list, recursively call xml_to_json on each list item and append the result to a list
            if isinstance(value, list):
                child_json[key] = []
                for item in value:
                    child_json[key].append(xml_to_json(
                        xmltodict.unparse({key: item}))[key][0])
            # if the value is a dictionary, recursively call xml_to_json on the dictionary
            elif isinstance(value, dict):
                child_json[key] = xml_to_json(
                    xmltodict.unparse({key: value}))[key]
            # if the value is a scalar value, add the key-value pair to the child dictionary
            else:
                child_json[key] = value
        # append the child dictionary to the custom JSON object
        custom_json[root_key].append(child_json)
    # return the custom JSON object
    return custom_json


def upload_page(request) -> HttpResponse:
    """Render the upload page and convert the uploaded XML file to JSON.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The HTTP response with the JSON data.

    """
    json_data = None
    if xml_file := request.FILES.get('file'):
        if request.method == 'POST':
            try:
                xml_string = xml_file.read().decode('utf-8')
                # convert the XML file to JSON using xml_to_json
                json_data = xml_to_json(xml_string) or {'Root': ''}
                # return the JSON response
                return HttpResponse(json.dumps(json_data), content_type='application/json')
            except Exception:
                print("Error converting XML to JSON")
                return HttpResponseBadRequest("Invalid XML file")
    return render(request, 'upload_page.html', {'json': json_data})


@api_view(['POST'])
def converter(request) -> Response:
    """Convert the uploaded XML file to JSON.

    Args:
        request (Request): The request object.

    Returns:
        Response: The JSON response.

    """
    if xml_file := request.FILES.get('file'):
        try:
            xml_string = xml_file.read().decode('utf-8')
            # convert the XML file to JSON using xml_to_json
            json_data = xml_to_json(xml_string)
            # return the JSON respons

            if not json_data:
                json_data = {'Root': ''}
            return Response(json_data, content_type='application/json')
        except Exception:
            return Response({"error": "Invalid XML file"}, status=400)
    return Response({"error": "No file uploaded"}, status=400)
