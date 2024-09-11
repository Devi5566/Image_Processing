import os
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
import cv2
from starlette.responses import FileResponse

# Buat aplikasi FastAPI
app = FastAPI()

# Setup untuk melayani file statis (CSS dan gambar)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Fungsi untuk membuat histogram RGB
def generate_rgb_histogram(image_path):
    image = Image.open(image_path).convert('RGB')
    r, g, b = image.split()

    # Membuat histogram untuk setiap channel RGB
    plt.figure(figsize=(6, 4))
    plt.hist(np.array(r).flatten(), bins=256, color='red', alpha=0.5, label='Red')
    plt.hist(np.array(g).flatten(), bins=256, color='green', alpha=0.5, label='Green')
    plt.hist(np.array(b).flatten(), bins=256, color='blue', alpha=0.5, label='Blue')
    plt.title('RGB Histogram')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

# Fungsi untuk membuat histogram Grayscale
def generate_grayscale_histogram(image_path):
    image = Image.open(image_path).convert('L')
    img_array = np.array(image)

    plt.figure(figsize=(6, 4))
    plt.hist(img_array.flatten(), bins=256, color='gray', alpha=0.7)
    plt.title('Grayscale Histogram')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

# Fungsi untuk melakukan ekualisasi histogram pada gambar grayscale
def equalize_image_histogram(image_path):
    image = Image.open(image_path).convert('L')
    img_array = np.array(image)

    # Ekualisasi menggunakan OpenCV
    img_equalized = cv2.equalizeHist(img_array)

    # Membuat gambar hasil ekualisasi
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Gambar asli
    axes[0].imshow(img_array, cmap='gray')
    axes[0].set_title("Original Image")
    axes[0].axis('off')

    # Gambar hasil ekualisasi
    axes[1].imshow(img_equalized, cmap='gray')
    axes[1].set_title("Equalized Image")
    axes[1].axis('off')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

# Fungsi untuk upload dan generate RGB histogram
@app.post("/upload-histogram/")
async def upload_histogram(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp_path = temp.name

    buf = generate_rgb_histogram(temp_path)
    os.remove(temp_path)  # Hapus file sementara setelah selesai
    return StreamingResponse(buf, media_type="image/png")

# Fungsi untuk upload dan equalized histogram grayscale
@app.post("/upload-equalization/")
async def upload_equalization(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp_path = temp.name

    buf = equalize_image_histogram(temp_path)
    os.remove(temp_path)  # Hapus file sementara setelah selesai
    return StreamingResponse(buf, media_type="image/png")

# Fungsi untuk upload dan generate Grayscale histogram
@app.post("/upload-histogram-grayscale/")
async def upload_histogram_grayscale(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp_path = temp.name

    buf = generate_grayscale_histogram(temp_path)
    os.remove(temp_path)  # Hapus file sementara setelah selesai
    return StreamingResponse(buf, media_type="image/png")

# Route untuk melayani halaman utama (index.html)
@app.get("/")
async def get_index():
    return HTMLResponse(open("index.html").read())

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
