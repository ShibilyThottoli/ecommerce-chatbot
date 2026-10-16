# E-Commerce Chatbot

An AI-powered e-commerce assistant built with **Python and Streamlit**. It understands customer questions and routes them to the appropriate workflow: answering frequently asked questions or searching a product database using natural language.

The chatbot can answer store-policy questions—such as cash on delivery and returns—and help users find products by brand, discount, price, and rating.

## Demo

### Product search

![E-Commerce Chatbot — product search example](assets/chatbot-demo-1.png)

### FAQ conversations

![E-Commerce Chatbot — FAQ examples](assets/chatbot-demo-2.png)

## Features

- **Conversational interface:** Chat with the assistant through a Streamlit UI.
- **Semantic question routing:** Classifies incoming questions and directs them to the FAQ or product-query workflow.
- **FAQ retrieval:** Uses FAQ data and ChromaDB to retrieve relevant information for policy questions.
- **Natural-language product search:** Converts product questions into SQL queries with a Groq-hosted language model.
- **SQLite product database:** Searches structured product information, including brand, price, discount, average rating, and product link.
- **Readable responses:** Converts matching product records into a natural-language answer.
- **Configurable settings:** Loads the Groq model and database path from environment variables.

## Example questions

**Product queries**
- “Show Puma shoes with a discount of 30% or more.”
- “Show the top 3 shoes in descending order of rating.”
- “Are there Nike shoes under ₹3,000?”
- “What is the price and rating of this product?”

**FAQ queries**
- “Is cash on delivery available?”
- “How is the return policy?”
- “How long does a refund take?”
- “What payment methods are accepted?”

The responses depend on the contents of the supplied FAQ data and local product database.

## How it works

1. A user submits a question through the Streamlit chat interface.
2. The semantic router decides whether the question belongs to the **FAQ** or **product/SQL** workflow.
3. For an FAQ question, the FAQ chain retrieves relevant information from the FAQ collection in ChromaDB and prepares an answer.
4. For a product question, the Groq model generates a SQL query based on the product schema.
5. The application executes the query against the local SQLite database.
6. The matching records are passed to the answer-generation step, which produces a user-friendly response in the chat.

```text
                         User question
                               |
                               v
                     Streamlit chat UI
                               |
                               v
                        Semantic router
                         /           \
                        v             v
                   FAQ route      Product route
                        |             |
                        v             v
                 FAQ data +       Groq model
                  ChromaDB       generates SQL
                        |             |
                        |             v
                        |        SQLite database
                        |             |
                        v             v
                   FAQ answer   Product records
                        \             /
                         v           v
                       Chat response
```

## Tech stack

| Technology | Role in the project |
|---|---|
| Python | Application logic |
| Streamlit | Interactive chat interface |
| Groq API | Language-model calls for SQL generation and response generation |
| Semantic Router | Routes user questions to the appropriate workflow |
| Hugging Face / Sentence Transformers | Text embeddings used by the semantic-routing or retrieval components |
| ChromaDB | Vector storage and retrieval for FAQs |
| SQLite | Stores structured product data |
| Pandas | Handles SQL query results |
| `python-dotenv` | Loads local configuration from `.env` |

## Project structure

The exact folder contents may vary. The application files described here follow this general structure:

```text
ecommerce-chatbot/
├── app/
│   ├── main.py                 # Streamlit interface and routing to chains
│   ├── router.py               # Semantic routing logic
│   ├── faq.py                  # FAQ ingestion and retrieval chain
│   ├── sql.py                  # Groq SQL generation and SQLite execution
│   ├── .env                    # Local environment variables (do not commit)
│   ├── db.sqlite               # Local product database
│   └── resources/
│       └── faq_data.csv        # FAQ source data
├── assets/
│   ├── chatbot-demo-1.png      # Product-query screenshot
│   └── chatbot-demo-2.png      # FAQ screenshot
├── requirements.txt            # Python dependencies
└── README.md
```

If your actual repository has a different layout, update this tree to match it before publishing.

## Getting started

### Prerequisites

- Python installed
- A Groq API key
- Internet access for Groq API calls and first-time model downloads
- The project files and data used by the application

### 1. Clone the repository

Replace the placeholder with your GitHub repository URL:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ecommerce-chatbot
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create `app/.env` if your code loads `.env` from the `app` directory. Add your own values:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=your_available_groq_model_id
SQLITE_DB_PATH=db.sqlite
```

Use a model ID currently available to your Groq account. The application reads the model name from `GROQ_MODEL`, so you can change it without editing the Python code.

**Security:** Never commit your real API key or other secrets. Add `.env` to `.gitignore`. If a key has already been pushed publicly, revoke it and create a replacement.

### 5. Run the application

From the project root:

```powershell
python -m streamlit run app/main.py
```

If you are already inside the `app` directory, run:

```powershell
python -m streamlit run main.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Product database

The SQL workflow is designed around a `product` table with these fields:

| Column | Description |
|---|---|
| `product_link` | Product page URL |
| `title` | Product name |
| `brand` | Brand name |
| `price` | Price in Indian rupees |
| `discount` | Discount value stored in the database |
| `avg_rating` | Average rating |
| `total_ratings` | Number of ratings |

The database file must be available at the path configured by `SQLITE_DB_PATH`. The default value in the application is `db.sqlite`, resolved relative to the `app` directory.

## Configuration notes

- `GROQ_API_KEY` authenticates requests to the Groq API.
- `GROQ_MODEL` selects the model used by the SQL and answer-generation functions.
- `SQLITE_DB_PATH` specifies the SQLite database filename or path relative to the application directory.
- FAQ ingestion uses the FAQ CSV file and a ChromaDB collection. Ensure the CSV is present at the path expected by `main.py`.

## Troubleshooting

**Groq reports `model_not_found`**  
Check the model IDs currently available to your Groq account and update `GROQ_MODEL` in `app/.env`.

**Groq reports `context_length_exceeded`**  
The request may include too many product records or too much text. Limit the number of records and/or fields passed to the answer-generation function.

**`ModuleNotFoundError`**  
Activate the same Python environment used to install the dependencies, then run:

```bash
python -m pip install -r requirements.txt
```

**The chatbot cannot find the database or FAQ CSV**  
Confirm the files exist in the locations expected by `main.py` and `sql.py`. Check that `SQLITE_DB_PATH` matches the actual database filename.

**The router chooses the wrong workflow**  
Review the example utterances or route definitions in `router.py` and add representative examples of the kinds of questions users ask.

## Current limitations

- Answers are limited by the information available in the local FAQ data and product database.
- Product search depends on the quality of the generated SQL and the database schema.
- Groq API access, model availability, rate limits, and context limits may affect requests.
- The project is a learning/demo application; generated SQL should be validated carefully before using this pattern with sensitive data or in production.

## Future improvements

- Add unit tests for routing, SQL generation, and FAQ retrieval.
- Improve validation and error handling for generated SQL.
- Add product filters, pagination, and more structured product cards.
- Add logging and evaluation for routing accuracy and answer quality.
- Deploy the Streamlit application and document the deployment steps.

## License

Add a license before distributing or reusing this project. If no license is included, GitHub visitors should not assume they have permission to reuse the code.
