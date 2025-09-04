import pandas as pd
import numpy as np
from collections import defaultdict


def compute_credits(df):
    credit_clean = df[['Instructor Name', 'Subject', 'Number', 'Section', 'Course Credit Hours']].drop_duplicates().reset_index(drop=True)
    return credit_clean[['Course Credit Hours']].groupby([credit_clean['Instructor Name']]).sum()


# def show_instructor_schedule(df, names=None):
#     if isinstance(names, str):
#         return df[df['Instructor Name']==names]
#     elif isinstance(names, np.ndarray):
#         return [df[df['Instructor Name']==i] for i in names]
#     elif isinstance(names, list):
#         return [df[df['Instructor Name']==i] for i in names]
#     else:
#         return None
    

def check_instructor_conflicts_matrix(df):
    """
    Check instructor conflicts using time-day matrix approach.
    Much more efficient than pairwise comparison.
    """
    # Filter out online courses and empty data
    data = df[
        ~df['Section'].str.startswith('AT', na=False) &
        ~df['Section'].str.startswith('F', na=False) &
        ~df['Section'].str.startswith('TC', na=False) &
        df['Meeting Days'].notna() &
        (df['Meeting Days'].str.strip() != '') &
        df['Beginning Time'].notna()
    ].copy()
    
    conflicts = []
    
    # Group by instructor
    for instructor, group in data.groupby('Instructor Name'):
        matrix = defaultdict(lambda: {'M': 0, 'T': 0, 'W': 0, 'R': 0, 'F': 0})
        course_details = defaultdict(lambda: defaultdict(list))  # Store course info
        
        for _, row in group.iterrows():
            start_time = int(float(row['Beginning Time']))
            meeting_days = row['Meeting Days'].upper()
            course_info = {
                'course': f"{row['Subject']}{row['Number']}-{row['Section']}",
                'title': row['Catalog Title'],
                'room': f"{row.get('Building', '')} {row.get('Room', '')}".strip()
            }
            
            # Parse meeting days
            for char in meeting_days:
                if char in ['M', 'T', 'W', 'R', 'F']:
                    matrix[start_time][char] += 1
                    course_details[start_time][char].append(course_info)
        
        # Check for conflicts (any cell > 1)
        for time_slot, day_counts in matrix.items():
            for day, count in day_counts.items():
                if count > 1:
                    courses = course_details[time_slot][day]
                    conflicts.append({
                        'instructor': instructor,
                        'time_slot': time_slot,
                        'day': day,
                        'count': count,
                        'courses': courses
                    })
    
    return conflicts

def check_room_conflicts_matrix(df):
    """
    Check room conflicts using time-day matrix approach.
    """
    # Filter out online courses and missing room data
    data = df[
        ~df['Section'].str.startswith('AT', na=False) &
        ~df['Section'].str.startswith('F', na=False) &
        ~df['Section'].str.startswith('TC', na=False) &
        df['Meeting Days'].notna() &
        (df['Meeting Days'].str.strip() != '') &
        df['Beginning Time'].notna() &
        df['Building'].notna() &
        df['Room'].notna()
    ].copy()
    
    # Convert Room to string and filter
    data['Room'] = data['Room'].astype(str)
    data = data[
        (data['Building'].str.strip() != '') &
        (data['Room'].str.strip() != '') &
        (data['Room'].str.strip() != 'nan')
    ]
    
    # Create room identifier
    data['room_key'] = data['Building'].str.strip() + ' ' + data['Room'].str.strip()
    
    conflicts = []
    
    # Group by room
    for room, group in data.groupby('room_key'):
        # Create time-day matrix
        matrix = defaultdict(lambda: {'M': 0, 'T': 0, 'W': 0, 'R': 0, 'F': 0})
        course_details = defaultdict(lambda: defaultdict(list))
        
        for _, row in group.iterrows():
            start_time = int(float(row['Beginning Time']))
            meeting_days = row['Meeting Days'].upper()
            course_info = {
                'course': f"{row['Subject']}{row['Number']}-{row['Section']}",
                'title': row['Catalog Title'],
                'instructor': row['Instructor Name']
            }
            
            # Parse meeting days
            for char in meeting_days:
                if char in ['M', 'T', 'W', 'R', 'F']:
                    matrix[start_time][char] += 1
                    course_details[start_time][char].append(course_info)
        
        # Check for conflicts
        for time_slot, day_counts in matrix.items():
            for day, count in day_counts.items():
                if count > 1:
                    courses = course_details[time_slot][day]
                    conflicts.append({
                        'room': room,
                        'time_slot': time_slot,
                        'day': day,
                        'count': count,
                        'courses': courses
                    })
    
    return conflicts


