from abc import ABC, abstractmethod
import cv2
import numpy as np
from pyzbar.pyzbar import decode

class BarcodeReaderInterface(ABC):
    @abstractmethod
    async def extract_barcode(self, image_bytes: bytes) -> str:
        pass

class BarcodeReader(BarcodeReaderInterface):
    async def extract_barcode(self, image_bytes: bytes) -> str:
        # 바이트를 numpy 배열로 변환
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 이미지 전처리
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 바코드 디코딩
        barcodes = decode(binary)
        if barcodes:
            return barcodes[0].data.decode('utf-8')
        return "" 