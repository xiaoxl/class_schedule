import pandas as pd
from generateoutput import save_reports

generated_file = 'out/26s_init.csv'

sf = pd.read_csv(generated_file)

def assign_section(df, cnumber, section, instructor):
    df.loc[(df['Number']==cnumber) & (df['Section']==section), 'Instructor Name'] = instructor
    return df.loc[(df['Number']==cnumber) & (df['Section']==section)]

def assign_room(df, cnumber, section, building, room, days=None):
    if days is None:
        df.loc[(df['Number']==cnumber) & (df['Section']==section), 'Building'] = building
        df.loc[(df['Number']==cnumber) & (df['Section']==section), 'Room'] = room
    else:
        df.loc[(df['Number']==cnumber) & (df['Section']==section) & (df['Meeting Days']==days), 'Building'] = building
        df.loc[(df['Number']==cnumber) & (df['Section']==section) & (df['Meeting Days']==days), 'Room'] = room
    return df.loc[(df['Number']==cnumber) & (df['Section']==section)]


def remove_section(df, cnumber, section):
    df = df.loc[(df['Number']!=cnumber) | (df['Section']!=section)]
    return df

def add_section(df, cnumber, section, instructor):
    newrow = pd.DataFrame({
        'Term Code': 202620,
        'Subject': ['MATH'],
        'Number': [cnumber],
        'Section': [section],
        'Instructor Name':[instructor],
        'Course Credit Hours': cnumber %10,
        })
    df = pd.concat([df, newrow], ignore_index=True)
    return df

def assign_time(df, cnumber, section, newtime, days=None, duration=50, forced=False):
    dh = duration//60
    dm = duration%60
    bh = newtime//100
    bm = newtime%100
    em = dm + bm
    emh = em//60
    realem = em%60
    realeh = bh + dh + emh
    endtime = int(f'{realeh}{realem}')
    if days is None:
        df.loc[(df['Number']==cnumber) & (df['Section']==section), 'Beginning Time'] = newtime
        df.loc[(df['Number']==cnumber) & (df['Section']==section), 'Ending Time'] = endtime
    else:
        if forced:
            df.loc[(df['Number']==cnumber) & (df['Section']==section), 'Meeting Days'] = days
        df.loc[(df['Number']==cnumber) & (df['Section']==section) & (df['Meeting Days']==days), 'Beginning Time'] = newtime
        df.loc[(df['Number']==cnumber) & (df['Section']==section) & (df['Meeting Days']==days), 'Ending Time'] = endtime
    
    return df.loc[(df['Number']==cnumber) & (df['Section']==section)]

def assign_day(df, cnumber, section, olddays, newday):
    df.loc[(df['Number']==cnumber) & (df['Section']==section) & (df['Meeting Days']==olddays), 'Meeting Days'] = newday        
    return df.loc[(df['Number']==cnumber) & (df['Section']==section)]

assign_room(sf, 1113, '006', 'Corley', 102)
assign_room(sf, 2703, '003', 'Corley', 102)


assign_section(sf, 2223, '003', 'Cox, Allie M.')
# change_time(sf, 2223, '001', 1100)
assign_section(sf, 1203, 'TC1', 'Bain, Leslie M.')
assign_section(sf, 1003, '004', 'Growns, Landon C.')
assign_section(sf, 1003, '006', 'King, Jamie L.')
assign_section(sf, 2703, '003', 'Xiao, Xinli')
assign_time(sf, 2703, '003', 1300)


assign_section(sf, 2703, '001', 'Jordan, Susan M.')

assign_section(sf, 2703, 'TC1', 'Overduin, Matthew D.')

assign_section(sf, 2914, '002', 'Jordan, Susan M.')
# assign_section(sf, 2914, '002', 'Overduin, Matthew D.')

assign_time(sf, 2914, '001', 900, 'MWF')
assign_time(sf, 2914, '001', 930, 'R', 80)

assign_section(sf, 2924, '002', 'Limperis, Thomas G.')
# assign_room(sf, 2924, '002', 'Corley', 267)
# assign_time(sf, 2924, '002', 1100, 'MWF')
# assign_time(sf, 2924, '002', 1100, 'T', 80)

assign_section(sf, 2924, '003', 'Myers, Jeanine L.')


assign_time(sf, 2924, '003', 1000, 'MWF')
assign_time(sf, 2924, '003', 930, 'R', 80)
assign_room(sf, 2924, '003', 'Corley', 268)