def md_instructor_matrix_conflicts(conflicts):
    """Print instructor conflicts in a clean format, combining same conflicts across days."""

    if not conflicts:
        t = "# ✅ \n No instructor scheduling conflicts detected!\n"
        return t
    
    t = "# ⚠️ \n INSTRUCTOR SCHEDULING CONFLICTS\n"
    t += "-" * 60
    t += "\n"
    
    # Group conflicts by instructor, time, and courses involved
    grouped_conflicts = defaultdict(list)
    
    for conflict in conflicts:
        # Create a key based on instructor, time, and courses (sorted for consistency)
        course_key = tuple(sorted([
            (course['course'], course['title'], course.get('room', ''))
            for course in conflict['courses']
        ]))
        
        key = (conflict['instructor'], conflict['time_slot'], course_key, conflict['count'])
        grouped_conflicts[key].append(conflict['day'])
    
    # Print grouped conflicts
    conflict_num = 1
    for key, days in grouped_conflicts.items():
        instructor, time_slot, course_info, count = key
        
        # Sort days and create display string
        day_order = {'M': 1, 'T': 2, 'W': 3, 'R': 4, 'F': 5}
        sorted_days = sorted(days, key=lambda d: day_order[d])
        day_str = ''.join(sorted_days)
        
        t += f"- Conflict #{conflict_num}: {instructor} on {day_str} at {time_slot}"
        t += f" - {count} classes scheduled:\n"
        
        for i, (course, title, room) in enumerate(course_info, 1):
            t += f"    {i}. {course} - {title}"
            if room:
                t += f"       Room: {room}\n"
        
        conflict_num += 1
    return t


def print_instructor_matrix_conflicts(conflicts):
    print(md_instructor_matrix_conflicts(conflicts))
    # """Print instructor conflicts in a clean format, combining same conflicts across days."""
    # t = ''
    # if not conflicts:
    #     t = "✅ No instructor scheduling conflicts detected!"
    #     return
    
    # print("⚠️ INSTRUCTOR SCHEDULING CONFLICTS (Matrix Method)")
    # print("=" * 60)
    
    # # Group conflicts by instructor, time, and courses involved
    # grouped_conflicts = defaultdict(list)
    
    # for conflict in conflicts:
    #     # Create a key based on instructor, time, and courses (sorted for consistency)
    #     course_key = tuple(sorted([
    #         (course['course'], course['title'], course.get('room', ''))
    #         for course in conflict['courses']
    #     ]))
        
    #     key = (conflict['instructor'], conflict['time_slot'], course_key, conflict['count'])
    #     grouped_conflicts[key].append(conflict['day'])
    
    # # Print grouped conflicts
    # conflict_num = 1
    # for key, days in grouped_conflicts.items():
    #     instructor, time_slot, course_info, count = key
        
    #     # Sort days and create display string
    #     day_order = {'M': 1, 'T': 2, 'W': 3, 'R': 4, 'F': 5}
    #     sorted_days = sorted(days, key=lambda d: day_order[d])
    #     day_str = ''.join(sorted_days)
        
    #     print(f"Conflict #{conflict_num}: {instructor} on {day_str} at {time_slot}")
    #     print(f"  {count} classes scheduled:")
        
    #     for i, (course, title, room) in enumerate(course_info, 1):
    #         print(f"    {i}. {course} - {title}")
    #         if room:
    #             print(f"       Room: {room}")
    #     print()
    #     conflict_num += 1


