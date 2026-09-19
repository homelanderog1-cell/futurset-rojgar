import requests
import time

def verify():
    endpoints = [
        ('Health Check', 'http://127.0.0.1:8000/health'),
        ('Main Home Page', 'http://127.0.0.1:8000/'),
        ('Gujarat Portal', 'http://127.0.0.1:8000/gujarat'),
        ('B.Tech CSE Portal', 'http://127.0.0.1:8000/btech-cse'),
        ('B.Tech API All', 'http://127.0.0.1:8000/api/jobs/btech-cse'),
        ('B.Tech API Central', 'http://127.0.0.1:8000/api/jobs/btech-cse?category=central_govt'),
        ('B.Tech API Gujarat', 'http://127.0.0.1:8000/api/jobs/btech-cse?category=gujarat_govt'),
        ('B.Tech API PSU', 'http://127.0.0.1:8000/api/jobs/btech-cse?category=psu'),
        ('B.Tech API Private', 'http://127.0.0.1:8000/api/jobs/btech-cse?category=private'),
        ('Direct Merit Jobs', 'http://127.0.0.1:8000/api/jobs?selection_mode=direct_merit'),
        ('Walk-in Jobs', 'http://127.0.0.1:8000/api/jobs?selection_mode=walk_in'),
        ('Apprentice Jobs', 'http://127.0.0.1:8000/api/jobs?selection_mode=apprenticeship'),
        ('Portal Stats API', 'http://127.0.0.1:8000/api/stats')
    ]

    all_pass = True
    for name, url in endpoints:
        try:
            r = requests.get(url, timeout=5)
            extra = ''
            if r.status_code == 200:
                if 'application/json' in r.headers.get('content-type', ''):
                    data = r.json()
                    if 'count' in data:
                        extra = f"Count: {data['count']}"
                    elif 'total_jobs' in data:
                        extra = f"Total: {data['total_jobs']} jobs ({data['total_vacancies']:,} vac), B.Tech: {data['btech_cse_jobs']} ({data['btech_cse_vacancies']:,} vac)"
                elif 'text/html' in r.headers.get('content-type', ''):
                    extra = f"HTML Size: {len(r.text)} bytes"
            else:
                all_pass = False
            print(f"[{'PASS' if r.status_code == 200 else 'FAIL'}] {name:20} HTTP {r.status_code} | {extra}")
        except Exception as e:
            all_pass = False
            print(f"[ERROR] {name:20} -> {e}")

    print("\nOverall Status:", "ALL ENDPOINTS WORKING PERFECTLY!" if all_pass else "FAILURES DETECTED")

if __name__ == '__main__':
    verify()
