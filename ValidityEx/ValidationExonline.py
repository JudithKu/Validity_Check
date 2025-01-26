import streamlit as st
import os
import random
import csv
import pygame
import pandas as pd

# Initialize pygame mixer for sound playback
pygame.mixer.init()

# Define sound folder and list of sounds
sound_folder = "./rms_adjust"  # Replace with your folder path
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
if "participant_id" not in st.session_state:
    st.session_state.participant_id = 1
if "age" not in st.session_state:
    st.session_state.age = None
if "gender" not in st.session_state:
    st.session_state.gender = None

# Function to play sound
def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Function to save results as downloadable file
def save_results():
    output_file = f"results_vp_{st.session_state.participant_id:02d}.csv"
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

# Start the experiment
st.title("Valence-Arousal Experiment")

if st.session_state.vp_number is None:
    st.session_state.vp_number = f"VP_{st.session_state.participant_id:02d}"

if st.session_state.age is None or st.session_state.gender is None:
    age = st.text_input("Enter your age:", key="age_input")
    gender = st.text_input("Enter your gender:", key="gender_input")

    if st.button("Start Experiment"):
        if age and gender:
            st.session_state.age = age
            st.session_state.gender = gender
            st.session_state.results = []
            st.session_state.sound_index = 0
        else:
            st.error("Please fill in all fields before starting.")

if st.session_state.age and st.session_state.gender:
    st.write(f"Participant ID: {st.session_state.vp_number}")
    st.write(f"Age: {st.session_state.age}, Gender: {st.session_state.gender}")

    # Play sound button
    if st.session_state.sound_index < len(st.session_state.sound_files):
        if st.session_state.can_play_sound:
            if st.button("Play Sound"):
                st.session_state.current_sound = st.session_state.sound_files[st.session_state.sound_index]
                file_path = os.path.join(sound_folder, st.session_state.current_sound)
                play_sound(file_path)
                st.session_state.can_play_sound = False
                st.session_state.submitted = False

        # Display image and sliders for valence and arousal
        if not st.session_state.can_play_sound and not st.session_state.submitted:
            st.image("Valence_Arousal_Sam.png", caption="Instructions for the Experiment", width=300)
            st.write("Rate the following:")
            valence = st.slider("Valence (-1 = very negative, 1 = very positive)", -1.0, 1.0, 0.0, 0.25, key=f"valence_{st.session_state.sound_index}")
            arousal = st.slider("Arousal (-1 = very calm, 1 = very excited)", -1.0, 1.0, 0.0, 0.25, key=f"arousal_{st.session_state.sound_index}")

            # Submit response
            if st.button("Submit Response"):
                st.session_state.results.append([st.session_state.current_sound, valence, arousal, st.session_state.age, st.session_state.gender])
                st.session_state.sound_index += 1
                st.session_state.current_sound = None
                st.session_state.can_play_sound = True
                st.session_state.submitted = True

    else:
        st.write("Experiment finished! Thank you for participating.")
        save_results()
        st.session_state.participant_id += 1
