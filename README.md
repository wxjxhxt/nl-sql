# NL-SQL Query Tool

## Introduction
NL-SQL Query Tool is a Python application that allows users to convert English questions into SQL queries. This tool is designed to simplify the process of querying databases by enabling users to express their queries in natural language.

## Installation
To use NL-SQL Query Tool, follow these steps:
1. Clone this repository to your local machine.
2. Create a Python virtual environment using `python -m venv env`.
3. Activate the virtual environment:
    - On Windows: `.\env\Scripts\activate`
    - On macOS and Linux: `source env/bin/activate`
4. Install the required packages using `pip install -r requirements.txt`.
5. Obtain your Google Gemini API key. You can get it from [Gemini Developer Console](https://console.developers.google.com/).
6. Configure your database connection by updating the `app.py` file:
    - Replace the database name, host, username, and password in the connection parameters according to your setup.

## Usage
To use NL-SQL Query Tool:
1. Run the application by executing `python app.py` in your terminal.
2. Access the tool via your web browser at the specified URL.
3. Enter your English question in the provided input field.
4. View the generated SQL query and execute it against your database.

## Example Prompts
The tool provides example prompts to demonstrate its functionality. You can customize these prompts by editing the `prompt` list in the `app.py` file. Ensure that the SQL code does not contain ``` at the beginning or end and does not include the word "sql" in the output.
