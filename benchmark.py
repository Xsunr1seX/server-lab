import requests
import time
from pathlib import Path
import json
def send_image(image_path):
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/jpeg')}
            response = requests.post('http://localhost:5000/upload', files=files, timeout=10)
            return response.status_code == 200
    except:
        return False
results = []
for n in [1, 2, 4]:
    input(f"Тест с {n} воркер(ами)")
    images = list(Path('test_images').glob('*.jpg'))[:20]
    start = time.time()
    success = sum(1 for img in images if send_image(img))
    total_time = time.time() - start
    speed = len(images) / total_time if total_time > 0 else 0
    results.append({
        'workers': n,
        'success': success,
        'total': len(images),
        'time': round(total_time, 2),
        'speed': round(speed, 2)
    })
    print(f"  Отправлено: {success}/{len(images)}")
    print(f"  Время: {total_time:.2f} сек")
    print(f"  Скорость: {speed:.2f} изобр/сек")
    input("Продолжить")
with open('benchmark_results.json', 'w') as f:
    json.dump(results, f, indent=2)