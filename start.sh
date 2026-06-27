#!/bin/bash
pip install -r requirements.txt flask-login gunicorn
gunicorn app:app --bind 0.0.0.0:$PORT
