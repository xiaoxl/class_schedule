import streamlit as st
import io
import openpyxl

from readfiles import read_from_file
from generateoutput import generate_reports, room_excel, instructor_excel



def main():
    st.title("ATU MAPS Class Schedule Processor beta 0.2.3")
    st.markdown('You may need to manually add a column called `Cross-List`')
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        df = read_from_file(uploaded_file)

        reports = generate_reports(df)

        instructor_conflicts = reports['instructor_conflicts']
        ic = reports['instructor_conflicts_text']
        room_conflicts = reports['room_conflicts']
        rc = reports['room_conflicts_text']
        t = reports['schedule_time']
        n = reports['schedule_instructor']
        c = reports['schedule_course']
        r = reports['schedule_room']
        h = reports['instructor_credits']

        if (not instructor_conflicts) and (not room_conflicts):
            wbu = openpyxl.Workbook()
            wbu.remove(wbu.active)
            instructor_excel(wbu, df)
            buffer_u = io.BytesIO()
            wbu.save(buffer_u)
            buffer_u.seek(0)
            
            wbr = openpyxl.Workbook()
            wbr.remove(wbr.active)
            room_excel(wbr, df)
            buffer_r = io.BytesIO()
            wbr.save(buffer_r)
            buffer_r.seek(0)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    "Download Instructor Schedule",
                    data=buffer_u,
                    file_name='schedule_instructor.xlsx',
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            with col2:
                st.download_button(
                    "Download Room Schedule",
                    data=buffer_r,
                    file_name='schedule_room.xlsx',
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        tabs = st.tabs([
            "Conflicts",
            'Credits',
            "Instructors",
            "Rooms",
            "Courses",
            "Time slots",
            "Excel"
        ])

        with tabs[0]:
            st.markdown(f'{ic}{rc}')
        with tabs[1]:
            st.markdown(h)
        with tabs[2]:
            st.markdown(n)
        with tabs[3]:
            st.markdown(r)
        with tabs[4]:
            st.markdown(c)
        with tabs[5]:
            st.markdown(t)
        with tabs[6]:
            st.write("File processed successfully")
            st.write(f"Rows: {len(df)}, Columns: {len(df.columns)}")
            st.dataframe(df)


if __name__ == "__main__":
    main()