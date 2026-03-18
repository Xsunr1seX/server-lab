from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import random
def generate_random_image(width, height, filename):
    img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(filename)
def generate_gradient_image(width, height, filename):
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    for i in range(width):
        for j in range(height):
            r = int(255 * i / width)
            g = int(255 * j / height)
            b = 128
            pixels[i, j] = (r, g, b)
    img.save(filename)
def generate_pattern_image(width, height, filename):
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    for _ in range(20):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        shape_type = random.choice(['rectangle', 'ellipse', 'line'])
        if shape_type == 'rectangle':
            draw.rectangle([x1, y1, x2, y2], fill=color)
        elif shape_type == 'ellipse':
            draw.ellipse([x1, y1, x2, y2], fill=color)
        else:
            draw.line([x1, y1, x2, y2], fill=color, width=3)
    img.save(filename)
def generate_checkerboard(width, height, filename, square_size=50):
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    for i in range(width):
        for j in range(height):
            if (i // square_size + j // square_size) % 2 == 0:
                pixels[i, j] = (255, 255, 255)  # Белый
            else:
                pixels[i, j] = (0, 0, 0)  # Черный
    img.save(filename)
def main():
    os.makedirs('test_images', exist_ok=True)
    sizes = [
        (100, 100),
        (320, 240),
        (640, 480),
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1920, 1080),
    ]
    total_images = 50
    for i in range(1, total_images + 1):
        size = sizes[i % len(sizes)]
        filename = f"test_images/image_{i:02d}.jpg"
        img_type = i % 4
        if img_type == 0:
            generate_random_image(*size, filename)
        elif img_type == 1:
            generate_gradient_image(*size, filename)
        elif img_type == 2:
            generate_pattern_image(*size, filename)
        else:
            generate_checkerboard(*size, filename)
    print(f" Сгенерировано {total_images} изображений")
    import glob
    images = glob.glob("test_images/*.jpg")
    total_size = sum(os.path.getsize(img) for img in images)
    print(f"Всего файлов: {len(images)}")
    print(f"Общий размер: {total_size / 1024 / 1024:.2f} MB")
if __name__ == '__main__':
    main()