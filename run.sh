#!/bin/bash

echo "==> Đang chạy server với Gunicorn..."
gunicorn -c gunicorn.conf.py app:app
