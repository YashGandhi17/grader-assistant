from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import helper as h
import model 
from answerKey import answer_key
import http.client
import json


router = APIRouter()

# Store the memory (accumulated text from PDFs)
memory = ""

# Endpoint to handle PDF upload for memory or evaluation
@router.post("/upload_pdf")
async def upload_pdf():
    global memory

    try:
        pdf_text = h.extract_text_from_pdf("OOPS.pdf")

        memory += "\n" + pdf_text
        return JSONResponse(content={"message": "Memory updated successfully. memory:" + memory})
    
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": f"Error processing PDF: {str(e)}"}
        )

@router.post("/evaluate_answer")
async def EvaluateAnswer(request: Request):
        body = await request.json()
        question = body.get("question")
        student_answer = body.get("student_answer")
        
        if question not in answer_key:
             return JSONResponse(status_code=500, content="Exception: Question does not exist")

        memory_prompt = "Be my assistant evaluator. I am a teacher and need to evaluate student answers. I will give you a pdf, remember that. All the further questions asked will be based on the content of that PDF. Furthermore I will give you the question, tentative answer for the question and the answer given by the student to that question. You need to compare the content of both the answers and then provide me with similarity result of how much similar the student answer is to the answer which I gave. Based on this result, I will evaluate how much marks I need to give to a student.\n" + f"Here is the pdf content:\n{memory}\n" 

        user_prompt = f"This is the input question and correct answer from the professor:\n{question}\n{answer_key[question]}\n" + """Strictly provide me with answer of similarity result in the following format:
        Correctness score (in a range of 0-1).
         Suggestion: 2 lines suggestion to student to perform better.""" + f"Student answer: {student_answer}"

        response = model.getModelResponse(memory_prompt, user_prompt)
        # percentage = h.extract_percentage(response)

        return JSONResponse(content={"Suggestion": response.suggestion, "Correctness Score": response.correctness_score})

@router.post("/check_plagrism")
async def checkPlagrism(request: Request):
    body = await request.json()
    student_answer = body.get("answer")

    conn = http.client.HTTPSConnection("api.gptzero.me")
    payload = json.dumps({
    "document": student_answer,
    "multilingual": False
    })
    headers = {
    'Content-Type': 'application/json'
    }
    conn.request("POST", "/v2/predict/text", payload, headers)
    res = conn.getresponse()
    
    data = res.read()
    data_str = data.decode("utf-8")
    data_dict = json.loads(data_str)

    return data_dict['documents'][0]['result_message']
