import streamlit as st, pandas as pd, plotly.express as px
import io, os, sys
from google import genai
from google.genai import types


def setup_page():
    st.set_page_config(
        page_title="Chatbot",
        layout="centered"
    )
    st.header(":blue[Visualize your data with help from a LLM 📊]")
    
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


def main():
    uploaded_file = st.sidebar.file_uploader("upload your csv file", accept_multiple_files=False, type=['csv'])
    if not uploaded_file: st.stop()
    st.session_state.df = pd.read_csv(uploaded_file)

    metadata = {
        "schema": {
            "row_count": len(st.session_state.df),
            "column_count": len(st.session_state.df.columns),
            "columns": []
        }
    }
    
    for col in st.session_state.df.columns:
        col_info = {
            "name": col,
            "dtype": str(st.session_state.df[col].dtype),
            "non_null_count": int(st.session_state.df[col].count()),
            "null_count": int(st.session_state.df[col].isnull().sum()),
            "unique_values": int(st.session_state.df[col].nunique()),
        }
        metadata["schema"]["columns"].append(col_info)
    
    #with open(metadata_path, 'r') as f:
        #metadata = json.load(f)

    prompt = st.text_input("enter your prompt below...")
    if not prompt: st.stop()
    instructions = f"""
                    you will always provide a python code based on the metadata schema of the 
                    dataset that is provided to you, write the code so it can run 
                    with streamlit, using plotly. always default to use_container_width 
                    to be False. there is a dataframe that is already stored in session state 
                    and you need to access it by calling `st.session_state.df`.
                    you must use this dataframe that's stored in the session state, use 
                    the metadata schema to understand the make up of the data. 
                    if there is no df in sesstion state then return a message saying so.
                    so, do not use dummy data or made up data. always be pythonic and concise.   
                    you will only return python code in your response as plain 
                    text file and no tick marks.  here is the metadata schema: {metadata} .  
                    You must adhere to the schema that's provided to you, use the schema as is. 
                    before you provide the code, make sure that you are using the column names 
                    as they appear in the metadata schema, use the metadata schema to 
                    understand the make up of the data.
                   """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            system_instruction = f'{instructions}',
            thinking_config=types.ThinkingConfig(
              thinking_budget=1000
            ),)
        )
    #user_code = st.code(response.text, language="python")
    #st.session_state['user_code'] = user_code
    #if st.button("Run Code") and 'user_code' in st.session_state:
    if response:
        try:
            exec(response.text)
        except Exception as e:
            st.error(f"Error executing code: {e}")


if __name__ == '__main__':
    setup_page()
    GEMINI_API_KEY = os.environ.get('api-key') #Make sure to point to the right api key
    client = genai.Client(api_key=GEMINI_API_KEY)
    MODEL_ID = "gemini-2.5-flash"
    if "df" not in st.session_state:
        st.session_state.df = None
    main()
