import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import base64

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"] 

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-001')

def extract_text_from_txt(txt_file):
    text = txt_file.read().decode("utf-8")
    return text

def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def generate_responses(text1, text2, question):
    generation_config = {
        "max_output_tokens": 3000,
        "temperature": 0.2,
        "top_p": 0.95,
    }
    
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    response = model.generate_content(
        [text1, text2, question],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    # Wait for response to complete iteration
    response.resolve()

    return response.text

def clear_input():
    st.session_state.input_text = ""

def main():
    # Add a logo and set up the layout
    logo_file = r'infoguru.png'
    if logo_file:
        with open(logo_file, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode("utf-8")

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: center;">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="width: 200px; height: auto; margin-right: 20px;">
                <h1>Data Insight Extractor</h1>
            </div>
            <style>
                .css-1cpxqw2 a {{ color: #FF6347 !important; }}
                .stButton button {{
                    color: white !important;
                    background-color: #4CAF50 !important;
                    border: none !important;
                    border-radius: 4px !important;
                    text-align: center !important;
                    font-size: 14px !important;
                    padding: 10px 24px !important;
                }}
                .stButton button:hover {{
                    background-color: #45a049 !important;
                }}
                .clear-button {{
                    background-color: #f44336 !important;
                }}
                .end-button {{
                    background-color: #FF6347 !important;
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    if 'input_text' not in st.session_state:
        st.session_state.input_text = ""

    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

    if uploaded_file is not None:
        #st.write("File uploaded")  # Debug statement
        if uploaded_file.name.endswith(".pdf"):
            text1 = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            text1 = extract_text_from_txt(uploaded_file)

        text2 = "Go through the document and answer the following question: (Please present the exact lines in the respective page no and Line number): present it in a table format:"

        st.write("File uploaded and text extracted. You can now ask questions.")

        question = st.text_input("You: ", value=st.session_state.input_text, key="input_text")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("Search", key="send_button"):
                if question:
                    with st.spinner("Generating response..."):
                        response = generate_responses(text1, text2, question)
                    st.session_state.conversation.append((question, response))
                    #st.session_state.input_text = ""
                    st.rerun()

        with col2:
            st.button("Clear", key="clear_button", on_click=clear_input)

        with col3:
            if st.button("End Conversation", key="end_button"):
                st.session_state.conversation = []
                #st.session_state.input_text = ""
                st.rerun()

        st.markdown('<div class="chat-history">', unsafe_allow_html=True)
        st.write("Chat History:")
        for q, r in st.session_state.conversation:
            st.markdown(f'<p class="user">You: {q}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="bot">Bot: {r}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("Please upload a PDF or TXT file.")

    # Copyright notice
    st.markdown(
        """
        <footer style="text-align: center; margin-top: 50px;">
            <p>&copy; 2024 Madhu. All rights reserved.</p>
        </footer>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
