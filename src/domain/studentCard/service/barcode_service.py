from src.infrastructure.studentCard.external.barcode_reader import (
    BarcodeReaderInterface,
)


class BarcodeService:
    def __init__(self, reader: BarcodeReaderInterface):
        self._reader = reader

    async def extract_barcode(self, image_bytes: bytes) -> str:
        if not image_bytes:
            raise ValueError("이미지 데이터가 없습니다")
        return await self._reader.extract_barcode(image_bytes)
