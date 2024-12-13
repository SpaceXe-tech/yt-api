from app.models import EnvVariables
from dotenv import dotenv_values

loaded_config = EnvVariables(**dotenv_values())
"""Loaded from .env file"""