def md_room_matrix_conflicts(conflicts):
    """Print room conflicts in a clean format, combining same conflicts across days."""
    if not conflicts:
        t = "# ✅ \n No room scheduling conflicts detected!\n"
        return t
    
    t = "# ⚠️ \n ROOM SCHEDULING CONFLICTS\n"
    t += "-" * 60
    t += "\n"
    
    # Group conflicts by room, time, and courses involved
    grouped_conflicts = defaultdict(list)
    
    for conflict in conflicts:
        # Create a key based on room, time, and courses (sorted for consistency)
        course_key = tuple(sorted([
            (course['course'], course['title'], course['instructor'])
            for course in conflict['courses']
        ]))
        
        key = (conflict['room'], conflict['time_slot'], course_key, conflict['count'])
        grouped_conflicts[key].append(conflict['day'])
    
    # Print grouped conflicts
    conflict_num = 1
    for key, days in grouped_conflicts.items():
        room, time_slot, course_info, count = key
        
        # Sort days and create display string
        day_order = {'M': 1, 'T': 2, 'W': 3, 'R': 4, 'F': 5}
        sorted_days = sorted(days, key=lambda d: day_order[d])
        day_str = ''.join(sorted_days)
        
        t += f"- Conflict {conflict_num}: **{room}** on {day_str} at {time_slot}"
        t += f" - {count} classes scheduled:\n"
        
        for i, (course, title, instructor) in enumerate(course_info, 1):
            t += f"    {i}. {course} - {instructor}: {title}\n"
            # t += f"       \n"
        
        conflict_num += 1
    return t

def print_room_matrix_conflicts(conflicts):
    print(md_room_matrix_conflicts(conflicts))
    # """Print room conflicts in a clean format, combining same conflicts across days."""
    # if not conflicts:
    #     print("✅ No room scheduling conflicts detected!")
    #     return
    
    # print("⚠️ ROOM SCHEDULING CONFLICTS (Matrix Method)")
    # print("=" * 60)
    
    # # Group conflicts by room, time, and courses involved
    # grouped_conflicts = defaultdict(list)
    
    # for conflict in conflicts:
    #     # Create a key based on room, time, and courses (sorted for consistency)
    #     course_key = tuple(sorted([
    #         (course['course'], course['title'], course['instructor'])
    #         for course in conflict['courses']
    #     ]))
        
    #     key = (conflict['room'], conflict['time_slot'], course_key, conflict['count'])
    #     grouped_conflicts[key].append(conflict['day'])
    
    # # Print grouped conflicts
    # conflict_num = 1
    # for key, days in grouped_conflicts.items():
    #     room, time_slot, course_info, count = key
        
    #     # Sort days and create display string
    #     day_order = {'M': 1, 'T': 2, 'W': 3, 'R': 4, 'F': 5}
    #     sorted_days = sorted(days, key=lambda d: day_order[d])
    #     day_str = ''.join(sorted_days)
        
    #     print(f"Conflict #{conflict_num}: {room} on {day_str} at {time_slot}")
    #     print(f"  {count} classes scheduled:")
        
    #     for i, (course, title, instructor) in enumerate(course_info, 1):
    #         print(f"    {i}. {course} - {instructor}")
    #         print(f"       {title}")
    #     print()
    #     conflict_num += 1

