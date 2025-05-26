# gunicorn.conf.py
workers = 8               # Số lượng worker process (CPU cores * 2 nếu nhẹ)
threads = 100             # Số lượng threads mỗi worker (spam nhanh)
worker_class = "gthread"  # Dùng gthread phù hợp xử lý IO (requests)
bind = "0.0.0.0:81"
timeout = 120             # Tăng timeout nếu spam chậm
loglevel = "error"        # Ẩn bớt log cho nhẹ
