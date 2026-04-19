from jose import jwt
from datetime import datetime

SECRET_KEY = "your-super-secret-key-change-this-in-production-123456789"
ALGORITHM = "HS256"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsImV4cCI6MTc3NjU4OTY3Nn0.NRfhx6EyHlNDapDULUeBy1Rn13aD53jwRjv15FI2X10"

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("✅ Токен валиден!")
    print(f"user_id: {payload.get('sub')}")
    print(f"expires: {datetime.fromtimestamp(payload.get('exp'))}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