def create_schedule_matrix_df(df, instructor_name):
    """
    Create a visual schedule matrix DataFrame for a specific instructor.
    Rows = time slots, Columns = MTWRF, Values = course count
    """
    # Filter for specific instructor and face-to-face classes
    data = df[
        (df['Instructor Name'] == instructor_name) &
        ~df['Section'].str.startswith('TC', na=False) &
        df['Meeting Days'].notna() &
        (df['Meeting Days'].str.strip() != '') &
        df['Beginning Time'].notna()
    ].copy()
    
    if data.empty:
        print(f"No face-to-face classes found for {instructor_name}")
        return None
    
    # Create matrix
    matrix = defaultdict(lambda: {'M': 0, 'T': 0, 'W': 0, 'R': 0, 'F': 0})
    
    for _, row in data.iterrows():
        start_time = int(float(row['Beginning Time']))
        meeting_days = row['Meeting Days'].upper()
        
        for char in meeting_days:
            if char in ['M', 'T', 'W', 'R', 'F']:
                matrix[start_time][char] += 1
    
    # Convert to DataFrame
    if not matrix:
        print(f"No valid schedule data for {instructor_name}")
        return None
    
    schedule_df = pd.DataFrame.from_dict(matrix, orient='index')
    schedule_df = schedule_df.sort_index()  # Sort by time
    schedule_df.index.name = 'Time'
    
    print(f"\nSchedule Matrix for {instructor_name}:")
    print("(Numbers show count of classes at each time slot)")
    print(schedule_df)
    
    # Highlight conflicts
    conflicts = (schedule_df > 1).any(axis=1)
    if conflicts.any():
        print(f"\n⚠️ Conflicts detected at times: {list(schedule_df[conflicts].index)}")
    else:
        print("\n✅ No scheduling conflicts!")
    
    return schedule_df

# Usage examples:
# instructor_conflicts = check_instructor_conflicts_matrix(df)
# print_instructor_matrix_conflicts(instructor_conflicts)
# 
# room_conflicts = check_room_conflicts_matrix(df)
# print_room_matrix_conflicts(room_conflicts)
#
# # Visualize specific instructor's schedule
# matrix_df = create_schedule_matrix_df(df, "Hogan, Jessica L.")
# import pandas as pd
# import pandas as pd

def count_sections_by_course(df):
    """
    Count the total number of sections for each course from a course schedule dataframe.
    
    Parameters:
    df (pandas.DataFrame): Course schedule dataframe with columns including 'Subject' and 'Number'
    
    Returns:
    pandas.DataFrame: DataFrame with Course and Section_Count columns, sorted by course code
    """
    # Create course code by combining Subject and Number
    df['Course'] = df['Subject'] + ' ' + df['Number'].astype(str)
    
    # Count sections for each course
    section_counts = df['Course'].value_counts().reset_index()
    section_counts.columns = ['Course', 'Section_Count']
    
    # Sort by course code for better readability
    section_counts = section_counts.sort_values('Course').reset_index(drop=True)
    
    return section_counts

def count_sections_by_course_and_format(df):
    """
    Count sections by course, separating in-person and online sections.
    
    Parameters:
    df (pandas.DataFrame): Course schedule dataframe
    
    Returns:
    pandas.DataFrame: DataFrame with Course, In_Person_Sections, Online_Sections, and Total_Sections
    """
    # Create course code by combining Subject and Number
    df['Course'] = df['Subject'] + ' ' + df['Number'].astype(str)
    
    # Identify online sections (TC sections or sections with empty Meeting Days)
    df['Is_Online'] = df['Section'].str.contains('TC', na=False) | df['Meeting Days'].isna() | (df['Meeting Days'] == '')
    
    # Count sections by course and format
    summary = df.groupby('Course').agg({
        'Is_Online': ['sum', 'count']
    }).reset_index()
    
    # Flatten column names
    summary.columns = ['Course', 'Online_Sections', 'Total_Sections']
    summary['In_Person_Sections'] = summary['Total_Sections'] - summary['Online_Sections']
    
    # Reorder columns
    summary = summary[['Course', 'In_Person_Sections', 'Online_Sections', 'Total_Sections']]
    
    # Sort by course code
    summary = summary.sort_values('Course').reset_index(drop=True)
    
    return summary

def compare_sections(sf, df):
    olddf = count_sections_by_course_and_format(df).set_index('Course')
    newdf = count_sections_by_course_and_format(sf).set_index('Course')
    return pd.concat([newdf-olddf, newdf], axis=1)

def compare_instructors(sf, df):
    csf = compute_credits(sf)
    return pd.concat([csf, csf - compute_credits(df)], axis=1)

