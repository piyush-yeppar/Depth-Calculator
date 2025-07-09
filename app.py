import streamlit as st
from PIL import Image
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Page setup
st.set_page_config(page_title="Hole Depth Estimator", layout="centered")
st.title("🕳️ Hole Depth Estimator")
st.markdown("Upload an image of a **hole or excavation site**, estimate its **depth** based on visual analysis.")

# Image uploader
uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)


    with st.spinner("Analyzing image..."):

        prompt = """
            You are a highly skilled construction analysis AI, trained to interpret excavation and trench images with expert-level precision.

            Your task is to examine the uploaded image of a construction site, trench, hole, or pit, and **estimate the vertical depth from the original ground surface level to the bottom of the excavation**.

            Key instructions:
            - Focus only on the **vertical depth from ground surface** to the **bottom of the trench/hole/pit**.
            - **Do NOT include soil piles, debris, or elevated edges** as part of the depth.
            - Use visible **reference objects** such as workers, tools, machinery, safety barriers, or shadows to infer scale.
            - If there is no clear reference, make a **reasonable assumption**, but state it clearly.

            Respond strictly in the following JSON format:
            {
            "estimated_depth_meters": "<estimated depth in foot and in meter as a string >",
            "reasoning": "<brief reasoning using visual evidence such as shadows, body proportions, or object sizes>",
            "assumptions": "<any assumptions made about object size, camera angle, or missing context>"
            }

            ⚠️ Important: Only return the JSON object. Do NOT include markdown, commentary, or explanation outside the JSON format.
            """

        # prompt = """
        # You are an expert in analyzing excavation and construction site photos.
        # From the uploaded image, estimate the **approximate depth** of the visible hole or trench.
        
        # Consider shadows, surrounding objects (like tools, people, or vehicles), and relative scale to reason about depth.

        # Respond in this JSON format:
        # {
        #     "estimated_depth_meters": "estimated depth in meters as a string",
        #     "reasoning": "brief explanation based on visual clues",
        #     "assumptions": "any assumptions you made, like object sizes or camera angle"
        # }

        # Do not include any markdown or extra commentary—only the JSON object.
        # """

        try:
            response = model.generate_content([prompt, image])
            text = response.text.strip()

            # Try parsing JSON
            try:
                cleaned = text.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned)

                st.success("✅ Analysis Complete")
                st.markdown(f"""
                ### 📐 Estimated Depth: **{data.get("estimated_depth_meters")} meters**
                - 🧠 **Reasoning:** {data.get("reasoning")}
                - ⚙️ **Assumptions:** {data.get("assumptions")}
                """)
            except Exception as e:
                st.error("Failed to parse response.")
                st.text_area("Raw Response:", text)

        except Exception as e:
            st.error(f" API Error: {e}")
