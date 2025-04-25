import psutil
import time
from collections import deque

# ==== Cấu hình hệ thống ====
CPU_THRESHOLD = 90     # %
RAM_THRESHOLD = 90     # %
MAX_WAIT_TIME = 30     # giây
MAX_QUEUE_SIZE = 20    # optional giới hạn queue

# ==== Queue toàn cục để theo dõi truy vấn đang đợi ====
traffic_queue = deque()

def is_system_overloaded(cpu_thresh=CPU_THRESHOLD, ram_thresh=RAM_THRESHOLD):
    """
    Kiểm tra xem hệ thống hiện tại có quá tải không.
    """
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.2)
    return mem.percent > ram_thresh or cpu > cpu_thresh

def queue_if_overloaded(user_id, query_type="chat"):
    """
    Nếu hệ thống quá tải, thêm người dùng vào hàng chờ và trả về True (nghĩa là cần dừng).
    Nếu hệ thống ổn, trả về False (có thể xử lý).
    """
    if is_system_overloaded():
        if not any(q["user"] == user_id for q in traffic_queue):
            traffic_queue.append({
                "user": user_id,
                "type": query_type,
                "timestamp": time.time()
            })
        return True
    return False

def check_and_dispatch(user_id):
    """
    Kiểm tra hàng chờ để xác định xem user hiện tại có được phép xử lý không.
    Trả về True nếu được xử lý, False nếu phải chờ.
    """
    global traffic_queue  # ✅ Khai báo ngay đầu hàm

    if is_system_overloaded():
        for req in traffic_queue:
            if req["user"] == user_id:
                wait_time = time.time() - req["timestamp"]
                return wait_time >= MAX_WAIT_TIME
        return False
    else:
        # Nếu user có trong queue thì xóa (đã đến lượt)
        traffic_queue = deque([q for q in traffic_queue if q["user"] != user_id])
        return True

def get_current_queue():
    """
    Trả về danh sách người đang chờ (để debug hoặc hiển thị UI nếu muốn).
    """
    return list(traffic_queue)

def clear_user_from_queue(user_id):
    """
    Gỡ user khỏi queue nếu cần manual xử lý.
    """
    global traffic_queue
    traffic_queue = deque([q for q in traffic_queue if q["user"] != user_id])
