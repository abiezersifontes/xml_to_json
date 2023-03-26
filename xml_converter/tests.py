"""
This module defines views and functions for converting XML files to JSON.

The module contains the following functions:

    - xml_to_json(xml_string: str) -> Dict[str, List[Dict[str, Any]]]: Converts an XML string to a custom JSON object
    - upload_page(request: HttpRequest) -> HttpResponse: Renders a file upload page or returns a JSON response for uploaded files
    - converter(request: HttpRequest) -> HttpResponse: Returns a JSON response for uploaded files

The module also contains a Django TestCase for testing XML to JSON conversion.

"""
from pathlib import Path

from django.test import TestCase, Client

TEST_DIR = Path(__file__).parent / Path('test_files')


class XMLConversionTestCase(TestCase):
    """
    Django TestCase for testing XML to JSON conversion.
    """

    def setUp(self):
        self.client = Client()

    def test_connected_convert_empty_document(self):
        """Test that an empty XML document is correctly converted to an empty JSON object."""
        with (TEST_DIR / Path('empty.xml')).open() as fp:
            response = self.client.post("/connected/", {
                'file': fp,
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                "Root": "",
            })

    def test_api_convert_empty_document(self):
        """Test that an empty XML document is correctly converted to an empty JSON object via the API."""
        with (TEST_DIR / Path('empty.xml')).open() as fp:
            response = self.client.post("/api/converter/convert/", {
                'file': fp,
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                "Root": "",
            })

    def test_connected_convert_addresses(self):
        """Test that an XML document containing multiple address elements is correctly converted to JSON."""
        with (TEST_DIR / Path('addresses.xml')).open() as fp:
            response = self.client.post("/connected/", {
                'file': fp,
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                'Root': [
                    {
                        'Address': [
                            {
                                'StreetLine1': '123 Main St.',
                                'StreetLine2': 'Suite 400',
                                'City': 'San Francisco',
                                'State': 'CA',
                                'PostCode': '94103'},
                            {
                                'StreetLine1': '400 Market St.',
                                'City': 'San Francisco',
                                'State': 'CA',
                                'PostCode': '94108'
                            }
                        ]
                    }
                ]
            })
