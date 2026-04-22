# Детальная страница соревнования

## 1. Маршрут
`GET /competitions/{competition_id}/page`
Шаблон: `app/templates/competition_detail.html`

## 2. Назначение
Полная информация о соревновании:
дисциплины, участники, результаты, возрастные категории.
Скачивание стартового листа и результатов.

## 3. Доступ
Публичная. Некоторые действия только для авторизованных.

## 4. Основные блоки
- Заголовок (название, статус, даты, место)
- Описание соревнования
- Возрастные категории
- Список дисциплин (SwimEvent)
- Участники по дисциплинам (Entry)
- Заплывы и результаты (Heat/HeatEntry)
- Кнопки скачивания PDF и CSV
- Кнопка "Подать заявку" (для athlete)
- Чат соревнования

## 5. Данные
- Competition (id, name, description, dates, venue, city, status)
- AgeCategory[] (возрастные категории)
- SwimEvent[] (дисциплины)
- Entry[] (заявки)
- Heat[] с HeatEntry[] (заплывы и результаты)

## 6. Логика и поведение
- Если competition не найдено — 404
- Кнопка "Подать заявку" видна только role=athlete
  и только если status=active
- Кнопки редактирования видны только admin/secretary
- PDF: GET /competitions/{id}/start-list.pdf
- PDF результаты: GET /competitions/{id}/results.pdf
- CSV результаты: GET /competitions/{id}/results.csv

## 7. Состояния
- Loading
- Not found: 404
- Нет дисциплин: "Дисциплины ещё не добавлены"
- Нет участников: "Заявок ещё нет"

## 8. Связанные файлы
- `app/templates/competition_detail.html`
- `app/routers/competitions.py`
- `app/routers/entries.py`
- `app/routers/heats.py`
- `app/services/competition_service.py`
- `app/services/pdf_service.py`
- `app/services/csv_service.py`

## 9. Критерии готовности
- [ ] Все данные соревнования отображаются
- [ ] Дисциплины и участники видны
- [ ] PDF и CSV скачиваются
- [ ] Кнопка заявки видна только athlete при active статусе
- [ ] Чат работает
- [ ] 404 при отсутствии соревнования