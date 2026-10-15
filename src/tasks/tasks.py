from time import sleep
from PIL import Image
from pathlib import Path


from src.tasks.celery_app import celery_instance


@celery_instance.task
def test_task():
    sleep(5)
    print("Its done")


@celery_instance.task
def resize_image(image_path: str):
    sizes = [i for i in range(1000, 10000, 1000)]
    output_folder = "src/static/images/"

    img = Image.open(image_path)
    filename = Path(image_path).name
    ext = Path(image_path).suffix

    for size in sizes:
        img_resized = img.resize((size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS)
        new_filename = f"{filename}_{size}px{ext}"
        output_path = Path(output_folder) / new_filename

        img_resized.save(output_path.absolute())
