from Home import st
#import streamlit as st
from Home import face_rec
from streamlit_webrtc import webrtc_streamer
import av
import time

st.set_page_config(page_title='Prediction')
st.subheader('Real-Time Attendance System')


#Retrive the  data from Redis Database
with st.spinner('Retriving Data from Redis DB...'):
    redis_face_db = face_rec.retrive_data(name='academy:register')    #.retrive_data(name ='academy:register')
    st.dataframe(redis_face_db)
st.success("Data sucessfully Retrive from Redis")

time
waiTime = 30 # time in second
setTime = time.time()
realtimePred = face_rec.RealTimePred() #real time prediction class


#Real Time Prediction
#streamlit webrtc

#callback function 
def video_frame_callback(frame):
    global setTime

    img = frame.to_ndarray(format='bgr24') # bgr is a 3 dimension numpy array
    # operation that you can perform on the array
    pred_img = realtimePred.face_prediction(img, redis_face_db,'facial_features',['Name', 'Role'],thresh= 0.5)
    #pred_img = face_rec.face_prediction(img,redis_face_db, 'Facial_Features',['Name', 'Role'],thresh=0.5)
    timenow = time.time()
    difftime = timenow - setTime
    if difftime >= waiTime:
        realtimePred.saveLogs_redis()
        setTime = time.time() # reset time

        print('save Data to redis database')

    return av.VideoFrame.from_ndarray(pred_img, format='bgr24')

webrtc_streamer(key='realtimepredictiom', video_frame_callback=video_frame_callback,
 rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }                
                )