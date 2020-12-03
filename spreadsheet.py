import random
import pandas as pd
from google.oauth2 import service_account
from apiclient import discovery

class Spreadsheet():
    def __init__(self):
        scopes = [
            'https://www.googleapis.com/auth/drive', 
            'https://www.googleapis.com/auth/drive.file', 
            'https://www.googleapis.com/auth/spreadsheets'
            ]
        service_account_file = 'google-token.json'
        credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
        self.spreadsheet_id = '1dsdUbH3H73i4nXWs-_kaU5VhK9VTo_hK4lxSPeCoHTY'
        self.idx_offset = 2 # pandas_idx + idx_offset = spreadsheet_idx
        self.service = discovery.build('sheets', 'v4', credentials=credentials)

    def add_invitee(self, inviter, invitee):
        inviter = f"{inviter.name} ({inviter.id})"
        invitee = f"{invitee.name} ({invitee.id})"

        range_name = 'Family Tree!A2:A'
        response = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        tracked_users = response.get('values', [[]])
        
        user_tracked = False
        
        row_idx = 2
        for user in tracked_users[0]:
            row_idx += 1
            if user == inviter:
                user_tracked = True
                break

        if not user_tracked:
            range_name = f'Family Tree!A{row_idx}:B{row_idx}'
            self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id,
                                                        range=range_name, valueInputOption='RAW',
                                                        body=dict(values=[[inviter, invitee]])).execute()
        else:
            range_name = f'Family Tree!B{row_idx}:B{row_idx}'
            response = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            previous_invitees = response['values'][0][0]
            all_invitees = previous_invitees + ',' + invitee
            self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, valueInputOption='RAW',
                                                        range=range_name, body=dict(values=[[all_invitees]])).execute()
            
    def spreadsheet_to_pandas(self, name, start_col, end_col):
        """
        Reads the spreadsheet with the given name from start_col to end_col into a pandas DataFrame and returns it.
        Args:
            name (str): Name of the spreadsheet
            start_col (str): Start column, inclusive (A-Z).
            end_col (str): End column, inclusive (A-Z). 
        """
        range_name = f'{name}!{start_col}:{end_col}'
        response = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        data = response['values']
        return pd.DataFrame(data[1:], columns=data[0])

    def add_question(self, author, question, spiciness):
        range_name = f'Questions!A:A'
        response = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        row_idx = len(response['values']) + 1
        range_name = f'Questions!A{row_idx}:D{row_idx}'
        self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, valueInputOption='RAW',
                                                   range=range_name,
                                                    body=dict(values=[[question, spiciness, '', author.name]])).execute()
        return True
            
    def get_question(self, spiciness):
        """
        Returns an unasked question at the given spiciness level or lower, or an error message is returned.
        Args:
            spiciness (int): Spiciness of the question to retrieve
        Returns:
            str: A random unasked question or an error message.
            int: Actual spiciness of the question returned.
        """
        df = self.spreadsheet_to_pandas('Questions', 'A', 'E')
        # Find unasked questions <= spiciness level
        unasked_questions = []
        while spiciness > 0:
            unasked_df = df.loc[(df['Asked'] != 'Y') & (df['Spiciness\n(1=bland, 5=spicy)'] == str(spiciness))]
            unasked_questions = list(unasked_df['Question'])
            if unasked_questions:
                break
            spiciness -= 1
            
        if not unasked_questions:
            num_unasked = len(list(df.loc[df['Asked'] != 'Y']['Question']))
            return (f'Could not find any questions <= spiciness level. {num_unasked} total unasked questions remaining.', -1)
        # Chosen random unasked question and mark question as asked
        chosen_question = random.choice(unasked_questions)
        update_idx = df.loc[df['Question'] == chosen_question].index.values[0] + self.idx_offset
        range_name = f'Questions!C{update_idx}:C{update_idx}'
        body = {
            'values': [['Y']]
        }
        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=range_name,
            valueInputOption="USER_ENTERED", body=body).execute()

        return (chosen_question, spiciness)

    def get_book_quote(self, book_name):
        """
        Returns a random quote from the given book or None if the book doesn't have any quotes.
        Args:
            book_name (str): Name of the book to get the quote from
        Returns:
            str: A random quote from the given book.
        """
        df = self.spreadsheet_to_pandas('Quotes', 'A', 'B')
        quotes = list(df.loc[df['Book'] == book_name]['Quote'])
        if quotes:
            return random.choice(quotes)
        return None


if __name__ == '__main__':
    spreadsheet = Spreadsheet()
    print(spreadsheet.get_question(3))
    print(spreadsheet.get_book_quote("Book3"))


