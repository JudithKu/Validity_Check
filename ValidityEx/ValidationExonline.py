import streamlit as st
import os
import random
import csv
import pandas as pd

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

# Start the experiment
st.title("Wor(l)d of Emotions")

# Introduction section
st.subheader("Introduction")
st.write("Thank you for participating! Your task is to listen to the fanatical words and classify them in terms of their “valence” and “arousal”. You will be given a small picture where these characteristics are visualized. Please move the slider to the appropriate value. Afterwards, please press Submit twice and then you can listen to the next word. There are in total 120 words, but you have the option to cancel after every block of 20 words. But please make sure to downloas the already rated words.")
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
                    st.session_state.submitted = False

            # Display image and sliders for valence and arousal
            if not st.session_state.can_play_sound and not st.session_state.submitted:
                image_path = os.path.join(os.path.dirname(__file__), "Valence_Arousal_Sam.png")
                st.image(image_path, caption="Please use this picture to give your opinion", width=350)
                valence = st.slider("Valence (-1 negative, +1 positive)", -1.0, 1.0, 0.0, 0.25, key=f"valence_{st.session_state.sound_index}")
                arousal = st.slider("Arousal (-1 calm, +1 excited)", -1.0, 1.0, 0.0, 0.25, key=f"arousal_{st.session_state.sound_index}")

                # Combined submit button
                if st.button("Submit Response"):
                    st.session_state.results.append([st.session_state.current_sound, valence, arousal, st.session_state.age, st.session_state.gender])
                    st.session_state.sound_index += 1
                    st.session_state.current_sound = None
                    st.session_state.can_play_sound = True
                    st.session_state.submitted = True

        else:
            # End of block
            if st.button("Continue to Next Block"):
                st.session_state.block_index += 1
            if st.button("Finish and Download Results"):
                st.write("Experiment finished! Thank you for participating.")
                save_results()

    else:
        st.write("Experiment finished! Thank you for participating.")
        save_results()
