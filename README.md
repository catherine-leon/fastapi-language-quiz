# French Language Quiz API

A **FastAPI-based quiz application for French language learning**. The project provides a REST API for loading, filtering, generating and extending a structured bank of language-learning questions, together with a lightweight browser interface for interactive quiz practice.

The question bank is stored as CSV data and can be filtered dynamically by **proficiency level** and **linguistic category**.

## Features

- generate random quizzes by level and category;
- retrieve the levels and categories available in the dataset;
- add new questions through the API;
- validate quiz and user-progress requests with Pydantic models;
- persist newly created questions to CSV;
- expose automatically generated OpenAPI / Swagger documentation;
- measure API request processing time through FastAPI middleware;
- use the API through either HTTP requests or an interactive HTML frontend.

## API

The application is implemented in [`main.py`](main.py) with **FastAPI**.

### `GET /`

Returns a basic welcome response.

### `GET /verify`

Health-check endpoint:

```json
{
  "status": "ok"
}
```

### `GET /info`

Extracts the unique proficiency levels and categories currently represented in the question bank.

Example response:

```json
{
  "levels": ["A1", "A2", "B1"],
  "categories": ["Grammaire", "Lexique", "Syntaxe"]
}
```

The values are derived from the CSV rather than hard-coded, allowing the frontend to build its filters dynamically.

### `POST /generate_quiz`

Generates a random quiz from questions matching a requested level and one or more categories.

Example request:

```json
{
  "level": "A2",
  "categories": ["Grammaire"],
  "number_of_questions": 5
}
```

The endpoint filters the question bank and samples from the matching questions. If fewer questions are available than requested, all matching questions are returned.

### `POST /create_question`

Validates a new question and appends it to the CSV question bank.

The data model supports:

- question text;
- category;
- proficiency level;
- correct answer;
- two required and two optional answer choices;
- an optional explanation.

The endpoint also verifies that the declared correct answer corresponds to an available option.

### `PUT /progress`

Demonstrates validated user-progress data with checks for invalid counter values.

## Data handling

The quiz bank is loaded from [`questions.csv`](questions.csv) with **pandas**.

```text
questions.csv
      │
      ▼
    pandas
      │
      ▼
list of question records
      │
      ├── level/category discovery
      ├── quiz filtering
      ├── random sampling
      └── question creation
```

Missing CSV values are converted to `None` so that optional fields can be represented correctly in JSON responses.

New questions created through the API are added to the in-memory collection and persisted back to the CSV file.

## Request validation

API payloads are defined with **Pydantic** models:

- `QuizRequest`
- `QuizResponse`
- `QuestionRequest`
- `UserProgress`

FastAPI therefore provides request parsing, validation and interactive API schemas automatically.

Additional application-level validation handles cases such as:

- empty question text;
- invalid answer labels;
- a correct answer without a corresponding option;
- negative progress counters;
- more correct answers than total answers;
- quiz filters with no matching questions.

## Middleware

A custom FastAPI middleware measures the processing time of each request and exposes it in the:

```text
X-Process-Time
```

response header.

## Interactive frontend

[`index.html`](index.html) provides a lightweight interface on top of the API.

It:

1. requests available levels and categories from `/info`;
2. lets the user choose quiz parameters;
3. sends a request to `/generate_quiz`;
4. renders the returned questions;
5. checks selected answers in the browser;
6. displays the explanation associated with each question.

This keeps the frontend independent from the contents of the question bank: available filters are obtained directly from the API.

## Project structure

```text
.
├── main.py           # FastAPI application
├── questions.csv     # Structured question bank
├── index.html        # Interactive quiz interface
├── requests.sh       # Example API requests
├── requirements.txt  # Python dependencies
├── .gitignore
└── README.md
```

## Technologies

**Backend**
- Python
- FastAPI
- Pydantic
- pandas
- NumPy
- Uvicorn

**Frontend**
- HTML
- CSS
- JavaScript
- Fetch API

**Data**
- CSV

## Installation

Clone the repository and create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the API

Start the application with:

```bash
uvicorn main:api --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive FastAPI documentation:

```text
http://localhost:8000/docs
```

## Running the frontend

Start the API first, then open `index.html` in a browser.

The frontend communicates with:

```text
http://localhost:8000
```

and retrieves the available quiz configuration automatically.

## Example requests

Example `curl` commands are provided in [`requests.sh`](requests.sh).

They cover:

- API status;
- quiz configuration;
- quiz generation;
- question creation;
- user-progress validation.

## Dataset

The repository includes the structured question bank used by the application. Each record contains the question, linguistic category, proficiency level, answer options, correct answer and an optional explanation.

No private keys or credentials are included in the repository.