assign_section(sf, 2924, '001', 'Myers, Jeanine L.')
assign_time(sf, 2924, '001', 1300, 'MWF')
assign_time(sf, 2924, '001', 1300, 'R', 80)
assign_room(sf, 2924, '001', 'Corley', 102)

assign_time(sf, 3153, '001', 900)
assign_time(sf, 903, '002', 1000)


assign_time(sf, 2223, '001', 1100)
assign_time(sf, 2223, '002', 1100, duration=80)
assign_room(sf, 2223, '002', 'Corley', 103)

assign_room(sf, 1914, '001', 'Corley', 267, 'R')
# assign_time(sf, 1914, '001', 930, 'R', 80)



assign_section(sf, 2934, '002', 'Myers, Jeanine L.')
assign_room(sf, 2934, '002', 'Corley', 101)
assign_day(sf, 2934, '002', 'T', 'R')

assign_day(sf, 2924, '002', 'R', 'T')


assign_section(sf, 1914, '002', 'Jordan, Susan M.')
assign_section(sf, 1914, '003', 'Ballard, Kasey L.')

assign_section(sf, 1003, '003', 'Ballard, Kasey L.')
assign_section(sf, 803, '003', 'Ballard, Kasey L.')
# change_time(sf, 1914, '003', (1000,930), 'MWFT')

assign_room(sf, 803, '001', 'Corley', 103)

assign_section(sf, 903, '002', 'Winn, Janet L.')
assign_section(sf, 1113, '002', 'Winn, Janet L.')
assign_time(sf, 1113, '002', 800, duration=80)
assign_time(sf, 903, '002', 800)
assign_room(sf, 903, '002', 'Corley', 104)
assign_room(sf, 1113, '002', 'Corley', 104)

assign_section(sf, 3203, '001', 'Myers, Jeanine L.')
assign_time(sf, 3203, '001', 1400)
assign_room(sf, 3203, '001', 'Corley', 104)
# assign_room(sf, 3203, '001', 'Rothwell', 206)

assign_section(sf, 2914, '003', 'Limperis, Thomas G.')
assign_section(sf, 2703, '002', 'Limperis, Thomas G.')
assign_room(sf, 2703, '002', 'Rothwell', 206)
assign_room(sf, 2914, '003', 'Rothwell', 211)
# assign_room(sf, 2914, '003', 'Rothwell', 211)


assign_time(sf, 3113, '001', 1100)
assign_room(sf, 3113, '001', 'Rothwell', 213)


assign_time(sf, 1003, '003', 1400)
assign_time(sf, 1003, '004', 1300, 'TR')

assign_time(sf, 1914, '003', 1000, 'MWF')
assign_time(sf, 1914, '003', 930, 'T', 80)
assign_room(sf, 1914, '003', 'Corley', 267)

assign_time(sf, 1914, '001', 900, 'MWF')
assign_time(sf, 1914, '001', 930, 'R', 80)
assign_room(sf, 1914, '001', 'Corley', 267, 'MWF')

assign_room(sf, 2163, '003', 'Corley', 104)

assign_section(sf, 2163, '004', 'Overduin, Matthew D.')



assign_time(sf, 2243, '002', 930, duration=80)



assign_room(sf, 4971, '001', 'Corley', 267)

assign_time(sf, 2163, '003', 1300, duration=80)

# assign_section(sf, 1003, '005', 'King, Jamie L.')
assign_day(sf, 1003, '005', 'TR', 'MWF')
assign_time(sf, 1003, '005', 1000)
assign_room(sf, 1003, '005', 'Corley', 104)

assign_day(sf, 1003, '004', 'MWF', 'TR')
assign_time(sf, 1003, '004', 930, duration=80)
assign_room(sf, 1003, '004', 'Rothwell', 221)

# assign_day(sf, 2243, '001', 'MWF', 'TR')
assign_time(sf, 2243, '001', 1300)
assign_room(sf, 2243, '001', 'Corley', 104)


# assign_room(sf, 3183, '001', 'Corley', 102)

sf = add_section(sf, 3033, 'AT1', 'Taylor, Teresa L.')

sf = remove_section(sf, 2163, '004')
sf = remove_section(sf, 2703, '003')

# sf.to_csv('out/26s_ver1.csv', index=False)
# sf.to_excel('out/26s_ver1.xlsx', index=False)

save_reports(sf, 'ver3')
