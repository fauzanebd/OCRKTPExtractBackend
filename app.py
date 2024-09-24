from dotenv import load_dotenv

load_dotenv(".env")
import logging
import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from minio import Minio
from minio.error import S3Error
from ultralytics import YOLO
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import re, datetime, textdistance, time
import datetime
import time
import jwt
from functools import wraps
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
import io

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

app = Flask(__name__)
bcrypt = Bcrypt(app)


# Configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['ADMIN_EMAIL'] = os.getenv('ADMIN_EMAIL')

# Initialize extensions

# logger.debug(f"MONGO_URI: {app.config['MONGO_URI']}")

try:
    mongo = PyMongo(app)
    mongo.db.command('ping')
    # logger.debug("MongoDB connection successful")
    print("MongoDB connection successful")
except Exception as e:
    # logger.error(f"MongoDB connection failed: {str(e)}")
    print(f"MongoDB connection failed: {str(e)}")
    mongo = None
mail = Mail(app)

# MinIO configuration
minio_client = Minio(
    os.getenv('S3_ENDPOINT'),
    access_key=os.getenv('S3_ACCESS_KEY'),
    secret_key=os.getenv('S3_SECRET_KEY'),
    secure=True  # Set to True if using HTTPS
)
BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# Ensure bucket exists
try:
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
except S3Error as e:
    print(f"Error occurred, bucket may not exist: {str(e)}")

# Load YOLO model
MODEL_DIR = 'models/best.pt'
model = YOLO(MODEL_DIR)

# Initialize EasyOCR reader
reader = easyocr.Reader(['id'])

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        is_development = os.getenv('NODE_ENV', '') == 'development'
        if is_development:
            current_user = {'username': 'developer'}
            return f(current_user, *args, **kwargs)
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = mongo.db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                raise Exception('User not found')
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    existing_user = mongo.db.users.find_one({'username': data['username']})
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = {
        'username': data['username'],
        'password': hashed_password,
        'email': data['email'],
        'is_approved': True
    }
    result = mongo.db.users.insert_one(new_user)
    
    # # Send confirmation email to admin
    # send_confirmation_email(data['email'])
    
    return jsonify({'message': 'User registered. You can now login.'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({'username': data['username']})
    
    try:
        if user and bcrypt.check_password_hash(user['password'], data['password']) and user['is_approved']:
            token = jwt.encode({
                'user_id': str(user['_id']),
                'exp': datetime.datetime.now() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({'token': token})
    except ValueError:
        return jsonify({'message': 'Failed to login'}), 500
    
    return jsonify({'message': 'Invalid credentials or user not approved'}), 401

@app.route('/upload', methods=['POST'])
@token_required
def upload_image(current_user):
    if 'image' not in request.files:
        return jsonify({"error": True, "message": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": True, "message": "No selected file"}), 400
    
    try:
        # Save image to S3
        file_data = file.read()
        
        img = Image.open(io.BytesIO(file_data))
        
        # Image preprocessing
        img = img.convert('RGB')
        img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_cv2 = cv2.resize(img_cv2, (640, 480))
        img_blur = cv2.GaussianBlur(img_cv2, (3, 3), 0)

        img_pil = Image.fromarray(cv2.cvtColor(img_blur, cv2.COLOR_BGR2RGB))
        img_pil = img_pil.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(img_pil)
        img_pil = enhancer.enhance(2)
        img_cv2 = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # YOLO prediction
        results = model.predict(img_cv2, imgsz=(480, 640), iou=0.7, conf=0.5)

        extracted_data = {}
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                class_name = model.names[int(box.cls[0])]
                
                cropped_img = img_cv2[y1:y2, x1:x2]
                ocr_result = reader.readtext(cropped_img)
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

        file_size = len(file_data)
        s3_filename = f"ktp_nik_{extracted_data['nik']}_{datetime.datetime.now().strftime('%Y%m%d')}.jpg"
        minio_client.put_object(
            BUCKET_NAME, s3_filename, io.BytesIO(file_data), file_size
        )
        file.close()
        # Get image from MinIO
        response = minio_client.get_object(BUCKET_NAME, s3_filename)
        

        response = {
            "error": False,
            "message": "OCR Success!",
            "data": extracted_data,
            "s3_filename": s3_filename
        }
        return jsonify(response), 200
    
    except S3Error as e:
        return jsonify({"error": True, "message": f"MinIO Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

@app.route('/save_data', methods=['POST'])
@token_required
def save_data(current_user):
    data = request.get_json()
    
    # try:
    ktp_data = {
        'nik': data['nik'],
        'nama': data['nama'],
        'alamat': data['alamat'],
        'prov_kab': data['prov_kab'],
        'rt_rw': data['rt_rw'],
        'tempat_lahir': data['tempat_lahir'],
        'tgl_lahir': data['tgl_lahir'],
        'pekerjaan': data['pekerjaan'],
        's3_filename': data['s3_filename'],
        'reported_by': current_user['username'],
        'reported_at': datetime.datetime.now()
    }
    
    result = mongo.db.extracted_data.insert_one(ktp_data)
    
    return jsonify({"message": "Data saved successfully", "id": str(result.inserted_id)}), 200
    # except Exception as e:
    #     return jsonify({"error": True, "message": str(e)}), 500

# def send_confirmation_email(user_email):
#     msg = Message('New User Registration',
#                   sender=app.config['MAIL_USERNAME'],
#                   recipients=[app.config['ADMIN_EMAIL']])
#     msg.body = f"A new user with email {user_email} has registered. Please approve their account."
#     mail.send(msg)

def extract_date(date_text):
    try:
        match = re.search(r"(\d{1,2})([-/\.])(\d{2})\2(\d{4})", date_text)
        if match:
            day, month, year = int(match.group(1)), int(match.group(3)), int(match.group(4))
            return datetime.datetime(year, month, day)
        parsed_date = datetime.datetime.strptime(date_text, "%Y %m-%d")
        return parsed_date
    except ValueError:
        pass

    try:
        parsed_date = datetime.datetime.strptime(date_text, "%d%m %Y")
        return parsed_date
    except ValueError:
        pass

    try:
        parsed_date = datetime.datetime.strptime(date_text, "%d %m-%Y")
        return parsed_date
    except ValueError:
        pass

    date_pattern = r"(\d{1,4})(?:[-/\.])(\d{1,2})(?:[-/\.])(\d{2,4})"
    match = re.search(date_pattern, date_text)
    if match:
        day, month, year = map(lambda x: int(x) if 1 <= int(x) <= 31 else None, match.groups())
        if day is not None and month is not None and year is not None:
            try:
                return datetime.datetime(year, month, day)
            except ValueError:
                return None
    return None

if __name__ == '__main__':
    app.run(debug=True)