import streamlit as st
import requests

data = {}

st.title("The fastest evaluation of your housing!")
st.write("You'll get a legally certified paper with the price by ChiValue. Simply provide your personal data and house id and wait for a couple of seconds for the evaluation!")

with st.form("Fill in the form"):
    firs_name = st.text_input("Your first name", max_chars=30)
    second_name = st.text_input("Your_second name", max_chars=60)
    house_id = st.text_input("Your house id", max_chars=6)
    passport_number = st.text_input("Fill in your passport number", max_chars=9)
    submit = st.form_submit_button("Apply!")

if submit:
    data = {
        "firs_name": firs_name,
        "second_name": second_name,
        "house_id": house_id,
        "passport_number": passport_number,
    }
response = requests.post("http://127.0.0.1:8000/score", json=data)
st.success("Congratulatins.")
st.write(response.json())
