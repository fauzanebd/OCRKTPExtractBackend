import base64
import easyocr
import cv2
import anthropic
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
import re, textdistance
from ultralytics import YOLO
from app import db

from app.utils.helpers import extract_date
from app.models.model_used import ModelUsed

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
    
    def extract_ktp_data_claude(self, image_data, user_id):
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        api_key = os.getenv('ANTHROPIC_API_KEY')
        client = anthropic.Anthropic(
            api_key=api_key,
        )
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            },
                        },
                        {
                            "type": "text",
                            "text": f"""
                                Extract the following information from the KTP (Kartu Tanda Penduduk) image and return it in JSON format snake_case:
                                - nik
                                - name 
                                - birth date
                                - gender (L or P)
                                - address
                            """
                        }
                    ]
                }
            ]
        )
        res = message.content[0].text
        # convert the response to a dictionary
        data = eval(res)
        return data
        

    def extract_ktp_data(self, image_data, user_id):
        preprocessed_image = self.preprocess_image(image_data)
        model = int(os.getenv('MODEL', 1))
        client_code = os.getenv('CLIENT_CODE')
        
        if model == 2:
            res = self.extract_ktp_data_claude(image_data, user_id)
            province_code, city_code, subdistrict_code = OCRService.convert_nik_to_locations(res['nik'])
            
            # insert model used
            model_used = ModelUsed(
                user_id=user_id,
                model_id=2,
            )
            
            db.session.add(model_used)
            db.session.commit()
            
            
            return {
                'client_code': client_code,
                'user_id': user_id,
                'model_id': 1,
                'province_code': province_code,
                'city_code': city_code,
                'subdistrict_code': subdistrict_code,
                'ward_code': None,
                'village_code': None,
                's3_file': '',
                'nik': res['nik'],
                'name': res['name'].title(),
                'birth_date': res['birth_date'],
                'gender': res['gender'],
                'address': res['address'],
                'no_phone': '',
                'no_tps': '',
                'is_party_member': False,
                'relation_to_candidate': '',
                'confirmation_status': '',
                'category': '',
                'positioning_to_candidate': '',
                'expectation_to_candidate': ''
            }
    
        results = self.model.predict(preprocessed_image, imgsz=(480, 640), iou=0.7, conf=0.5)

        # insert model used
        model_used = ModelUsed(
            user_id=user_id,
            model_id=1,
        )
        
        db.session.add(model_used)
        db.session.commit()
            
        data_pemilih = {}
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                class_name = self.model.names[int(box.cls[0])]
                
                cropped_img = preprocessed_image[y1:y2, x1:x2]
                ocr_result = self.reader.readtext(cropped_img)
                extracted_text = " ".join([detection[1] for detection in ocr_result if detection[2] > 0.5])
                data_pemilih[class_name] = extracted_text

        if 'prov_kab' in data_pemilih:
            prov_kab = data_pemilih['prov_kab']
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

        if 'jk' in data_pemilih:
            datatext = data_pemilih['jk']
            if textdistance.levenshtein(datatext.upper(), "LAKI-LAKI") < textdistance.levenshtein(datatext.upper(), "PEREMPUAN"):
                data_pemilih['jk'] = "LAKI-LAKI"
            else:
                data_pemilih['jk'] = "PEREMPUAN"

        if 'ttl' in data_pemilih:
            ttl = data_pemilih['ttl']
            match = re.search(r'\d', ttl)
            if match:
                index = match.start()
                data_pemilih['tempat_lahir'] = ttl[:index].strip()
                data_pemilih['tgl_lahir'] = extract_date(ttl[index:].strip())

        if 'nik' in data_pemilih:
            data_pemilih['nik'] = re.sub(r'\D', '', data_pemilih['nik'])
            province_code, city_code, subdistrict_code = OCRService.convert_nik_to_locations(data_pemilih['nik'])
            
            data_pemilih['province_code'] = province_code
            data_pemilih['city_code'] = city_code
            data_pemilih['subdistrict_code'] = subdistrict_code
            
        change_keys = {
            'nama': 'name',
            'alamat': 'address',
            'rt_rw': 'no_tps',
            'pekerjaan': 'job',
            'no_hp': 'no_phone',
            's3_filename': 's3_file'
        }
        
        for old_key, new_key in change_keys.items():
            if old_key in data_pemilih:
                data_pemilih[new_key] = data_pemilih.pop(old_key)
                
        return {
            'client_code': client_code,
            'user_id': user_id,
            'model_id': 1,
            'province_code': data_pemilih.get('province_code', None),
            'city_code': data_pemilih.get('city_code', None),
            'subdistrict_code': data_pemilih.get('subdistrict_code', None),
            'ward_code': None,
            'village_code': None,
            's3_file': data_pemilih.get('s3_file', ''),
            'nik': data_pemilih.get('nik', ''),
            'name': data_pemilih.get('name', ''),
            'birth_date': data_pemilih.get('tgl_lahir', None),
            'gender': data_pemilih.get('jk', 'L'),
            'address': data_pemilih.get('address', ''),
            'no_phone': data_pemilih.get('no_hp', ''),
            'no_tps': data_pemilih.get('no_tps', ''),
            'is_party_member': False,
            'relation_to_candidate': '',
            'confirmation_status': '',
            'category': '',
            'positioning_to_candidate': '',
            'expectation_to_candidate': ''
        }
    
    def convert_nik_to_locations(nik):
        # get 6 first digits of nik
        nik = str(nik)
        if len(nik) < 6:
            return None
        
        province_code = nik[:2]
        city_code =  province_code + '.' + nik[2:4] 
        subdistrict_code = city_code + '.' + nik[4:6]
        
        return province_code, city_code, subdistrict_code

ocr_service = OCRService()