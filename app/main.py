from fastapi import FastAPI
from starlette import status

app = FastAPI(
    title="Спортивный портал по плаванию",
    description="Платформа для проведения соревнований по плаванию, Новости в сфере плавания, Обучающие материалы",
    version="1.0.0",
)


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
