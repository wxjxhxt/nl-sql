#undergrads
import speech_recognition as sr     
import streamlit as st              
import os                           
import google.generativeai as genai         
# import assemblyai as aai                   
import pymysql                      
from googletrans import Translator   
import pandas as pd
import matplotlib.pyplot as plt
import distutils
import seaborn as sns
from io import BytesIO
import xlsxwriter
import base64
import numpy as np
from reportlab.lib.pagesizes import letter
import tempfile
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
load_dotenv()                    

#API KEYS
# aai.settings.api_key = "043b959beccb44bf8d2b08f6a836d457"
genai.configure(api_key='AIzaSyBr__M4c4oph-O17DEIIOidORQl9Xizdpw')

st.header("App To Retrieve SQL Data") #app
# Apply the background image
page_bg_img = """
<style>~
[data-testid="stAppViewContainer"] {
 background-image: url(https://img.freepik.com/free-vector/abstract-paper-style-background_52683-134881.jpg?size=626&ext=jpg);
 background-size: cover;
}
[data-testid="stHeader"] {
background-color: rgb(0, 0, 0 ,0);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)



def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-pro')       #genrative ,model gemini pro
    response=model.generate_content([prompt[0],question])       #rquesting response
    return response.text 

## Prompt
prompt=[
    """
    You are an expert in converting English questions to SQL queries!
The SQL database has the tables SALES and Products with the following columns:

For the SALES table:
- SaleID (INTEGER PRIMARY KEY)
- Date (DATE)
- CustomerID (INTEGER)
- EmployeeID (INTEGER)
- TotalAmount (NUMERIC(10, 2))

For the Products table:
- ProductID (INTEGER PRIMARY KEY)
- ProductName (VARCHAR(255))
- Description (TEXT)
- UnitPrice (NUMERIC(10, 2))
- QuantityInStock (INTEGER)

For example:
Example 1 - How many sales transactions were made in the last week?
The SQL command could resemble this:
SELECT COUNT(*) FROM SALES WHERE Date >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK);