def print_section_summary(df):
    """
    Print a formatted summary of section counts by course, separating in-person and online.
    
    Parameters:
    df (pandas.DataFrame): Course schedule dataframe
    """
    section_counts = count_sections_by_course_and_format(df)
    
    print("Course Section Summary:")
    print("=" * 65)
    print(f"{'Course':<15} {'In-Person':>10} {'Online':>8} {'Total':>8} {'Details'}")
    print("-" * 65)
    
    total_in_person = 0
    total_online = 0
    
    for _, row in section_counts.iterrows():
        in_person = int(row['In_Person_Sections'])
        online = int(row['Online_Sections'])
        total = int(row['Total_Sections'])
        
        # Create detail string
        if online > 0 and in_person > 0:
            detail = f"({in_person} F2F + {online} Online)"
        elif online > 0:
            detail = "(All Online)"
        else:
            detail = "(All In-Person)"
        
        print(f"{row['Course']:<15} {in_person:>10} {online:>8} {total:>8} {detail}")
        
        total_in_person += in_person
        total_online += online
    
    print("=" * 65)
    print(f"{'TOTALS':<15} {total_in_person:>10} {total_online:>8} {total_in_person + total_online:>8}")
    print(f"Unique courses: {len(section_counts)}")
    print(f"In-Person sections: {total_in_person}")
    print(f"Online sections: {total_online}")
    print(f"Total sections: {total_in_person + total_online}")

# Example usage:
# Assuming your dataframe is loaded as 'schedule_df'
# section_counts = count_sections_by_course_and_format(schedule_df)
# print_section_summary(schedule_df)

# If you have the CSV data, you can load it like this:
# df = pd.read_csv('your_schedule_file.csv')
# print_section_summary(df)

# import pandas as pd
# from collections import defaultdict

