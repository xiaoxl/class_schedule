from collections import defaultdict

def check_instructor_conflicts_matrix(df):
    """
    Check instructor conflicts using time-day matrix approach.
    Much more efficient than pairwise comparison.
    """
    # Filter out online courses and empty data
    data = df[df['Meeting Days'].notna() & df['Beginning Time'].notna()]
    
    conflicts = []
    
    # Group by instructor
    for instructor, group in data.groupby('Instructor Name'):
        matrix = defaultdict(lambda: {'M': 0, 'T': 0, 'W': 0, 'R': 0, 'F': 0})
        course_details = defaultdict(lambda: defaultdict(list))  # Store course info
        
        for _, row in group.iterrows():
            start_time = row['Beginning Time']
            meeting_days = row['Meeting Days'].upper()
            course_info = {
                'course': f"{row['Subject']}{row['Number']}-{row['Section']}",
                'room': f"{row['Room']}".strip()
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
    data = df[df['Meeting Days'].notna() & df['Beginning Time'].notna() & df['Room'].notna()]
    
    conflicts = []
    
    # Group by room
    for room, group in data.groupby('Room'):
        # Create time-day matrix
        matrix = defaultdict(lambda: {'M': 0, 'T': 0, 'W': 0, 'R': 0, 'F': 0})
        course_details = defaultdict(lambda: defaultdict(list))
        
        for _, row in group.iterrows():
            start_time = row['Beginning Time']
            meeting_days = row['Meeting Days']
            course_info = {
                'course': f"{row['Subject']}{row['Number']}-{row['Section']}",
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
            (course['course'], course.get('room', ''))
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
        
        for i, (course, room) in enumerate(course_info, 1):
            t += f"    {i}. {course}: "
            if room:
                t += f"       Room: {room}\n"
        
        conflict_num += 1
    return t


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
            (course['course'], course['instructor'])
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
        
        for i, (course, instructor) in enumerate(course_info, 1):
            t += f"    {i}. {course} - {instructor}\n"
            # t += f"       \n"
        
        conflict_num += 1
    return t
