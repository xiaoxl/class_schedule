import streamlit as st
import pandas as pd
import io
# from datetime import datetime
# from check import whole_package
import openpyxl
from check import room_excel, instructor_excel
from check import md_courses, md_instructor, md_rooms, md_time, md_compute_credits
from conflicts import (
    check_instructor_conflicts_matrix,
    check_room_conflicts_matrix,
    md_instructor_matrix_conflicts,
    md_room_matrix_conflicts
)
from readfiles import read_from_file


def main():
    st.title("ATU MAPS Class Schedule Processor beta 0.1.1")
    
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        df = read_from_file(uploaded_file)

        instructor_conflicts = check_instructor_conflicts_matrix(df)
        ic = md_instructor_matrix_conflicts(instructor_conflicts)
        room_conflicts = check_room_conflicts_matrix(df)
        rc = md_room_matrix_conflicts(room_conflicts)
        t = md_time(df)
        n = md_instructor(df)
        c = md_courses(df)
        r = md_rooms(df)
        h = md_compute_credits(df)
        
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


        # with open('out/schedule_instructor.xlsx', 'rb') as f:
        
        #     st.download_button(
        #         "Download Summary Report",
        #         data=f,
        #         file_name='schedule_instructor.xlsx',
        #         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        #     )
        



        # Generate CSV
        # csv_buffer = io.StringIO()
        # df.to_csv(csv_buffer, index=False)
        
        # st.download_button(
        #     "Download CSV",
        #     data=csv_buffer.getvalue(),
        #     file_name="processed_data.csv",
        #     mime="text/csv"
        # )

if __name__ == "__main__":
    main()