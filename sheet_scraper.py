from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


import pandas as pd
import os
import pickle
import re


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# here enter the id of your google sheet
SPREADSHEET_ID_input = '1gEUMO67MNcgKsz40Wfx5GinMjJoLWGm9tSyLJ2MCnuc'
RANGE_NAME = 'A4:AD100'
# RANGE_NAME = 'A4:C18'  # keith
# RANGE_NAME = 'A4:L18'  # rick
CREDENTIAL_FILE = 'credentials.json'

MAX_PRODUCTS = 20


class ScraleScraper:
    def __init__(self, sheet_ID, sheet_range):
        self.sheet_ID = sheet_ID
        self.sheet_range = sheet_range

        self.sheet = None
        self.raw_data = None
        self.data = None
        self.service = None

        self.range_split = None
        self.rrows = []
        self.rcols = []

        self.who_orders = None
        self.df = None
        self.df_simple = None

        self.re_url = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            # domain...
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def get_sheet(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIAL_FILE, SCOPES)  # here enter the name of your downloaded JSON file
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

        self.sheet = self.service.spreadsheets()
        self.raw_data = self.sheet.values().get(spreadsheetId=self.sheet_ID,
                                                range=self.sheet_range).execute()
        self.data = self.raw_data.get('values', [])

    def parse_sheet(self):
        # parse range from RANGE_NAME
        self.range_split = self.split_range()

        # init a dataframe
        df_col_names = ['Wie', 'Wat', 'Hoeveel', 'Prijs', 'Link']
        self.df = pd.DataFrame()

        # get input names
        name_range = '%s%s:%s%s' % (self.rcols[0], self.rrows[0], self.rcols[1], self.rrows[0])

        self.who_orders = self.sheet.values().get(spreadsheetId=self.sheet_ID,
                                                  range=name_range).execute().get('values', [])
        self.who_orders = [x for x in self.who_orders[0] if x]

        print(self.who_orders)

        # loop over names
        for num, name in enumerate(self.who_orders):
            # if num > 3:
            #     continue

            tmp_col = num * 3 + 1
            tmp_row = int(self.rrows[0]) + 2
            data_range = self.create_range(tmp_row, tmp_col, tmp_row + MAX_PRODUCTS, tmp_col + 2)
            link_range = self.create_range(tmp_row, tmp_col, tmp_row + MAX_PRODUCTS, tmp_col)

            # GET TEXT DATA (naam, aantal, prijs)
            data_persoon = self.sheet.values().get(spreadsheetId=self.sheet_ID,
                                                   range=data_range).execute().get('values', [])

            # GET HYPERLINKS
            link_tmp = self.sheet.get(spreadsheetId=self.sheet_ID, ranges=link_range,
                                      fields="sheets/data/rowData/values/hyperlink").execute()
            self.a = link_tmp
            len(self.a['sheets'][0]['data'][0]['rowData'])
            links = self.flatten_link_dict(link_tmp)

            # get indices of empty rows
            ind_empty = []
            for i, row in enumerate(data_persoon):
                if not row:
                    ind_empty.append(i)
                else:
                    if not row[0]:
                        ind_empty.append(i)

            for i in sorted(ind_empty, reverse=True):
                del data_persoon[i]
                if i < len(links):
                    del links[i]

            # CHECK IF TEXT DATA CONTAINS URLS
            # and put everything in a nice nested list
            ind_to_remove = []
            for num, row in enumerate(data_persoon):
                # if num in ind_empty:
                #     continue
                if row:
                    # put in some nice name if not existent
                    if links[num] and self.is_url(links[num]):
                        if self.is_url(row[0]):
                            data_persoon[num][0] = self.get_name_url(row[0])
                        # and add the links to the data list
                        # print(links[num])
                        if self.is_url(links[num]):
                            data_persoon[num].append(links[num])
                    else:
                        ind_to_remove.append(num)

            # remove nonsense rows
            for i in sorted(ind_to_remove, reverse=True):
                del data_persoon[i]

            # add name to data_persn list for dataframe
            for row in data_persoon:
                row.insert(0, name)
            df_pers = pd.DataFrame(data_persoon, columns=df_col_names)
            self.df = self.df.append(df_pers)

        # do some things on dataframe
        # convert hoeveel to ints
        self.df['Hoeveel'] = pd.to_numeric(self.df['Hoeveel'], errors='coerce')
        self.df['Hoeveel'] = self.df['Hoeveel'].fillna(1)
        self.df['Prijs'] = self.df['Prijs'].str.replace(',', '.')
        self.df['Prijs'] = pd.to_numeric(self.df['Prijs'], errors='coerce')

    def simplify_bestellijst(self):
        tmp = self.df[['Hoeveel', 'Link']]
        self.df_simple = tmp.groupby(['Link']).sum()
        self.df_simple = self.df_simple.reset_index()

    def doe_het_allemaal(self):
        self.get_sheet()
        self.parse_sheet()
        self.simplify_bestellijst()

    def split_range(self):
        tmp = self.sheet_range.split(':')
        self.rrows.append(''.join(filter(str.isnumeric, tmp[0])))
        self.rrows.append(''.join(filter(str.isnumeric, tmp[1])))
        self.rcols.append(''.join(filter(str.isalpha, tmp[0])))
        self.rcols.append(''.join(filter(str.isalpha, tmp[1])))
        return [self.rrows, self.rcols]

    def create_range(self, row1, col1, row2, col2):

        tmp = '%s%s:%s%s' % (self.col_num_to_str(col1), str(row1),
                             self.col_num_to_str(col2), str(row2))
        return tmp.upper()

    def is_url(self, url):
        return re.match(self.re_url, url)

    @staticmethod
    def col_num_to_str(col):
        tmp = ''
        if col > 26:
            tmp += 'A'
            col -= 26
        return tmp + chr(col + 96)

    @staticmethod
    def flatten_link_dict(link_dict):
        result = []
        tmp_data = link_dict['sheets'][0]['data'][0]['rowData']
        for item in tmp_data:
            if 'values' in item:
                result.append(item['values'][0]['hyperlink'])
            else:
                result.append(None)
        return result

    @staticmethod
    def get_name_url(url):
        tmp = url.split('/')
        return tmp[-1]


if __name__ == '__main__':
    SS = ScraleScraper(SPREADSHEET_ID_input, RANGE_NAME)
    # SS.get_sheet()
    # SS.parse_sheet()
    # SS.simplify_bestellijst()
    SS.doe_het_allemaal()

    # more options can be specified also
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'max_colwidth', 40, 'display.width', 150):
        print(SS.df)
        print('==================================')
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'max_colwidth', 120, 'display.width', 150):
        print(SS.df_simple)

    print()
    print('done')
