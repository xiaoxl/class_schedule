import pandas as pd
import numpy as np
from datetime import datetime, time
import os

def parse_time(s):
    if not pd.isna(s):
        for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%H%M", "%H%M.0"):
            try:
                return datetime.strptime(s.zfill(4), fmt).time()
            except ValueError:
                continue
    return np.nan  # if no format matches


def merge_rows(df):
    rf = df.to_dict()
    for c in rf.keys():
        if c != 'Cross-List':
            LL = list(rf[c].values())
            if LL[0] == LL[1]:
                rf[c] = [LL[0]]
            elif not pd.isna(LL[0]) and pd.isna(LL[1]):
                rf[c] = [LL[0]]
            elif pd.isna(LL[0]) and not pd.isna(LL[1]):
                rf[c] = [LL[1]]
            elif pd.isna(LL[0]) and pd.isna(LL[1]):
                rf[c] = [LL[0]]
            else:
                if c == 'Beginning Time':
                    rf[c] = min(LL[0], LL[1])
                elif c == 'Ending Time':
                    rf[c] = max(LL[0], LL[1])
                else:
                    rf[c] = [f'{LL[0]}-{LL[1]}']
        else:
            rf[c] = [np.nan]
            
    return pd.DataFrame(rf)


def merge_cross_list(df):
    cl = df['Cross-List'].dropna().drop_duplicates()
    for c in cl:
        df = pd.concat([df, merge_rows(df[df['Cross-List']==c])])
        df = df[df['Cross-List']!=c]
    return df.drop(columns=['Cross-List'])


def read_from_ad(df):
    sf = df['Course/Section'].str.extract(r'(?P<Subject>[A-Z]+) (?P<Number>[\w-]+)/(?P<Section>\w+) (?P<Type>\w+)')
    # sf = sf.drop(columns=['Type'])
    sf['Instructor Name'] = df['Instructor']
    sf['Meeting Days'] = df['Days Met'].str.upper()
    sf['Beginning Time'] = df['Start Time'].apply(parse_time)
    sf['Ending Time'] = df['End Time'].apply(parse_time)
    sf['Room'] = df['Room']
    sf['Credits'] = sf['Number'].str[-1].astype(int)
    sf['Cross-List'] = df['Cross-List']
    if 'Catalog Title' in df.columns:
        sf['Title'] = df['Catalog Title']
    else:
        sf['Title'] = np.nan
    sf = merge_cross_list(sf)
    sf = clean_df(sf)
    return sf


def roomnumber(x):
    return int(x) if str(x).isdigit() else x

def merge_building_room(x):
    if pd.isna(x['Building']):
        t = np.nan
    else:
        t = f'{x['Building']} {roomnumber(x['Room'])}'
    return t


def read_from_argos(df):
    sf = df[['Subject', 'Number', 'Section', 'Instructor Name', 'Meeting Days']].copy()
    sf['Number'] = sf['Number'].astype(str)
    sf['Beginning Time'] = df['Beginning Time'].astype(str).apply(parse_time).copy()
    sf['Ending Time'] = df['Ending Time'].astype(str).apply(parse_time).copy()
    sf['Room'] = df[["Building", "Room"]].apply(merge_building_room, axis=1).copy()
    if 'Course Credit Hours' in df.columns:
        sf['Credits'] = df['Course Credit Hours'].copy().astype(int)
    else:
        sf['Credits'] = df['Number'].astype(str).str[-1].astype(int)
    if 'Cross-List' in df.columns:
        sf['Cross-List'] = df['Cross-List']
    else:
        sf['Cross-List'] = np.nan
    if 'Type' in df.columns:
        sf['Type'] = df['Type']
    else:
        sf['Type'] = np.nan
    if 'Catalog Title' in df.columns:
        sf['Title'] = df['Catalog Title'].copy()
    else:
        sf['Title'] = ''
    sf = merge_cross_list(sf)
    sf = clean_df(sf)
    return sf


def clean_df(df):
    df['Instructor Name'] = df['Instructor Name'].str.strip()
    df['Subject'] = df['Subject'].str.strip()
    df['Number'] = df['Number'].astype(str).str.strip()
    df['Section'] = df['Section'].astype(str).str.strip()
    df['Meeting Days'] = df['Meeting Days'].str.upper()
    df['Room'] = df['Room'].str.strip()
    df = df[df['Section'].str.match(r"^(AT|TC|[0-9]|M|H|F)")]
    return df


def read_from_file(filename):
    
    fileext = os.path.splitext(str(filename))[-1].lstrip('.')
    # if isinstance(filename, str):
    #     fileext = filename.split('.')[-1]
    # else:
    #     fileext = filename.name.split('.')[-1]
    if  fileext in ['xlsx', 'xls']:
        df = pd.read_excel(filename)
    elif fileext == 'csv':
        df = pd.read_csv(filename)

    if 'Course/Section' in df.columns:
        sf = read_from_ad(df)
    else:
        sf = read_from_argos(df)
    
    return sf

if __name__ == '__main__':
    # df1 = read_from_file('src/MAPS fall 25.xlsx')
    # df2 = read_from_file('src/schedule.xlsx')
    df3 = read_from_file('src/MAPS 202620 9.12.xlsx')

