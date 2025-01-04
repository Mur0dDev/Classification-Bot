import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsClient:
    def __init__(self, credentials_file: str, spreadsheet_name: str):
        """
        Initialize the Google Sheets client.
        :param credentials_file: Path to the credentials.json file.
        :param spreadsheet_name: Name of the spreadsheet.
        """
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.client = None
        self.sheet = None

    def authenticate(self):
        """
        Authenticate and authorize with the Google Sheets API.
        """
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open(self.spreadsheet_name)
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with Google Sheets: {e}")

    def append_data(self, worksheet_name: str, data: list):
        """
        Append a row of data to the specified worksheet.
        :param worksheet_name: Name of the worksheet to append data to.
        :param data: List of data to append as a row.
        """
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            worksheet.append_row(data)
        except Exception as e:
            raise RuntimeError(f"Failed to append data to worksheet '{worksheet_name}': {e}")

    def get_row_count(self, worksheet_name: str) -> int:
        """
        Get the number of rows currently in the worksheet.
        :param worksheet_name: Name of the worksheet.
        :return: Number of rows in the worksheet (excluding the header row).
        """
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            return len(worksheet.get_all_values())  # Count rows in the sheet
        except Exception as e:
            raise RuntimeError(f"Failed to get row count for worksheet '{worksheet_name}': {e}")