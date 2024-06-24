import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import argparse


class GoogleSheetAPI:
    """Client for Google Sheets API."""

    def __init__(self, service_account_file: str = None, spreadsheet_id: str = None):
        """Instantiate GoogleSheetAPI object."""
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_file

        creds, _ = google.auth.default()
        self._service = build("sheets", "v4", credentials=creds)
        self.spreadsheet_id = spreadsheet_id or os.environ["SPREADSHEET_ID"]
        self.funding_rate_sheet = "FundingRate"

    def get_values(self, range_name: str = "A1:Z10000"):
        """Get values from Google Sheet in range."""
        range_ = f"{self.funding_rate_sheet}!{range_name}"
        result = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range=range_)
            .execute()
        )
        rows = result.get("values", [])
        return rows

    def put_values(self, values: list[list], range_name: str) -> None:
        range_ = f"{self.funding_rate_sheet}!{range_name}"
        body = {"values": values}
        result = (
            self._service.spreadsheets()
            .values()
            .update(
                spreadsheetid=self.spreadsheet_id,
                range=range_,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        return result


def main():
    """Main function that instantiates GoogleSheetAPI and updates"""
    args = argparse.ArgumentParser()
    args.add_argument("--service_account_file", help="Service account file")
    args.add_argument("--spreadsheet_id", help="Spreadsheet ID")
    args = args.parse_args()

    client = GoogleSheetAPI()
    print(client.get_values())
