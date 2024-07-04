from typing import List, Dict
import pyperclip as pyperclip
import requests

# graphQL Query
# TODO: more fields used as needed, for later processing
QUERY_STRING = """

query GetMedia($status: [MediaStatus!], $format: [MediaFormat!], $season: MediaSeason, $year: Int){
    Page{
        media(status_in: $status, format_in: $format, season: $season, seasonYear: $year){
            title{
                romaji
                english
                native
            }
            id
            startDate{
                year
                month
                day
            }
            endDate{
                year
                month
                day
            }
            episodes
            seasonInt
            seasonYear
            season
            format
            status
            duration
            genres
            meanScore
            popularity
            trending
            stats{
                scoreDistribution{
                    score
                    amount
                }
                statusDistribution{
                    status
                    amount
                }
            }
        }
    }
}

"""

# variables to filter graphQL by
VARIABLES = {
    "status": ["RELEASING", "NOT_YET_RELEASED"],
    "format": ["TV", "MOVIE", "TV_SHORT", "OVA", "ONA"],
    "year": 2024,
    "season": "SUMMER"
}


# API endpoint
GRAPH_QL_URL = 'https://graphql.anilist.co/'


def query_graphql(query: str, variables: dict, url: str):
    """
    Query a GraphQL API using the provided query and variables.

    :param query: The GraphQL query to execute, as a string.
    :type query: str
    :param variables: A dictionary of variables to pass in the query.
    :type variables: dict, optional
    :param url: The URL of the GraphQL API endpoint.
    :type url: str

    :return The response data from the GraphQL API, as a dictionary. If the response status code is not 200, returns None.
    :rtype dict
    """
    # Prepare the request headers
    headers = {
        'Content-Type': 'application/json',
        # Add any other headers as needed
    }

    # Prepare the request payload
    request_data = {
        'query': query,
        'variables': variables,
    }

    # Send the POST request
    response = requests.post(url, headers=headers, json=request_data)

    if response.status_code == 200:
        data = response.json()

        return data
    else:
        return None


def process_graphql(response_data: Dict):
    """
    Process GraphQL response data and extract media information in the format [romaji, english, start_date_str].
    This function processes the provided GraphQL response data and extracts relevant information about media objects.
    It returns a list of tuples containing the romaji name, English name, and start date string for each media object.
    The returned list is sorted by English title.

    :param response_data: The GraphQL response data dictionary.
    :type response_data: dict

    :return A sorted list of extracted media information based on English title.
    :rtype: list
    """
    # return this format: [romaji, english, start_date_str]
    media_object = response_data['data']['Page']['media']

    extracted_elements = []

    for element in media_object:
        start_date = element['startDate']
        start_date_format = "{}.{}.{}".format

        # check for a set start date
        if start_date['year'] is not None and start_date['month'] is not None and start_date['day'] is not None:
            start_date_str = start_date_format(start_date['day'], start_date['month'], start_date['year'])
        else:
            # fallback date
            start_date_str = start_date_format(1, 1, 1999)

        romaji_name = ""
        english_name = ""

        # check for romaji title of the series
        if "romaji" in element['title'] and element['title']['romaji'] is not None:
            romaji_name = element['title']['romaji']

        # check for english title of the series
        if "english" in element['title'] and element['title']['english'] is not None:
            english_name = element['title']['english']

        extracted_elements.append([romaji_name, english_name, start_date_str])

    return sorted(extracted_elements, key=lambda x: x[1])


def tabulate_anichart_data(data_set: List[List[str]]):
    """
    Tabulates and copies AniChart data to the clipboard.

    This function takes in a list of lists containing string data, formats it into a tabulated string,
    and then prints and copies it to the clipboard. The function also prints the total number of elements in the input data set.

    :param data_set: A list of lists containing string data.
    :type data_set: List[List[str]]
    :rtype: None
    """
    print('\n--------------------\n')

    string_to_copy = ""
    for entry in data_set:
        # assemble tabulated data
        loop_string = "{} \t {} \t {} \n".format(*entry)
        string_to_copy += loop_string

    print(string_to_copy)
    pyperclip.copy(string_to_copy)

    print('\n\n--------------------\n\n')

    print("Elements: {}".format(len(data_set)))


def extract_graphql_data(status_var: List[str] = None, format_var: List[str] = None, year_var: int = None, season_var: str = None):
    """
    Extracts and processes GraphQL data.

    :param status_var: A list of strings representing the statuses to filter by, defaults to None.
    :type status_var: list[str](, optional)
    :param format_var: A list of strings representing the formats to filter by, defaults to None.
    :type format_var: list[str](, optional)
    :param year_var: An integer representing the year to filter by, defaults to None.
    :type year_var: int(, optional)
    :param season_var: A string representing the season to filter by, defaults to None.
    :type season_var: str(, optional)

    :return: None
    :rtype: None
    """
    # overwrite values if set as parameters
    if status_var:
        VARIABLES['status'] = status_var
    if format_var:
        VARIABLES['format'] = format_var
    if year_var:
        VARIABLES['year'] = year_var
    if season_var:
        VARIABLES['season'] = season_var

    response_data = query_graphql(QUERY_STRING, VARIABLES, GRAPH_QL_URL)
    if response_data is None:
        print("No data returned from query graphql!")
        exit()
    processed_data = process_graphql(response_data)
    tabulate_anichart_data(processed_data)


if __name__ == '__main__':
    # status: FINISHED, RELEASING, NOT_YET_RELEASED, CANCELLED, HIATUS
    # formats: TV, TV_SHORT, MOVIE, SPECIAL, OVA, ONA, MUSIC, MANGA, NOVEL, ONE_SHOT
    extract_graphql_data(status_var=None, format_var=["TV"], year_var=2024, season_var="SUMMER")

