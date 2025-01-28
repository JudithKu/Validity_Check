import streamlit as st
import os
import random
import csv
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Define sound folder and list of sounds
sound_folder = os.path.join(os.path.dirname(__file__), "rms_adjust")  # Replace with your folder path
if "sound_files" not in st.session_state:
    st.session_state.sound_files = [f for f in os.listdir(sound_folder) if f.endswith(".wav")]
    random.shuffle(st.session_state.sound_files)

# Initialize session state variables
if "results" not in st.session_state:
    st.session_state.results = []
if "current_sound" not in st.session_state:
    st.session_state.current_sound = None
if "sound_index" not in st.session_state:
    st.session_state.sound_index = 0
if "vp_number" not in st.session_state:
    st.session_state.vp_number = None
if "can_play_sound" not in st.session_state:
    st.session_state.can_play_sound = True
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "age" not in st.session_state:
    st.session_state.age = None
if "gender" not in st.session_state:
    st.session_state.gender = None
if "block_index" not in st.session_state:
    st.session_state.block_index = 0

# Function to save results as downloadable file
def save_results():
    output_file = f"results_vp_{st.session_state.vp_number}.csv"
    results_df = pd.DataFrame(
        st.session_state.results, columns=["Filename", "Valence", "Arousal", "Age", "Gender"]
    )
    csv = results_df.to_csv(index=False)

    # Streamlit download button
    st.download_button(
        label="Download Results",
        data=csv,
        file_name=output_file,
        mime="text/csv",
    )
    st.success("Results are ready to download!")

# Function to send results via email using Mailjet
def send_email_with_results():
    sender_email = st.secrets["email"]["sender"]
    receiver_email = st.secrets["email"]["receiver"]
    username = st.secrets["email"]["username"]
    password = st.secrets["email"]["password"]

    # Create CSV file from results
    output_file = f"results_vp_{st.session_state.vp_number}.csv"
    results_df = pd.DataFrame(
        st.session_state.results, columns=["Filename", "Valence", "Arousal", "Age", "Gender"]
    )
    results_df.to_csv(output_file, index=False)

    # Email message setup
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = f"Results for VP {st.session_state.vp_number}"

    body = "Attached are the results of the experiment."
    message.attach(MIMEText(body, 'plain'))

    # Attach the CSV file
    with open(output_file, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {output_file}',
        )
        message.attach(part)

    # Send the email using Mailjet SMTP
    try:
        server = smtplib.SMTP('in-v3.mailjet.com', 587)  # Mailjet SMTP server and port
        server.starttls()  # Use STARTTLS for secure connection
        server.login(username, password)  # Login with Mailjet credentials
        server.send_message(message)
        server.quit()
        st.success("Results have been sent via email!")  # Success notification
    except smtplib.SMTPException as e:
        st.error(f"Email sending failed: {e}")  # Clear error message for SMTP issues
    except Exception as e:
        st.error(f"An unexpected error occurred while sending email: {e}")  # General error message

# Start the experiment
st.title("Wor(l)d of Emotions")

# Introduction section
st.subheader("Introduction")
st.write(
    """ 
    Thank you for participating! Your task is to listen to the fanatical words and classify them in terms of their “valence” and “arousal”.

    - When you press Play Sound sound bar appears and you can press the play button to listen to it
    - You will be given a small picture where these valence and arousal are visualized.
    - Please move the slider to the appropriate value.
    - Afterwards, please press Submit Response twice

    There are in total 120 words, but you have the option to cancel after every block of 20 words. Please make sure to download the already rated words before exiting.
    """
)

if st.session_state.vp_number is None:
    vp_number = st.text_input("Enter your given VP number (if you didn't get any please contact me)", key="vp_number_input")

    if st.button("Confirm VP Number"):
        if vp_number.strip():
            st.session_state.vp_number = vp_number.strip()
        else:
            st.error("Please enter a valid VP number.")

if st.session_state.vp_number and (st.session_state.age is None or st.session_state.gender is None):
    age = st.text_input("Enter your age:", key="age_input")
    gender = st.selectbox(
        "Select your gender:",
        ["Male", "Female", "Divers", "I do not want to specify"],
        key="gender_input"
    )

    if st.button("Start Experiment"):
        if age and gender:
            st.session_state.age = age
            st.session_state.gender = gender
            st.session_state.results = []
            st.session_state.sound_index = 0
            st.session_state.block_index = 0
        else:
            st.error("Please fill in all fields before starting.")

if st.session_state.vp_number and st.session_state.age and st.session_state.gender:
    # Only display participant details before the first sound is played
    if st.session_state.sound_index == 0 and st.session_state.can_play_sound:
        st.write(f"Participant ID: {st.session_state.vp_number}")
        st.write(f"Age: {st.session_state.age}, Gender: {st.session_state.gender}")

    # Determine block size
    block_size = 20
    start_index = st.session_state.block_index * block_size
    end_index = start_index + block_size

    # Play sounds in blocks
    if start_index < len(st.session_state.sound_files):
        st.write(f"Block {st.session_state.block_index + 1}")

        if st.session_state.sound_index < end_index and st.session_state.sound_index < len(st.session_state.sound_files):
            if st.session_state.can_play_sound:
                if st.button("Play Sound"):
                    st.session_state.current_sound = st.session_state.sound_files[st.session_state.sound_index]
                    file_path = os.path.join(sound_folder, st.session_state.current_sound)
                    with open(file_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/wav")
                    st.session_state.can_play_sound = False

            # Display images and sliders for valence and arousal
            if not st.session_state.can_play_sound:
                valence_image_path = os.path.join(os.path.dirname(__file__), "Valence_Sam.png")
                arousal_image_path = os.path.join(os.path.dirname(__file__), "Arousal_Sam.png")

                st.image(valence_image_path, caption="Valence Scale", width=300)
                valence = st.slider("Valence (-1 negative, +1 positive)", -1.0, 1.0, 0.0, 0.25, key=f"valence_{st.session_state.sound_index}")

                st.image(arousal_image_path, caption="Arousal Scale", width=300)
                arousal = st.slider("Arousal (-1 calm, +1 excited)", -1.0, 1.0, 0.0, 0.25, key=f"arousal_{st.session_state.sound_index}")

                # Submit response and proceed to the next sound
                if st.button("Submit Response"):
                    st.session_state.results.append([st.session_state.current_sound, valence, arousal, st.session_state.age, st.session_state.gender])
                    st.session_state.sound_index += 1
                    st.session_state.current_sound = None
                    st.session_state.can_play_sound = True

        else:
            # End of block
            if st.button("Continue to Next Block"):
                st.session_state.block_index += 1
            if st.button("Finish and Download Results"):
                st.write("Experiment finished! Thank you for participating.")
                save_results()
                if st.button("Send Results via Email"):
                    send_email_with_results()

    else:
        st.write("Experiment finished! Thank you for participating.")
        save_results()
        if st.button("Send Results via Email"):
            send_email_with_results()
