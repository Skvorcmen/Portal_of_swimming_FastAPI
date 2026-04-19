from fastapi import FastAPI
from app.routers import auth

app = FastAPI(
    title="Спортивный портал по плаванию",
    description="Платформа для управления соревнованиями, заплывами и результатами",
    version="1.0.0",
)

# Подключаем роутеры API
app.include_router(auth.router)


@app.get("/")
def home():
    return {"message": "Портал по плаванию работает!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    print("PyCharm")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
