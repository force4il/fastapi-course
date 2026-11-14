from fastapi import APIRouter, BackgroundTasks, UploadFile

from services.images import ImageService

router = APIRouter(prefix="/images", tags=["Изображения"])


@router.post("")
def upload_image(file: UploadFile, background_tasks: BackgroundTasks):
    ImageService().upload_image(file=file, background_tasks=background_tasks)
