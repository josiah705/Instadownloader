from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import instaloader
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/download")
async def download_instagram_video(insta_url: str = Form(...)):
    try:
        if not any(x in insta_url for x in ["/p/", "/reel/", "/tv/"]):
            return JSONResponse(content={"error": "Invalid Instagram URL"}, status_code=400)

        shortcode = insta_url.rstrip("/").split("/")[-1]
        folder = f"downloads/{shortcode}"

        L = instaloader.Instaloader(
            dirname_pattern=folder,
            save_metadata=False,
            download_comments=False,
            post_metadata_txt_pattern=""
        )

        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=shortcode)

        for file in os.listdir(folder):
            if file.endswith(".mp4"):
                file_path = os.path.join(folder, file)
                return FileResponse(path=file_path, media_type="video/mp4", filename=f"{shortcode}.mp4")

        return JSONResponse(content={"error": "Video not found"}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
