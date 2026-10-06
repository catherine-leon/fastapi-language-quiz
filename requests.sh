#!/usr/bin/env bash

BASE_URL="http://localhost:8000"

curl -X GET "$BASE_URL/"

curl -X GET "$BASE_URL/verify"

curl -X GET "$BASE_URL/info"

curl -X POST "$BASE_URL/generate_quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "Débutant",
    "categories": ["Culture"],
    "number_of_questions": 1
  }'

curl -X POST "$BASE_URL/create_question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qui est Nikola Tesla ?",
    "categorie": "Science",
    "niveau": "Avancé",
    "reponse": "D",
    "reponseA": "Un chanteur",
    "reponseB": "Un acteur",
    "reponseC": "Un journaliste",
    "reponseD": "Un ingénieur",
    "commentaire": "Nikola Tesla était un inventeur et ingénieur."
  }'

curl -X PUT "$BASE_URL/progress" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "completed_exercises": 5,
    "correct_answers": 8,
    "total_answers": 10
  }'
