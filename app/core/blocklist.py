from datetime import datetime, timedelta
from collections import defaultdict

# Хранилище заблокированных IP (в продакшене использовать Redis)
blocked_ips = {}
failed_attempts = defaultdict(int)


def is_ip_blocked(ip: str) -> bool:
    """Проверка, заблокирован ли IP"""
    if ip in blocked_ips:
        if blocked_ips[ip] > datetime.now():
            return True
        else:
            del blocked_ips[ip]
    return False


def record_failed_attempt(ip: str) -> bool:
    """Запись неудачной попытки. Возвращает True если IP заблокирован"""
    failed_attempts[ip] += 1
    
    if failed_attempts[ip] >= 10:
        blocked_ips[ip] = datetime.now() + timedelta(minutes=15)
        return True
    return False


def reset_attempts(ip: str) -> None:
    """Сброс счётчика попыток"""
    if ip in failed_attempts:
        del failed_attempts[ip]
