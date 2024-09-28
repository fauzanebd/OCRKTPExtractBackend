import easyocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
import re, textdistance
from ultralytics import YOLO

from app.utils.helpers import extract_date

class OCRService:
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance        

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        MODEL_DIR = 'yolo_models/best.pt'
        self.model = YOLO(MODEL_DIR)
        self.reader = easyocr.Reader(['id'])  # Assuming 'id' is the language code for Indonesian

    def preprocess_image(self, image_data):
        img = Image.open(io.BytesIO(image_data))
        img = img.convert('RGB')
        img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_cv2 = cv2.resize(img_cv2, (640, 480))
        img_blur = cv2.GaussianBlur(img_cv2, (3, 3), 0)

        img_pil = Image.fromarray(cv2.cvtColor(img_blur, cv2.COLOR_BGR2RGB))
        img_pil = img_pil.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(img_pil)
        img_pil = enhancer.enhance(2)
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def extract_ktp_data(self, image_data):
        preprocessed_image = self.preprocess_image(image_data)

        results = self.model.predict(preprocessed_image, imgsz=(480, 640), iou=0.7, conf=0.5)

        
        extracted_data = {}
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                class_name = self.model.names[int(box.cls[0])]
                
                cropped_img = preprocessed_image[y1:y2, x1:x2]
                ocr_result = self.reader.readtext(cropped_img)
                extracted_text = " ".join([detection[1] for detection in ocr_result if detection[2] > 0.5])
                extracted_data[class_name] = extracted_text

        if 'prov_kab' in extracted_data:
            prov_kab = extracted_data['prov_kab']
            if "KOTA" in prov_kab:
                provinsi, kabupaten = prov_kab.split("KOTA", 1)
                kabupaten = "KOTA " + kabupaten.strip()
            elif "KABUPATEN" in prov_kab:
                provinsi, kabupaten = prov_kab.split("KABUPATEN", 1)
                kabupaten = "KABUPATEN " + kabupaten.strip()
            elif "JAKARTA" in prov_kab:
                provinsi, kabupaten = prov_kab.split("JAKARTA", 1)
                kabupaten = kabupaten.strip()
                provinsi = "PROVINSI DKI JAKARTA"
            else:
                provinsi = prov_kab
                kabupaten = ""
            provinsi = provinsi.strip()

        if 'jk' in extracted_data:
            datatext = extracted_data['jk']
            if textdistance.levenshtein(datatext.upper(), "LAKI-LAKI") < textdistance.levenshtein(datatext.upper(), "PEREMPUAN"):
                extracted_data['jk'] = "LAKI-LAKI"
            else:
                extracted_data['jk'] = "PEREMPUAN"

        if 'ttl' in extracted_data:
            ttl = extracted_data['ttl']
            match = re.search(r'\d', ttl)
            if match:
                index = match.start()
                extracted_data['tempat_lahir'] = ttl[:index].strip()
                extracted_data['tgl_lahir'] = extract_date(ttl[index:].strip())

        if 'nik' in extracted_data:
            extracted_data['nik'] = re.sub(r'\D', '', extracted_data['nik'])

        return extracted_data

ocr_service = OCRService()