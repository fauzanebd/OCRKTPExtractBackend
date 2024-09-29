import os
from dotenv import load_dotenv

load_dotenv(".env")

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_URI')