def time_to_readable(time_val):
    """
    Convert decimal time format (e.g., 930.0) to readable format (e.g., 9:30).
    """
    if pd.isna(time_val) or time_val == '':
        return '-'
    
    time_val = float(time_val)
    hours = int(time_val // 100)
    minutes = int(time_val % 100)
    
    return f"{hours}:{minutes:02d}"

def get_term_info(term_code):
    """
    Extract term information from term code.
    """
    # Assuming format like 202620 (YYYY + term code)
    year = int(str(term_code)[:4])
    term_num = str(term_code)[-2:]
    
    term_map = {
        '10': 'Fall',
        '20': 'Spring', 
        '30': 'Summer'
    }
    
    term_name = term_map.get(term_num, 'Unknown')
    return f"{term_name} {year}"

def csv_to_markdown_schedule(csv_file_path, output_file_path=None):
    """
    Convert CSV schedule file to markdown format.
    
    Parameters:
    csv_file_path (str): Path to the CSV file
    output_file_path (str, optional): Path to save markdown file. If None, automatically saves with same name as CSV but .md extension.
    
    Returns:
    str: Markdown formatted schedule
    """
    
    # Read CSV file
    df = pd.read_csv(csv_file_path)
    
    # Get term information
    term_code = df['Term Code'].iloc[0]
    term_info = get_term_info(term_code)
    
    # Group courses by subject and number
    df['Course_Key'] = df['Subject'] + ' ' + df['Number'].astype(str)
    df['Full_Title'] = df['Course_Key'] + ' - ' + df['Catalog Title']
    
    # Sort by course - first by subject, then by course number (as integer), then by section
    df['Number_Int'] = df['Number'].astype(int)
    
    # Create a numerical sort key for sections to handle mixed numeric and TC sections
    def section_sort_key(section):
        section_str = str(section)
        if 'TC' in section_str:
            # TC sections: TC1=1000, TC2=1001, etc. (come after numeric sections)
            try:
                tc_num = int(section_str.replace('TC', ''))
                return 1000 + tc_num
            except:
                return 1000
        else:
            try:
                # Numeric sections: 001=1, 002=2, etc.
                return int(section_str)
            except:
                # If conversion fails, put at the end
                return 9999
    
    df['Section_Sort'] = df['Section'].apply(section_sort_key)
    df = df.sort_values(['Subject', 'Number_Int', 'Section_Sort'])
    
    # Clean up temporary columns
    df = df.drop(['Number_Int', 'Section_Sort'], axis=1)
    
    # Start building markdown
    markdown_lines = []
    markdown_lines.append(f"# Math Department {term_info} Schedule")
    markdown_lines.append(f"**Term: {term_code} ({term_info})**")
    markdown_lines.append("")
    
    # Group by course
    course_groups = df.groupby('Full_Title')
    
    for course_title, course_df in course_groups:
        markdown_lines.append(f"## {course_title}")
        markdown_lines.append("| Section | Instructor | Days | Time | Building | Room | Credits |")
        markdown_lines.append("|---------|------------|------|------|----------|------|---------|")
        
        for _, row in course_df.iterrows():
            section = row['Section']
            instructor = row['Instructor Name']
            days = row['Meeting Days'] if pd.notna(row['Meeting Days']) and row['Meeting Days'] != '' else 'Online'
            
            # Format time
            if pd.notna(row['Beginning Time']) and row['Beginning Time'] != '':
                start_time = time_to_readable(row['Beginning Time'])
                end_time = time_to_readable(row['Ending Time'])
                time_str = f"{start_time}-{end_time}"
            else:
                time_str = '-'
            
            # Handle building and room for online courses
            if days == 'Online':
                building = '-'
                room = '-'
                time_str = '-'
            else:
                building = row['Building'] if pd.notna(row['Building']) and row['Building'] != '' else '-'
                room = row['Room'] if pd.notna(row['Room']) and row['Room'] != '' else '-'
            
            credits = int(row['Course Credit Hours'])
            
            markdown_lines.append(f"| {section} | {instructor} | {days} | {time_str} | {building} | {room} | {credits} |")
        
        markdown_lines.append("")
    
    # Add summary at the end
    markdown_lines.append("---")
    markdown_lines.append("")
    markdown_lines.append("## Schedule Summary")
    markdown_lines.append("")
    
    # Count sections by type
    online_sections = len(df[df['Section'].str.contains('TC', na=False) | 
                          df['Meeting Days'].isna() | 
                          (df['Meeting Days'] == '')])
    total_sections = len(df)
    in_person_sections = total_sections - online_sections
    unique_courses = df['Course_Key'].nunique()
    
    markdown_lines.append(f"- **Total Sections**: {total_sections}")
    markdown_lines.append(f"- **In-Person Sections**: {in_person_sections}")
    markdown_lines.append(f"- **Online Sections**: {online_sections}")
    markdown_lines.append(f"- **Unique Courses**: {unique_courses}")
    
    # Faculty summary
    markdown_lines.append("")
    markdown_lines.append("### Faculty Teaching Load")
    faculty_counts = df['Instructor Name'].value_counts()
    for instructor, count in faculty_counts.items():
        markdown_lines.append(f"- **{instructor}**: {count} sections")
    
    # Join all lines
    markdown_content = "\n".join(markdown_lines)
    
    # Save to file - if no output path provided, use same name as CSV but with .md extension
    if output_file_path is None:
        # Get the CSV filename without extension and add .md
        import os
        base_name = os.path.splitext(csv_file_path)[0]
        output_file_path = base_name + '.md'
    
    with open(output_file_path, 'w') as f:
        f.write(markdown_content)
    print(f"Markdown schedule saved to: {output_file_path}")
    
    return markdown_content

def convert_and_display(csv_file_path):
    """
    Convert CSV to markdown and display the result.
    
    Parameters:
    csv_file_path (str): Path to the CSV file
    """
    markdown_content = csv_to_markdown_schedule(csv_file_path)
    print(markdown_content)
    return markdown_content

# Example usage:
# Automatically saves as 'spring_2026_schedule.md' if CSV is 'spring_2026_schedule.csv'

#
# Or specify custom output path:
# markdown_schedule = csv_to_markdown_schedule('spring_2026_schedule.csv', 'custom_name.md')
# 
# Or just display without saving:
# convert_and_display('spring_2026_schedule.csv')