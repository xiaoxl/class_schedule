import pandas as pd
import numpy as np
from datetime import datetime


def parse_time(s):
    if not pd.isna(s):
        # s = str(s)
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
                rf[c] = [f'{LL[0]}-{LL[1]}']
        else:
            # Keep Cross-List column as is (take first value)
            rf[c] = [np.nan]
            
    return pd.DataFrame(rf)


def merge_cross_list(df):
    cl = df['Cross-List'].dropna().drop_duplicates()
    for c in cl:
        df = pd.concat([df, merge_rows(df[df['Cross-List']==c])])
        df = df[df['Cross-List']!=c]
    return df.drop(columns=['Cross-List'])


def read_from_ad(filename):
    df = pd.read_excel(filename)
    sf = df['Course/Section'].str.extract(r'(?P<Subject>[A-Z]+) (?P<Number>[\w-]+)/(?P<Section>\w+) (?P<Type>\w+)')
    sf = sf.drop(columns=['Type'])
    sf['Instructor Name'] = df['Instructor']
    sf['Meeting Days'] = df['Days Met'].str.upper()
    sf['Beginning Time'] = df['Start Time'].apply(parse_time)
    sf['Ending Time'] = df['End Time'].apply(parse_time)
    sf['Room'] = df['Room']
    # sf[['Building', 'Room']] = df['Room'].str.extract(r'(?P<Building>\w+) (?P<Room>\w+)')
    sf['Cross-List'] = df['Cross-List']
    sf = merge_cross_list(sf)
    sf = sf[sf['Section'].str.match(r"^(0|M|H|F|AT|TC)")]
    sf['Room'] = sf['Room'].str.strip()
    sf['Subject'] = sf['Subject'].str.strip()
    sf['Number'] = sf['Number'].str.strip()
    sf['Section'] = sf['Section'].str.strip()
    sf['Instructor Name'] = sf['Instructor Name'].str.strip()
    return sf


def merge_building_room(x):
    if pd.isna(x['Building']):
        t = np.nan
    else:
        t = f'{x['Building']} {int(x['Room'])}'
    return t


def read_from_argos(filename):
    df = pd.read_excel(filename)
    sf = df[['Subject', 'Number', 'Section', 'Instructor Name', 'Meeting Days']].copy()
    sf['Number'] = sf['Number'].astype(str)
    sf['Beginning Time'] = df['Beginning Time'].astype(str).apply(parse_time).copy()
    sf['Ending Time'] = df['Ending Time'].astype(str).apply(parse_time).copy()
    sf['Room'] = df[["Building", "Room"]].apply(merge_building_room, axis=1).copy()
    if 'Cross-List' in df.columns:
        sf['Cross-List'] = df['Cross-List']
    else:
        sf['Cross-List'] = np.nan
    sf = merge_cross_list(sf)
    sf = sf[sf['Section'].str.match(r"^(0|M|H|F|AT|TC)")]
    sf['Room'] = sf['Room'].str.strip()
    sf['Subject'] = sf['Subject'].str.strip()
    sf['Number'] = sf['Number'].str.strip()
    sf['Section'] = sf['Section'].str.strip()
    sf['Number'] = sf['Number'].str.strip()
    sf['Meeting Days'] = sf['Meeting Days'].str.upper()
    return sf


def read_from_file(filename):
    df = pd.read_excel(filename)
    if 'Course/Section' in df.columns:
        sf = read_from_ad(filename)
    else:
        sf = read_from_argos(filename)
    return sf

if __name__ == '__main__':
    df1 = read_from_ad('src/MAPS fall 25.xlsx')
    df2 = read_from_argos('src/schedule.xlsx')
