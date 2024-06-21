import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetAPI:
    """Client for Google Sheets API."""

    def __init__(self, service_account_file: str = None, spreadsheet_id: str = None):
        """Instantiate GoogleSheetAPI object."""
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_file

        creds, _ = google.auth.default()
        self._service = build("sheets", "v4", credentials=creds)
        self.spreadsheet_id = spreadsheet_id or os.environ["SPREADSHEET_ID"]

    def get_values(self, range_name: str):
        """Get values from Google Sheet in range."""
        result = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        return rows


if __name__ == "__main__":
    # Pass: spreadsheet_id, and range_name
    get_values("1UX91fvcKfvy7hGlUDzfqSEzsfMZMO9pkRDAzhhBOx0E", "A1:C2")
