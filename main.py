import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import openai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found. Please add it to your environment variables.")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str


class UserAnswer(BaseModel):
    answer: str
    topic: str
    correct: bool
    difficulty: str


class GenerateTestRequest(BaseModel):
    answers: List[UserAnswer]


class HintRequest(BaseModel):
    question: str


class FeedbackResponse(BaseModel):
    feedback: str
    correct_answers_count: int


@app.post("/generate_test/")
async def generate_test(request: GenerateTestRequest):
    topics_to_review = set()
    for answer in request.answers:
        if not answer.correct and answer.topic:
            topics_to_review.add(answer.topic)

    new_questions = []
    for topic in topics_to_review:
        prompt = f"Generate a test with 20 question for 5-6 graders на русском on the topic: {topic}. Provide the correct answer and three incorrect answers."
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7,
            )
            question_text = response.choices[0].message['content'].strip()

            question_parts = question_text.split("\n")
            if len(question_parts) >= 4:
                question = question_parts[0].strip()
                correct_answer = question_parts[1].strip()
                incorrect_answers = [question_parts[2].strip(), question_parts[3].strip(), question_parts[4].strip()]

                new_question = {
                    "question": question,
                    "correct_answer": correct_answer,
                    "incorrect_answers": incorrect_answers,
                    "difficulty": "A",
                    "topic": topic
                }
                new_questions.append(new_question)
            else:
                raise ValueError("Failed to parse generated question text")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating question for topic {topic}: {str(e)}")

    return {"new_questions": new_questions}


@app.post("/get_hint/")
async def get_hint(request: HintRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a teacher of math for 5-6 graders на русском."},
                {"role": "user",
                 "content": f"Give me a hint on how to solve this math problem: {request.question} на русском"}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        hint = response.choices[0].message['content'].strip()
        return {"hint": hint}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating hint: {str(e)}")


@app.post("/generate_feedback/", response_model=FeedbackResponse)
async def generate_feedback(user_answers: List[UserAnswer]):
    try:
        topics_to_review = {answer.topic for answer in user_answers if not answer.correct}
        correct_answers_count = sum(1 for answer in user_answers if answer.correct)

        feedback_parts = [f'You need to review the topics: {topics_to_review}']
        feedback_text = " ".join(feedback_parts)

        return {
            "feedback": feedback_text,
            "correct_answers_count": correct_answers_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for 6th and 7th graders preparing for exams. Context: Please provide answers on russian."},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        return {"question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