Example 2 - Retrieve all products with a unit price greater than $100.
The corresponding SQL query might be:
SELECT * FROM Products WHERE UnitPrice > 100;
also the sql code should not have ``` in beginning or end and sql word in output

Please note that to perform date and time operations in MySQL, you should use MySQL's date and time functions.

    """


]


conn = pymysql.connect(
    host='localhost',
    user='root',
    password='', 
    db='text_to_sql',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def read_sql_query(sql, table_name, conn):
    try:
        
        cur = conn.cursor()

        cur.execute(sql)

        rows = cur.fetchall()
        
        conn.commit()
     
        return rows, cur  
    except pymysql.Error as e:
        st.write("Error connecting:", e)
        return None, None
    
def query_results_to_dataframe(results, cur):
    if results is not None and cur is not None:  # Check if both results and cur are not None
        column_names = [col[0] for col in cur.description]
        df = pd.DataFrame(results, columns=column_names)
        return df
    else:
        return None


def generate_pdf_report(gemini_response, query_results_df, graph_figure):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 16)
    c.drawString(100, 750, "Gemini Response Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 650, "Query Results:")
    if query_results_df is not None:
       
        query_results_str = query_results_df.to_string(index=False)
        lines = query_results_str.split('\n')
        y_position = 630
        for line in lines:
            c.drawString(120, y_position, line)
            y_position -= 20
    
    # Graph
    c.drawString(100, 400, "Graph:")
    if graph_figure is not None:
        # Save the figure to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            graph_figure.savefig(tmp_file.name, format='png')
            tmp_file.close()
            
            c.drawImage(tmp_file.name, 100, 250, width=400, height=300)
           
            os.unlink(tmp_file.name)
    
    c.save()
    buffer.seek(0)
    
    return buffer


def download_pdf_report(gemini_response, query_results_df, graph_figure):
    buffer = generate_pdf_report(gemini_response, query_results_df, graph_figure)
    return buffer
    
def detect_language():
    r = sr.Recognizer()
    audio = None  # Initialize audio with None
    with sr.Microphone() as source:
        print("Listening...")
        st.write("Listening...")
        try:
            audio = r.listen(source, timeout=3)
            # Process the audio here
        except sr.WaitTimeoutError:
            print("Listening timed out.")

    # Check if audio is still None
    if audio is None:
        return "Unable to detect language"

    try:
        detected_language = r.recognize_google(audio)  
        return detected_language
    except sr.UnknownValueError:
        return "Unable to detect language"
    except sr.RequestError as e:
        return f"Error: {e}"

def translate_to_english(text):
    translator = Translator()
    translated_text = translator.translate(text, dest='en')
    return translated_text.text


def main(conn):
    detected_language = detect_language()
    if detected_language != "Unable to detect language":
        print("Detected Language:", detected_language)
        if detected_language != "en":
            translated_text = translate_to_english(detected_language)
            print("Translated Text (to English):", translated_text)
            question = st.text_input("Input1:", key="input", value=translated_text)
            if question:
                st.write("querying...")
                response = get_gemini_response(question, prompt)
                print(response)
                st.write("SQL Query:", response)
                if "SALES" in response.upper():
                    table_name = "SALES"
                elif "PRODUCTS" in response.upper():
                    table_name = "PRODUCTS"
                else:
                    st.write("Invalid query.")
                    return
                response, cur = read_sql_query(response, table_name, conn)
                
                if response is not None:
                    st.subheader("The Response is")
                    df = query_results_to_dataframe(response, cur)  # Update columns accordingly
                    if df is not None:
                        st.write(df)
                        fig = plot_chart(df)

                        # Display the plot in Streamlit
                        if fig is not None:
                            st.pyplot(fig)
                            
                        else:
                            st.write("No plot to display.")
                        download_report(response, df, fig)        
                    else:
                        st.write("No data found for the query.")
                else:
                    st.write("Error executing SQL query.")
        else:
            st.write("Language is already English")
    else:
        st.write("Language detection failed")
        st.title('Download Response with Graphs in Different Formats')

   

def plot_chart(df):
    if df.empty:
        st.write("Insufficient data for plotting.")
        return None

    x_col = df.columns[0]  # Column for x-axis
    y_col = df.columns[1]  # Column for y-axis

    fig, ax = plt.subplots(figsize=(10, 6))

    
    if df[y_col].dtype == 'object':
        
        ax.bar(df[x_col], df[y_col])
        ax.set_title('Bar Chart')
    elif len(df[y_col].unique()) < 10:
       
        ax.bar(df[x_col], df[y_col])
        ax.set_title('Bar Chart')
    elif df[y_col].dtype in ['int64', 'float64']:
        
        ax.plot(df[x_col], df[y_col])
        ax.set_title('Line Chart')
    else:
        st.write("Unable to determine plot type for the provided data.")
        return None

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for better visibility

    return fig

def download_report(gemini_response, query_results_df, graph_figure):
    pdf_buffer = download_pdf_report(gemini_response, query_results_df, graph_figure)
    st.download_button(
        label="Download Report",
        data=pdf_buffer,
        file_name="Query_report.pdf",
        mime="application/pdf"
    )

if __name__ == "__main__":
    submit = st.button("MIC")
    if submit:
        main(conn)
    else:
        question = st.text_input("Input: ", key="input")  # string for input for API
        submit = st.button("Ask the question")
        # if submit is clicked
        if submit:
            
            st.write("querying...")
            response = get_gemini_response(question, prompt)
            print(response)
            st.write("SQL Query:", response)
            if "SALES" in response.upper():
                table_name = "SALES"
            elif "PRODUCTS" in response.upper():
                table_name = "PRODUCTS"
            else:
                st.write("Invalid query.")
                raise ValueError("Invalid query.")  # Raise an error for an invalid query
            response, cur = read_sql_query(response, table_name, conn)  # Pass table name as argument
            st.subheader("The Response is")
            df = query_results_to_dataframe(response, cur)
               # Update columns accordingly
            if df is not None:
                st.write(df)
                fig = plot_chart(df)
                if fig is not None:
                    st.pyplot(fig)
                else:
                    st.write("No plot to display.")
                download_report(response, df, fig)    
            else:
                st.write("No data found for the query.")
    
