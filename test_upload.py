import requests
from PIL import Image
import io
img = Image.new('RGB', (100, 100), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)
files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
response = requests.post('http://localhost:5000/upload', files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")