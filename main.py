from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
import google.generativeai as genai
from typing import List
import os
from starlette.requests import Request
import uvicorn

# Configure Google Generative AI
GOOGLE_API_KEY = "AIzaSyCyq0jbEgSC9C-TykrFFVUK5_wQVhpjnS8"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")

def extract_text(img_path):
    img = Image.open(img_path)
    response = model.generate_content(["read the image and give the text exactly", img])
    print((response.text))
    for i in response.text :
        if i != "*":
            ans = "".join(response.text)
    return ans

def send_message(prompt):
    var = model.generate_content(prompt)
    return var.text

def evaluate(faculty_answer, student_answer):
    data = send_message("evaluate the answer : " + student_answer + "with respect to" + faculty_answer + "and give the marks and. dont give anything else. ")
    return data

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/result", response_class=HTMLResponse)
async def get_result(request: Request, images: List[UploadFile] = File(...), faculty_answer: str = Form(...), marking_scheme: str = Form(...)):
    image_paths = []
    results = []
    for image in images:
        file_location = f"images/{image.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(image.file.read())
        image_paths.append(file_location)
        student_answer = extract_text(file_location)
        result = evaluate(faculty_answer, student_answer)
        results.append(result)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "faculty_answer": faculty_answer,
        "image_paths": image_paths,
        "results": results,
        "zip": zip,  # Pass the zip function to the template context
        "enumerate": enumerate  # Pass the enumerate function to the template context
    })
    uvicorn.run(app, host="0.0.0.0", port=8000)
