import io
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from PIL import Image, ImageOps
import numpy as np
import matplotlib.pyplot as plt
import base64

app = FastAPI()

# Mount static directory and template files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Function to convert image to base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Function to create histogram for RGB images
def create_rgb_histogram(image_array):
    plt.figure(figsize=(4, 3))
    
    # Red channel
    plt.hist(image_array[:, :, 0].ravel(), bins=256, color='red', alpha=0.5, label='Red')
    
    # Green channel
    plt.hist(image_array[:, :, 1].ravel(), bins=256, color='green', alpha=0.5, label='Green')
    
    # Blue channel
    plt.hist(image_array[:, :, 2].ravel(), bins=256, color='blue', alpha=0.5, label='Blue')

    plt.xlabel('Pixel value')
    plt.ylabel('Frequency')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Image.open(buf)

# Function to create histogram for grayscale images
def create_grayscale_histogram(image_array):
    plt.figure(figsize=(4, 3))
    plt.hist(image_array.ravel(), bins=256, color='gray', alpha=0.7)
    plt.xlabel('Pixel value')
    plt.ylabel('Frequency')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Image.open(buf)

# Function to equalize RGB image
def equalize_rgb(image):
    # Split the image into R, G, B channels
    r, g, b = image.split()

    # Equalize each channel
    r_eq = ImageOps.equalize(r)
    g_eq = ImageOps.equalize(g)
    b_eq = ImageOps.equalize(b)

    # Merge the channels back together
    return Image.merge('RGB', (r_eq, g_eq, b_eq))

# Function to equalize grayscale image
def equalize_grayscale(image):
    image_gray = ImageOps.grayscale(image)
    img_array = np.array(image_gray)
    img_equalized = ImageOps.equalize(image_gray)
    return img_equalized, img_array

# Home route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route to upload RGB image
@app.post("/upload-rgb/")
async def upload_rgb(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read()))

    # Create histogram for original RGB image
    img_array_original = np.array(image)
    histogram_original_image = create_rgb_histogram(img_array_original)

    # Equalize the RGB image
    equalized_image = equalize_rgb(image)
    
    # Create histogram for equalized RGB image
    img_array_equalized = np.array(equalized_image)
    histogram_equalized_image = create_rgb_histogram(img_array_equalized)

    # Convert images and histograms to base64
    original_image_base64 = image_to_base64(image)
    equalized_image_base64 = image_to_base64(equalized_image)
    histogram_original_base64 = image_to_base64(histogram_original_image)
    histogram_equalized_base64 = image_to_base64(histogram_equalized_image)
    
    return {
        "original_image": original_image_base64,
        "equalized_image": equalized_image_base64,
        "histogram_original": histogram_original_base64,
        "histogram_equalized": histogram_equalized_base64
    }

# Route to upload grayscale image
@app.post("/upload-grayscale/")
async def upload_grayscale(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert("L")

    # Equalize grayscale image
    equalized_image, img_array = equalize_grayscale(image)
    
    # Create histogram for original grayscale image
    histogram_image = create_grayscale_histogram(img_array)

    # Convert images to base64
    original_image_base64 = image_to_base64(image)
    equalized_image_base64 = image_to_base64(equalized_image)
    histogram_base64 = image_to_base64(histogram_image)
    
    return {
        "original_image": original_image_base64,
        "equalized_image": equalized_image_base64,
        "histogram": histogram_base64
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
