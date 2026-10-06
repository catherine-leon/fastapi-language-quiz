from pathlib import Path
import random
import time
from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "questions.csv"


api = FastAPI(
    title="French Language Quiz API",
    description=(
        "API for managing French-language quiz questions and generating quizzes "
        "by proficiency level and category."
    ),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "system",
            "description": "API status and available quiz configuration.",
        },
        {
            "name": "quiz",
            "description": "Quiz generation and question management.",
        },
        {
            "name": "users",
            "description": "Example endpoint for user progress.",
        },
    ],
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)


@api.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to the response headers."""
    start_time = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start_time:.6f}"
    return response


def load_data() -> list[dict]:
    """Load quiz questions from CSV and convert missing values to None."""
    if not QUESTIONS_FILE.exists():
        return []

    try:
        dataframe = pd.read_csv(QUESTIONS_FILE, sep=None, engine="python")
        dataframe = dataframe.replace({np.nan: None})
        return dataframe.to_dict(orient="records")
    except Exception as exc:
        raise RuntimeError(f"Unable to load quiz data: {exc}") from exc


data = load_data()


class QuizRequest(BaseModel):
    """Parameters used to generate a quiz."""

    level: str
    categories: List[str]
    number_of_questions: int


class QuizResponse(BaseModel):
    """Generated quiz payload."""

    quiz: List[dict]


class QuestionRequest(BaseModel):
    """A question to append to the quiz dataset."""

    question: str
    categorie: str
    niveau: str
    reponse: str
    reponseA: str
    reponseB: str
    reponseC: Optional[str] = None
    reponseD: Optional[str] = None
    commentaire: Optional[str] = None


class UserProgress(BaseModel):
    """User progress information."""

    username: str
    completed_exercises: int
    correct_answers: int
    total_answers: int


@api.get("/", name="Home", tags=["system"])
def get_index():
    """Return a welcome message."""
    return {"message": "Bienvenue sur l’API du questionnaire de français !"}


@api.get("/verify", tags=["system"])
def verify():
    """Check that the API is running."""
    return {"status": "ok"}


@api.get("/info", tags=["system"], name="Get quiz configuration")
def get_info():
    """Return the proficiency levels and categories available in the dataset."""
    if not data:
        return {"levels": [], "categories": []}

    levels = sorted({q["niveau"] for q in data if q.get("niveau")})
    categories = sorted({q["categorie"] for q in data if q.get("categorie")})
    return {"levels": levels, "categories": categories}


@api.post(
    "/generate_quiz",
    response_model=QuizResponse,
    name="Generate a quiz",
    tags=["quiz"],
)
def generate_quiz(request: QuizRequest):
    """Generate a random quiz for a requested level and set of categories."""
    if request.number_of_questions < 1:
        raise HTTPException(
            status_code=400,
            detail="number_of_questions must be greater than zero.",
        )

    if not data:
        raise HTTPException(
            status_code=500,
            detail="No quiz data could be loaded.",
        )

    filtered_data = [
        question
        for question in data
        if question["niveau"] == request.level
        and question["categorie"] in request.categories
    ]

    if not filtered_data:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No questions found for level '{request.level}' "
                "and the requested categories."
            ),
        )

    sample_size = min(len(filtered_data), request.number_of_questions)
    return {"quiz": random.sample(filtered_data, sample_size)}


@api.post("/create_question", name="Create a question", tags=["quiz"])
def create_question(request: QuestionRequest):
    """Append a validated question to the CSV dataset."""
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question text cannot be empty.",
        )

    valid_answers = {"A", "B", "C", "D"}
    correct_answer = request.reponse.strip().upper()
    if correct_answer not in valid_answers:
        raise HTTPException(
            status_code=400,
            detail="reponse must be one of A, B, C or D.",
        )

    options = {
        "A": request.reponseA,
        "B": request.reponseB,
        "C": request.reponseC,
        "D": request.reponseD,
    }
    if not options.get(correct_answer):
        raise HTTPException(
            status_code=400,
            detail="The correct answer must have a corresponding option.",
        )

    new_question = {
        "question": request.question,
        "categorie": request.categorie,
        "niveau": request.niveau,
        "reponse": correct_answer,
        "reponseA": request.reponseA,
        "reponseB": request.reponseB,
        "reponseC": request.reponseC,
        "reponseD": request.reponseD,
        "commentaire": request.commentaire,
    }

    data.append(new_question)

    try:
        pd.DataFrame(data).to_csv(QUESTIONS_FILE, index=False)
    except Exception as exc:
        data.pop()
        raise HTTPException(
            status_code=500,
            detail=f"Unable to save the question: {exc}",
        ) from exc

    return {"status": "created", "question": new_question}


@api.put("/progress", name="Update user progress", tags=["users"])
def update_progress(progress: UserProgress):
    """Validate and return user progress information."""
    if (
        progress.completed_exercises < 0
        or progress.correct_answers < 0
        or progress.total_answers < 0
    ):
        raise HTTPException(
            status_code=400,
            detail="Progress counters cannot be negative.",
        )

    if progress.correct_answers > progress.total_answers:
        raise HTTPException(
            status_code=400,
            detail="correct_answers cannot exceed total_answers.",
        )

    return progress


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
