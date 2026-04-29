import time

def generate_case_id():
    return f"CASE-{int(time.time() * 1000)}"
