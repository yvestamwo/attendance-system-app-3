import streamlit as st


#" Header 1"

#st.set_page_config(page_title='Attendance system', layout= 'wide')

st.set_page_config(page_title='Attendance system')
st.header('Attendance System using Face Recognition')

with st.spinner(" Loading Model and Connecting to Redis db"):
    import face_rec

st.success('Model loaded Suscesfully')
st.success('Redis db sucessfully connected') 