"""This module has functions that are useful in other parts of the
project. For example,

* some convenience functions for gspread

"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pdb


def iter_worksheet(spreadsheet, worksheet_name,
                   as_dict=True, header_row=1):
    """Get all rows of one worksheet of a spreadsheet, either in
    dictionary format (as_dict=True) or as lists of cell values. This
    is analogous iterating over csv.reader or csv.DictReader.

    """
    # raise error if parameters are not valid
    if as_dict and header_row is None:
        raise ValueError("must have header row to get as dictionary")

    # store whether there is a header for convenience
    has_header = header_row is not None

    # get worksheet
    worksheet = spreadsheet.worksheet(worksheet_name)

    # read worksheet as a list of lists
    raw_row_list = worksheet.get_all_values()

    # row_index stores the row we're going to read
    row_index = 2
    if has_header:
        row_index = header_row

    # if reading as dictionary or skipping header row, advance the
    # index once and store the header row
    if as_dict or has_header:
        header = raw_row_list[row_index - 1]
        row_index += 1

    # yield either dictionaries or lists depending on the as_dict
    # parameter
    for row in raw_row_list[row_index:]:
        if as_dict:
            row_dict = dict(zip(header, row))
            yield row_dict
        else:
            yield row
    # pdb.set_trace()


def gspread_connection(json_configuration_file):
    """Return an authorized connection to a google spreadsheet that has
    been shared with the `client_email` address in the configuration
    file.

    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_configuration_file,
        scopes=['https://spreadsheets.google.com/feeds'],
    )
    client = gspread.authorize(credentials)
    return client


def gspread_spreadsheet(json_configuration_file, spreadsheet_url):
    """Return an gspread google spreadsheet that has been shared with the
    `client_email` address in the configuration file.

    """
    connection = gspread_connection(json_configuration_file)

    # throw an informative error if we can't open the spreadsheet
    try:
        spreadsheet = connection.open_by_url(spreadsheet_url)
    except gspread.exceptions.SpreadsheetNotFound:
        msg = (
            "Could not open '{}'. Is it shared with the service account "
            "email? You can find the service account email as "
            "'client_email' in '{}'"
        ).format(
            spreadsheet_url,
            json_configuration_file,
        )
        raise gspread.exceptions.SpreadsheetNotFound(msg)
    else:
        return spreadsheet
