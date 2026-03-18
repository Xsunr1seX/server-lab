import pika
import cv2
import os
import json
import time
from pathlib import Path
import numpy as np

class ImageProcessorWorker:
    def __init__(self, rabbitmq_host='localhost', input_queue='image_tasks', 
                 output_dir='result'):
    
        self.rabbitmq_host = rabbitmq_host
        self.input_queue = input_queue
        self.output_dir = Path(output_dir)
        # Создаем директорию для результатов, если её нет
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Параметры подключения к RabbitMQ
        self.connection = None
        self.channel = None
        
        # Доступные фильтры
        self.filters = {
            'grayscale': self.apply_grayscale,
            'blur': self.apply_blur,
            'edge_detection': self.apply_edge_detection,
            'sepia': self.apply_sepia,
            'invert': self.apply_invert,
            'sharpen': self.apply_sharpen
        }
        
    def connect_rabbitmq(self):
        """Установка соединения с RabbitMQ"""
        try:
            
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbitmq_host, port=5672)
            )
            self.channel = self.connection.channel()
            
            # Объявляем очередь (устойчивая)
            self.channel.queue_declare(
                queue=self.input_queue,
                durable=True
            )
            
            # Настройка QoS (prefetch_count=1 для fair dispatch)
            self.channel.basic_qos(prefetch_count=1)
            
            
        except Exception as e:
            raise
    # Черно-белый фильтр
    def apply_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Размытие по Гауссу
    def apply_blur(self, image, kernel_size=(5, 5)):
        return cv2.GaussianBlur(image, kernel_size, 0)
    # Обнаружение границ
    def apply_edge_detection(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    #Сепия фильтр
    def apply_sepia(self, image):
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        sepia = cv2.transform(image, kernel)
        sepia = np.clip(sepia, 0, 255)
        return sepia.astype(np.uint8)
    # Инвертирование цветов
    def apply_invert(self, image):

        return cv2.bitwise_not(image)
    # Увеличение резкости
    def apply_sharpen(self, image):
        kernel = np.array([[-1, -1, -1],
                          [-1, 9, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)
    
    def process_image(self, image_path, filter_name):
        try:
            # Проверяем существование файла
            if not os.path.exists(image_path):
                return None
            
            # Загружаем изображение
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            
            # Применяем фильтр
            if filter_name in self.filters:
                processed_image = self.filters[filter_name](image)
            else:
                processed_image = self.apply_grayscale(image)
            
            return processed_image
            
        except Exception as e:
            return None
    
    def save_result(self, image, original_path, filter_name):
        try:
            # Создаем имя файла для результата
            original_filename = Path(original_path).stem
            extension = Path(original_path).suffix
            timestamp = int(time.time())
            
            output_filename = f"{original_filename}_{filter_name}_{timestamp}{extension}"
            output_path = self.output_dir / output_filename
            
            # Сохраняем изображение
            cv2.imwrite(str(output_path), image)
           
            return str(output_path)
            
        except Exception as e:
            return None
    
    def callback(self, ch, method, properties, body):
        try:
            message = json.loads(body.decode())

            task_id = message.get("task_id")
            filename = message.get("filename")
            filter_name = message.get("operation", "blur")

            image_path = os.path.join("/app/uploads", filename)

            print(f"Processing {filename}", flush=True)

            processed_image = self.process_image(image_path, filter_name)

            if processed_image is None:
                raise Exception("Processing failed")

        # сохраняем картинку
            result_image_path = os.path.join("/app/results", f"{task_id}.jpg")
            cv2.imwrite(result_image_path, processed_image)

        # сохраняем json
            result_json_path = os.path.join("/app/results", f"{task_id}.json")
            with open(result_json_path, "w") as f:
                json.dump({"status": "done"}, f)

            print(f"Done {task_id}", flush=True)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"ERROR: {e}", flush=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    
    def start_consuming(self):
        """Запуск потребителя"""
        try:
            self.connect_rabbitmq()
            
            # Начинаем слушать очередь
            self.channel.basic_consume(
                queue=self.input_queue,
                on_message_callback=self.callback
            )
            
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise e
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                


import os

import os

if __name__ == "__main__":
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    queue = os.getenv("QUEUE_NAME", "image_tasks")
    out = os.getenv("RESULT_DIR", "/app/results")

    print(f"HOST={host}", flush=True)
    print(f"QUEUE={queue}", flush=True)
    print(f"RESULT_DIR={out}", flush=True)

    worker = ImageProcessorWorker(
        rabbitmq_host=host,
        input_queue=queue,
        output_dir=out
    )

    print("Worker started", flush=True)
    worker.start_consuming()