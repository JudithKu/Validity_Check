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
        key="download_results"
    )
    st.success("Results are ready to download!")

def send_email_with_results():
    try:
        # SMTP credentials from Streamlit secrets
        sender_email = st.secrets["email"]["sender"]
        receiver_email = st.secrets["email"]["receiver"]
        username = st.secrets["email"]["username"]
        password = st.secrets["email"]["password"]

        # Create CSV file
        output_file = f"results_vp_{st.session_state.vp_number}.csv"
        results_df = pd.DataFrame(
            st.session_state.results, columns=["Filename", "Valence", "Arousal", "Age", "Gender"]
        )
        results_df.to_csv(output_file, index=False)

        # Prepare email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = f"Results for VP {st.session_state.vp_number}"

        body = "Attached are the results of the experiment."
        message.attach(MIMEText(body, 'plain'))

        # Attach CSV file
        with open(output_file, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {output_file}',
            )
            message.attach(part)

        # Connect to SMTP server and send email
        server = smtplib.SMTP('in-v3.mailjet.com', 587)
        server.starttls()
        server.login(username, password)
        server.send_message(message)
        server.quit()

        st.success("Email sent successfully!")
    except Exception as e:
        st.error("Failed to send email. Please try again later.")

# Start the experiment
st.title("Wor(l)d of Emotions")

# Introduction section
st.subheader("Introduction")
st.write(
    """ 
    Thank you for participating! Your task is to listen to fantasy words and classify them in terms of their “valence” and “arousal”.

    - When you press Play Sound sound bar appears and you can press the play button to listen to it
    - You will be given a small picture where valence and arousal are visualized.
    - Please move the slider to the appropriate value.
    - Afterwards, please press Submit Response twice.

    There are in total 120 words, but you have the option to cancel after every block of 20 words. Please make sure to send the results via E-mail. If you get an error please download the results.
    """
)

if st.session_state.vp_number is None:
    vp_number = st.text_input("Enter your given VP number (if you didn't get any please contact me)", key="vp_number_input")

    if st.button("Confirm VP Number", key="confirm_vp_number"):
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

    if st.button("Start Experiment", key="start_experiment"):
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
        
block_size = 20  # Anzahl der Sounds pro Block
if st.session_state.block_index < len(st.session_state.sound_files) // block_size:
    start_index = st.session_state.block_index * block_size
    end_index = start_index + block_size

    # Block-Header anzeigen
    st.write(f"Block {st.session_state.block_index + 1} of {len(st.session_state.sound_files) // block_size}")

    # Aktuellen Sound abspielen und bewerten
    if st.session_state.sound_index < len(st.session_state.sound_files):
        current_sound_key = f"sound_{st.session_state.sound_index}"
        if st.session_state.can_play_sound:
            if st.button("Play Sound", key=f"play_sound_{current_sound_key}"):
                st.session_state.current_sound = st.session_state.sound_files[st.session_state.sound_index]
                file_path = os.path.join(sound_folder, st.session_state.current_sound)
                with open(file_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/wav")
                st.session_state.can_play_sound = False

        if not st.session_state.can_play_sound:
            # Slider für Valence und Arousal anzeigen
            valence_image_path = os.path.join(os.path.dirname(__file__), "Valence_Sam.png")
            arousal_image_path = os.path.join(os.path.dirname(__file__), "Arousal_Sam.png")

            st.image(valence_image_path, caption="Valence Scale", width=300)
            valence = st.slider(
                "Valence (-1 negative, +1 positive)", -1.0, 1.0, 0.0, 0.25, key=f"valence_{current_sound_key}"
            )

            st.image(arousal_image_path, caption="Arousal Scale", width=300)
            arousal = st.slider(
                "Arousal (-1 calm, +1 excited)", -1.0, 1.0, 0.0, 0.25, key=f"arousal_{current_sound_key}"
            )

            # Antwort absenden und zum nächsten Sound wechseln
            if st.button("Submit Response", key=f"submit_response_{current_sound_key}"):
                st.session_state.results.append(
                    [st.session_state.current_sound, valence, arousal, st.session_state.age, st.session_state.gender]
                )
                st.session_state.sound_index += 1
                st.session_state.current_sound = None
                st.session_state.can_play_sound = True

    # Block abgeschlossen: Ergebnisse anzeigen und Buttons anbieten
    if st.session_state.sound_index == end_index or st.session_state.sound_index == len(st.session_state.sound_files):
        st.write("You have completed the current block!")
        save_results()

        # Button für den E-Mail-Versand
        if st.button("Send Results via Email", key=f"send_results_email_block_{st.session_state.block_index}"):
            send_email_with_results()

        # Button für den nächsten Block
        if st.button("Continue to Next Block", key=f"continue_next_block_{st.session_state.block_index}"):
            st.session_state.block_index += 1
            st.session_state.can_play_sound = True  # Reset für den nächsten Block
else:
    st.write("You have completed all blocks! Thank you for your participation.")

    # Ensure the last block's results are saved
    if st.session_state.sound_index == len(st.session_state.sound_files):
        save_results()

    if st.button("Send Final Results via Email", key="send_final_results_email"):
        send_email_with_results()
