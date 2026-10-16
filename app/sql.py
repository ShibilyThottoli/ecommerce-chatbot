
import os
import re
import sqlite3
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from groq import Groq


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

BASE_DIR = Path(__file__).parent

load_dotenv(BASE_DIR / ".env")

GROQ_MODEL = os.getenv("GROQ_MODEL")

# Read the database path from .env.
# If SQLITE_DB_PATH is not defined, use db.sqlite.
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "db.sqlite")

db_path = BASE_DIR / SQLITE_DB_PATH

# Initialize the Groq client
client_sql = Groq()


# --------------------------------------------------
# 2. Prompt for generating SQL queries
# --------------------------------------------------

sql_prompt = """
You are an expert in understanding database schemas and
generating SQL queries for natural language questions.

<schema>
table: product

fields:
product_link - string (hyperlink to product)
title - string (name of the product)
brand - string (name of the brand)
price - integer (price in Indian Rupees)
discount - float (discount represented as a decimal)
avg_rating - float (average rating between 0 and 5)
total_ratings - integer (total number of ratings)
</schema>

Instructions:
- Generate a single SQL query for the user's question.
- Use SELECT * to retrieve all fields.
- For brand searches, use LIKE with wildcards, such as
  brand LIKE '%nike%'.
- Do not use ILIKE.
- Return only the SQL query inside <SQL></SQL> tags.
"""


# --------------------------------------------------
# 3. Prompt for converting database results into answers
# --------------------------------------------------

comprehension_prompt = """
You are an expert at answering questions using the provided data.

You will receive a Question and Data.
Answer using only the information provided in the Data.

Use simple, natural language.
Do not say "Based on the data" or use unnecessary technical terms.

When listing products, use this format:

1. Product title: Rs. 1104 (35% off), Rating: 4.4
   Product link: <product_link>

List each product on a separate line.

Include the product title, price in Indian Rupees,
discount, rating, and product link whenever those fields
are available in the provided data.
"""


# --------------------------------------------------
# 4. Generate an SQL query using Groq
# --------------------------------------------------

def generate_sql_query(question):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sql_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        model=GROQ_MODEL,
        temperature=0.2,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content


# --------------------------------------------------
# 5. Execute the SQL query against SQLite
# --------------------------------------------------

def run_query(query):
    query = query.strip()

    # Allow only SELECT queries
    if not query.upper().startswith("SELECT"):
        return None

    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn)
            return df

    except sqlite3.Error as error:
        print(f"SQLite error: {error}")
        return None
    except Exception as error:
        print(f"Query execution error: {error}")
        return None


# --------------------------------------------------
# 6. Convert query results into a natural-language answer
# --------------------------------------------------

def data_comprehension(question, context):
    # Limit the data sent to the AI
    context = context[:5]

    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": comprehension_prompt,
            },
            {
                "role": "user",
                "content": (
                    f"QUESTION: {question}\n"
                    f"DATA: {context}"
                ),
            },
        ],
        model=GROQ_MODEL,
        temperature=0.2,
        max_tokens=512,
    )

    return chat_completion.choices[0].message.content


# --------------------------------------------------
# 7. Complete SQL chatbot chain
# --------------------------------------------------

def sql_chain(question):
    sql_query = generate_sql_query(question)

    # Extract SQL between <SQL> and </SQL>
    pattern = r"<SQL>(.*?)</SQL>"
    matches = re.findall(pattern, sql_query, re.DOTALL | re.IGNORECASE)

    if not matches:
        return "Sorry, the AI could not generate a valid SQL query."

    query = matches[0].strip()

    print("Generated SQL query:")
    print(query)

    response = run_query(query)

    if response is None:
        return "Sorry, there was a problem executing the SQL query."

    if response.empty:
        return "Sorry, no products were found matching your request."

    context = response.to_dict(orient="records")

    answer = data_comprehension(question, context)

    return answer


# --------------------------------------------------
# 8. Test the SQL chatbot independently
# --------------------------------------------------

if __name__ == "__main__":
    question = "Show the top 3 shoes in descending order of rating"

    answer = sql_chain(question)

    print("\nChatbot response:")
    print(answer)
