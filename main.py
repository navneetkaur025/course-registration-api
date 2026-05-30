from fastapi import FastAPI, UploadFile, File, HTTPException
from bs4 import BeautifulSoup

app = FastAPI()

courses_db = {}

@app.get("/")
def home():
    return {"message": "Course Catalog API Running"}

@app.post("/api/v1/admin/catalog/import")
async def import_catalog(file: UploadFile = File(...)):
    content = await file.read()
    soup = BeautifulSoup(content, "html.parser")

    table = soup.find("table")

    if not table:
        raise HTTPException(status_code=400, detail="No table found")

    rows = table.find_all("tr")[1:]

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 5:
            continue

        course_code = cols[0].get_text(strip=True)
        title = cols[1].get_text(strip=True)

        try:
            credits = int(cols[2].get_text(strip=True))
        except:
            credits = 0

        prerequisites = cols[3].get_text(strip=True)

        cross_listed = bool(cols[4].get_text(strip=True))

        courses_db[course_code] = {
            "course_code": course_code,
            "title": title,
            "credits": credits,
            "prerequisites": prerequisites,
            "cross_listed": cross_listed
        }

    return {"status": "success", "courses_imported": len(courses_db)}

@app.get("/api/v1/catalog/courses/{course_code}")
def get_course(course_code: str):

    if course_code not in courses_db:
        raise HTTPException(status_code=404, detail="Course not found")

    return courses_db[course_code]