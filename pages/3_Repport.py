#from Home import st
import streamlit as st
from Home import face_rec
import pandas as pd
st.set_page_config(page_title='Reporting', layout='wide')
st.subheader('Reporting')

#retrive logs in report.py
#extract data from redi list

name = 'attendance:logs'
def load_logs(name, end=-1):
    logs_list = face_rec.r.lrange(name, start = 0 ,end=end) #extract  all data from the redis database
    return logs_list



#create tabs to show info
tab1, tab2, tab3 =  st.tabs(['Registered Data', 'Logs', 'Attendance Report'])
with tab1:
    if st.button('Refresh Data'):
        #Retrive the  data from Redis Database
        with st.spinner('Retriving Data from Redis DB...'):
            redis_face_db = face_rec.retrive_data(name='academy:register')    #.retrive_data(name ='academy:register')
            #st.dataframe(redis_face_db) display name, role and embedings
            st.dataframe(redis_face_db[['Name', 'Role']])
with tab2:
    if st.button('Refresh Logs'):
        st.write(load_logs(name=name))

with tab3:
    st.subheader('Attendance Report')
    #load logs into attribute logs_list
    log_list = load_logs(name=name)
    st.write(log_list)
    # step-1 convert the logs that in list of bytes into list of string
    convert_byte_to_string =lambda x: x.decode('utf-8')
    logs_list_string = list(map(convert_byte_to_string, log_list))

    #st.write(logs_list_string)

     #step-2: split string by @ and create nested list
    split_string = lambda x: x.split('@')
    logs_nested_list = list(map(split_string, logs_list_string))
    #convert nester list info into dataframe

    logs_df = pd.DataFrame(logs_nested_list, columns = ['Name','Role','Timestamp'])

    #st.write(logs_df)

    #step-3: Time based Analysis or Report

    logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
    logs_df['Date'] = logs_df['Timestamp'].dt.date

    st.dataframe(logs_df)

    #step-3.1: cal. intime and outtime

    # in time: At which person is first detected in the day (min Timestamp on the date)
    # out time: At which person is last detected in the day (max Timestamp on the date)

    repport_df = logs_df.groupby(by=['Date','Name', 'Role']).agg(
        In_time = pd.NamedAgg('Timestamp', 'min'), #in time
        Out_time= pd.NamedAgg('Timestamp','max') 
    ).reset_index()
    repport_df['In_time'] = pd.to_datetime(repport_df['In_time'])
    repport_df['Out_time'] = pd.to_datetime(repport_df['Out_time'])
    repport_df['Duration'] = repport_df['Out_time']-repport_df['In_time']

    #step-4: Marking person is present or absent

    all_dates = repport_df['Date'].unique()
    name_role = repport_df[['Name','Role']].drop_duplicates().values.tolist()

    date_name_rol_zip = []
    for dt in all_dates:
        for name, role in name_role:
            date_name_rol_zip.append([dt, name, role])
    date_name_rol_zip_df = pd.DataFrame(date_name_rol_zip, columns=['Date','Name','Role'])

    #left join with report_df

    date_name_rol_zip_df = pd.merge(date_name_rol_zip_df, repport_df, how='left', on=['Date','Name','Role'])

   # st.dataframe(date_name_rol_zip_df)

    #Duration
    #Hours

    date_name_rol_zip_df['Duration_seconds'] = date_name_rol_zip_df['Duration'].dt.seconds
    date_name_rol_zip_df['Duration_hour'] = date_name_rol_zip_df['Duration_seconds']/(60*60)

    #st.dataframe(date_name_rol_zip_df)

    def status_marker(x):
        if pd.Series(x).isnull().all():
            return 'Absent'
        elif x>=0 and x<1:
            return 'Absent(less than 1s)'
        elif x>= 1 and x<4:
            return ' Half Day (less than 4 ours)'
        elif x>= 4 and x < 6:
            return 'Half Day'
        elif x>= 6:
            return 'Present'
    
    date_name_rol_zip_df['status'] = date_name_rol_zip_df['Duration_hour'].apply(status_marker)

    st.dataframe(date_name_rol_zip_df)
    