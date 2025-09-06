import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from readfiles import read_from_file, parse_time


def assign_section(df, subject, cnumber, section, instructor):
    df.loc[
        (df['Subject'] == subject) &
        (df['Number'] == str(cnumber)) &
        (df['Section'] == section),
        'Instructor Name'
    ] = instructor
    return df.loc[
        (df['Subject']==subject) &
        (df['Number']==str(cnumber)) &
        (df['Section']==section)
    ]

def assign_room(df, subject, cnumber, section, room, days=None):
    if days is None:
        df.loc[
            (df['Subject'] == subject) &
            (df['Number'] == str(cnumber)) &
            (df['Section'] == section),
            'Room'
        ] = room
    else:
        df.loc[
            (df['Subject'] == subject) &
            (df['Number'] == str(cnumber)) &
            (df['Section'] == section) &
            (df['Meeting Days'] == days),
            'Room'
        ] = room
    return df.loc[
        (df['Subject']==subject) &
        (df['Number']==str(cnumber)) &
        (df['Section']==section)
    ]

def assign_time(df, subject, cnumber, section, newtime, days=None, duration=50):
    btime = parse_time(str(newtime))
    dt = datetime.combine(datetime.now().date(), btime)
    etime = (dt + timedelta(minutes=duration)).time()
    if days is None:
        df.loc[
            (df['Subject'] == subject) &
            (df['Number'] == str(cnumber)) &
            (df['Section'] == section),
            'Beginning Time'
        ] = btime
        df.loc[
            (df['Subject'] == subject) &
            (df['Number'] == str(cnumber)) &
            (df['Section'] == section),
            'Ending Time'
        ] = etime
    else:
        df.loc[
            (df['Subject'] == subject) &
            (df['Number'] == str(cnumber)) &
            (df['Section'] == section) &
            (df['Meeting Days'] == days),
            'Beginning Time'
        ] = btime
        df.loc[
            (df['Subject'] == subject) &
            (df['Number'] == str(cnumber)) &
            (df['Section'] == section) &
            (df['Meeting Days'] == days),
            'Ending Time'
        ] = etime
    return df.loc[
        (df['Subject']==subject) &
        (df['Number']==str(cnumber)) &
        (df['Section']==section)
    ]

def assign_days(df, subject, cnumber, section, olddays, newdays):
    df.loc[
        (df['Subject'] == subject) &
        (df['Number'] == str(cnumber)) &
        (df['Section'] == section) &
        (df['Meeting Days'] == olddays),
        'Meeting Days'
    ] = newdays
    return df.loc[
        (df['Subject']==subject) &
        (df['Number']==str(cnumber)) &
        (df['Section']==section)
    ]

def remove_section(df, subject, cnumber, section):
    df = df.loc[
        (df['Subject']!=subject) | 
        (df['Number']!=str(cnumber)) | 
        (df['Section']!=section)
    ]
    return df

def add_section(df, subject, cnumber, section, instructor,
                days=np.nan, btime=np.nan, etime=np.nan, room=np.nan):
    btime = parse_time(str(btime))
    etime = parse_time(str(etime))
    newrow = pd.DataFrame({
        'Subject': [subject],
        'Number': [str(cnumber)],
        'Section': [section],
        'Instructor Name':[instructor],
        'Credits': int(cnumber) %10,
        'Meeting Days': days,
        'Beginning Time': btime,
        'Ending Time': etime,
        'Room': room,
        })
    df = pd.concat([df, newrow], ignore_index=True)
    return df


if __name__ == '__main__':
    sf = read_from_file('src/26s_init.csv')
    sf = remove_section(sf, 'MATH', 1914, '001')
    sf = add_section(sf, 'MATH', 1914, '001', 'aa', days='MWF', btime=800, etime=850, room='eee')

    assign_section(sf, 'MATH', 1914, '001', 'xdx')
    assign_room(sf, 'MATH', 1914, '001', 'xdx', 'R')
    assign_time(sf, 'MATH', 1914, '002', 930, duration=80)
    assign_time(sf, 'MATH', 1914, '002', 900, days='R', duration=50)
    assign_days(sf, 'MATH', 1914, '002', 'MWF', 'R')




