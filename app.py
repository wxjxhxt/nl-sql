#undergrads
import speech_recognition as sr     
import streamlit as st              
# import os                           
import google.generativeai as genai         
# import assemblyai as aai                   
import pymysql                      
from googletrans import Translator   
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter
import base64
import numpy as np
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


#Function To Load Google Gemini Model and provide queries as response
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



## Fucntion To retrieve query from the database
# def read_sql_query(sql, text_to_sql):
#     try:
#         # Connect to the PYSQL database
#         conn = pymysql.connect(host='localhost',
#                              user='root',
#                              password='',
#                              db='text_to_sql')
#         # Create a cursor
#         cur = conn.cursor()
#         st.write(sql)
#         # Execute the SQL query
#         cur.execute(sql)
#         # Fetch all the rows
#         rows = cur.fetchall()
#         conn.commit()
#         conn.close()
#         return rows
#     except pymysql.Error as e:
#         st.write("Error connecting:", e)
#         return None

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',  # Replace with your MySQL password
                       db='text_to_sql',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
def read_sql_query(sql, table_name):
    try:
        # Connect to the MySQL database
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password='',  # Replace with your MySQL password
                               db='text_to_sql')  # Replace with your database name
        # Create a cursor
        cur = conn.cursor()
        
        # Execute the SQL query
        cur.execute(sql)
        
        # Fetch all the rows
        rows = cur.fetchall()
        
        conn.commit()
        conn.close()
        
        return rows, cur  # Return the fetched rows
    except pymysql.Error as e:
        st.write("Error connecting:", e)
        return None

def query_results_to_dataframe(results, cur):
    if results is not None and cur is not None:  # Check if both results and cur are not None
        column_names = [col[0] for col in cur.description]
        df = pd.DataFrame(results, columns=column_names)
        return df
    else:
        return None


def detect_language():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        st.write("Listening...")
        try:
            audio = r.listen(source, timeout=3)
            # Process the audio here
        except sr.WaitTimeoutError:
            print("Listening timed out.")
    
    try:
        detected_language = r.recognize_google(audio)  # Let Google API detect the language
        return detected_language
    except sr.UnknownValueError:
        return "Unable to detect language"
    except sr.RequestError as e:
        return f"Error: {e}"

# Function to translate text to English
def translate_to_english(text):
    translator = Translator()
    translated_text = translator.translate(text, dest='en')
    return translated_text.text

# Main function
# def main():
#     detected_language = detect_language()
#     if detected_language != "Unable to detect language":
#         print("Detected Language:", detected_language)
#         if detected_language != "en":  # If language detected is not English
#             translated_text = translate_to_english(detected_language)
#             print("Translated Text (to English):", translated_text)
#             question=st.text_input("Input1:", key="input", value=translated_text)
#             if question:
#              st.write("querying....")
#              response=get_gemini_response(question, prompt)
#              print(response)
#              response=read_sql_query(response,"storedb")
#              st.subheader("The Response is")
#              for row in response:
#                 stripped = str(row[0]).replace('(', '').replace(')', '').replace(',', '')
#                 print(row)
#                 st.header(stripped)
#         else:
#             st.write("Language is already English")
#     else:
#         st.write("Language detection failed")

def main():
    cur = conn.cursor()  # Assuming 'conn' is your database connection object
    cur.execute(sql_query)
    response = cur.fetchall()
    
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
                response = read_sql_query(response, table_name)
                if response is not None:
                    st.subheader("The Response is")
                    df = query_results_to_dataframe(response, cur)  # Update columns accordingly
                    if df is not None:
                        st.write(df)
                        fig = plot_bar_chart(df)

                        # Display the plot in Streamlit
                        if fig is not None:
                            st.pyplot(fig)
                        else:
                            st.write("No plot to display.")    
                    else:
                        st.write("No data found for the query.")
                else:
                    st.write("Error executing SQL query.")
        else:
            st.write("Language is already English")
    else:
        st.write("Language detection failed")
        st.title('Download Response with Graphs in Different Formats')

    # df = pd.DataFrame(response,fig)
    # if st.button('Download CSV'):
    #     csv_link = download_csv(df, 'mydata')  # Call the download_csv function
    #     # Display a download link
    #     st.markdown(f'Download your file [here]({csv_link})')

def plot_bar_chart(df):
    if df.empty:
        st.write("Insufficient data for plotting.")
        return None

    # Assuming the DataFrame columns are in the correct order for plotting
    x_col = df.columns[0]  # Column for x-axis
    y_col = df.columns[1]  # Column for y-axis

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df[x_col], df[y_col])
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title('Bar Chart')
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for better visibility

    return fig

# def download_csv(dataframe, filename):
#     # Convert DataFrame to CSV string
#     csv_string = dataframe.to_csv(index=False)

#     # Encode CSV string to base64
#     csv_bytes = csv_string.encode('utf-8')
#     b64 = base64.b64encode(csv_bytes).decode('utf-8')

#     # Create download link with base64 content
#     href = f'data:text/csv;base64,{b64}'

#     return href  
if __name__ == "__main__":
    submit = st.button("MIC")
    if submit:
        main()
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
            response, cur = read_sql_query(response, table_name)  # Pass table name as argument
            st.subheader("The Response is")
            df = query_results_to_dataframe(response, cur)  # Update columns accordingly
            if df is not None:
                st.write(df)
                fig = plot_bar_chart(df)
                if fig is not None:
                    st.pyplot(fig)
                else:
                    st.write("No plot to display.")
            else:
                st.write("No data found for the query.")
    # df = pd.DataFrame(response,fig)        
    # if st.button('Download CSV'):
    #     csv_link = download_csv(df, 'mydata')  # Call the download_csv function
    #     # Display a download link
    #     st.markdown(f'Download your file [here]({csv_link})')

# if __name__ == "__main__":
#     print("HELLO")
#     submit=st.button("MIC")
#     if submit:
#         main()
#     else:
#         print("ENGLISH")  
#         question=st.text_input("Input: ",key="input")                   #string for input for API
#         submit=st.button("Ask the question")
# # if submit is clicked
#         if submit:
#             response=get_gemini_response(question,prompt)
#             st.write("querying....")
#             st.write(response)
#             print(response)
#             response=read_sql_query(response,"storedb")
#             st.subheader("The Response is")
#             for row in response:
#                 stripped = str(row[0]).replace('(', '').replace(')', '').replace(',', '')
#                 print(row)
#                 st.header(stripped)