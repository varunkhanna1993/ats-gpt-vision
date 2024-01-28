import base64 as base64
import streamlit as st
import io as io
from PIL import Image
import pdf2image
import os
from openai import OpenAI
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_gpt4_vision_response(input_text, image_url, prompt):
    if not input_text or not image_url or not prompt:
        st.error("Input text, image URL, or prompt is missing.")
        return None

    messages = [
        {"role": "user", "content": [{"type": "text", "text": input_text}, {"type": "image_url", "image_url": {"url": image_url}}]},
        {"role": "assistant", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(model="gpt-4-vision-preview", messages=messages, max_tokens=400)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in API call: {e}")
        return None


def input_pdf_setup(uploaded_file):
    if uploaded_file is None:
        raise FileNotFoundError("No file uploaded")

    # Convert the first two pages of the PDF to images
    images = pdf2image.convert_from_bytes(uploaded_file.read(), fmt="jpeg", first_page=1, last_page=2)

    # Initialize a byte array to hold the combined image
    combined_img_byte_arr = io.BytesIO()

    # Combine the images vertically
    first_page, second_page = images[0], images[1]
    combined_image = Image.new('RGB', (first_page.width, first_page.height + second_page.height))
    combined_image.paste(first_page, (0, 0))
    combined_image.paste(second_page, (0, first_page.height))

    # Save the combined image to the byte array
    combined_image.save(combined_img_byte_arr, format='JPEG')
    combined_img_byte_arr = combined_img_byte_arr.getvalue()

    # Convert to base64
    image_url = f"data:image/jpeg;base64,{base64.b64encode(combined_img_byte_arr).decode()}"

    return image_url

def read_prompt_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return None


# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Assist - Apply to Jobs with Confidence")
input_text = st.text_area("Job Description:",  height=300, key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])
# Function to inject custom CSS # Optional or comment out

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit2 = st.button("Percentage match")

# File paths for the prompt files
file_path_prompt1 = "prompts/prompt1.txt"  # Update with actual file path
file_path_prompt2 = "prompts/prompt2.txt"  # Update with actual file path

input_prompt1 = read_prompt_from_file(file_path_prompt1)   # Your input prompt 1 here
input_prompt2 = read_prompt_from_file(file_path_prompt2) # Your input prompt 2 here

if submit1 and uploaded_file is not None:
    try:
        image_url = input_pdf_setup(uploaded_file)
        response = get_gpt4_vision_response(input_text, image_url, input_prompt1)
        if response:
            st.subheader("The Response is")
            st.write(response)
    except FileNotFoundError as e:
        st.error(e)

elif submit2 and uploaded_file is not None:
    try:
        image_url = input_pdf_setup(uploaded_file)
        response = get_gpt4_vision_response(input_text, image_url, input_prompt2)
        if response:
            st.subheader("The Response is")
            st.write(response)
    except FileNotFoundError as e:
        st.error(e)
