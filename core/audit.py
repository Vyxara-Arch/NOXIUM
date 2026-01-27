import datetime


class AuditLog:
    _logs = []
    MAX_ENTRIES = 200

    @staticmethod
    def log(action: str, details: str, level: str = "INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {action}: {details}"
        AuditLog._logs.append(entry)
        if len(AuditLog._logs) > AuditLog.MAX_ENTRIES:
            AuditLog._logs = AuditLog._logs[-AuditLog.MAX_ENTRIES :]

    @staticmethod
    def get_logs():
        return AuditLog._logs
