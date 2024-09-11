import os
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
from starlette.responses import StreamingResponse
import cv2

app = FastAPI()

# Fungsi untuk membuat histogram RGB
def generate_rgb_histogram(image_path):
    image = Image.open(image_path).convert('RGB')
    r, g, b = image.split()  # Pisahkan channel RGB

    # Membuat histogram untuk setiap channel (R, G, B) dalam satu plot
    plt.figure(figsize=(6, 4))
    plt.hist(np.array(r).flatten(), bins=256, color='red', alpha=0.5, label='Red Channel')
    plt.hist(np.array(g).flatten(), bins=256, color='green', alpha=0.5, label='Green Channel')
    plt.hist(np.array(b).flatten(), bins=256, color='blue', alpha=0.5, label='Blue Channel')
    plt.title('RGB Histogram')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

# Fungsi untuk melakukan ekualisasi histogram gambar grayscale
def equalize_image_histogram(image_path):
    image = Image.open(image_path).convert('L')  # Convert to grayscale
    img_array = np.array(image)

    # Ekualisasi menggunakan OpenCV
    img_equalized = cv2.equalizeHist(img_array)

    # Membuat gambar dan histogram sebelum dan sesudah ekualisasi
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Tampilkan gambar asli grayscale
    axes[0, 0].imshow(img_array, cmap='gray')
    axes[0, 0].set_title("Original Image")
    axes[0, 0].axis('off')

    # Tampilkan histogram gambar asli grayscale
    axes[0, 1].hist(img_array.flatten(), bins=256, color='gray', alpha=0.7)
    axes[0, 1].set_title('Original Histogram')

    # Tampilkan gambar hasil ekualisasi
    axes[1, 0].imshow(img_equalized, cmap='gray')
    axes[1, 0].set_title("Equalized Image")
    axes[1, 0].axis('off')

    # Tampilkan histogram hasil ekualisasi
    axes[1, 1].hist(img_equalized.flatten(), bins=256, color='gray', alpha=0.7)
    axes[1, 1].set_title('Equalized Histogram')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf


@app.post("/upload-histogram/")
async def upload_histogram(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp_path = temp.name
    buf = generate_rgb_histogram(temp_path)
    os.remove(temp_path)  # Menghapus file sementara setelah selesai
    return StreamingResponse(buf, media_type="image/png")

@app.post("/upload-equalization/")
async def upload_equalization(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp_path = temp.name
    buf = equalize_image_histogram(temp_path)
    os.remove(temp_path)  # Menghapus file sementara setelah selesai
    return StreamingResponse(buf, media_type="image/png")

@app.get("/")
async def get_index():
    content = """
    <html>
    <head>
        <title>Image Upload and Processing</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-image: url('/static/background.jpg'); /* Ganti dengan path ke gambar latar belakang */
                background-size: cover; /* Menyesuaikan ukuran gambar dengan layar */
                background-position: center; /* Menyelaraskan gambar di tengah */
            }
            .container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                padding: 20px;
                background-color: rgba(255, 255, 255, 0.8); /* Warna latar belakang dengan transparansi */
                border-radius: 8px;
            }
            .image-box, .result-box {
                margin: 10px;
                padding: 10px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .image-box input[type="file"] {
                margin-bottom: 10px;
            }
            .result-box img {
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            h1 {
                text-align: center;
                color: #333;
                margin-top: 20px;
            }
            .upload-section {
                margin-bottom: 40px;
            }
            .upload-section h2 {
                color: #555;
            }
        </style>
    </head>
    <body>
        <div class="upload-section">
            <h1>Upload Image for RGB Histogram</h1>
            <div class="container">
                <div class="image-box">
                    <input type="file" id="imageInput" onchange="loadImage(event)">
                    <br><br>
                    <img id="uploadedImage" style="max-width: 300px;" />
                </div>
                <div class="result-box">
                    <img id="histogramResult" style="max-width: 300px;" />
                </div>
            </div>
        </div>
        <div class="upload-section">
            <h1>Upload New Image for Histogram Equalization</h1>
            <div class="container">
                <div class="image-box">
                    <input type="file" id="equalizeInput" onchange="loadEqualizedImage(event)">
                    <br><br>
                    <img id="uploadedEqualizeImage" style="max-width: 300px;" />
                </div>
                <div class="result-box">
                    <img id="equalizeResult" style="max-width: 300px;" />
                </div>
            </div>
        </div>

        <script>
            // Load and display the uploaded image for RGB histogram
            function loadImage(event) {
                var image = document.getElementById('uploadedImage');
                image.src = URL.createObjectURL(event.target.files[0]);

                var formData = new FormData();
                formData.append("file", event.target.files[0]);

                fetch('/upload-histogram/', {
                    method: 'POST',
                    body: formData
                }).then(response => response.blob())
                  .then(blob => {
                      var url = URL.createObjectURL(blob);
                      document.getElementById('histogramResult').src = url;
                  });
            }

            // Load and display the uploaded image for equalization
            function loadEqualizedImage(event) {
                var image = document.getElementById('uploadedEqualizeImage');
                image.src = URL.createObjectURL(event.target.files[0]);

                var formData = new FormData();
                formData.append("file", event.target.files[0]);

                fetch('/upload-equalization/', {
                    method: 'POST',
                    body: formData
                }).then(response => response.blob())
                  .then(blob => {
                      var url = URL.createObjectURL(blob);
                      document.getElementById('equalizeResult').src = url;
                  });
            }
            </script>
        </body>
    </html>

    """
    return HTMLResponse(content=content)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)