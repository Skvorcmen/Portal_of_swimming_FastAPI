# Список соревнований

## 1. Маршрут
`GET /competitions/page`
Шаблон: `app/templates/competitions_list.html`

## 2. Назначение
Отображает все соревнования портала.
Позволяет искать и фильтровать по названию, городу, статусу.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Заголовок страницы
- Панель поиска и фильтров (название, город, статус)
- Список карточек соревнований
- Пагинация

## 5. Данные
- Список Competition из БД
- Поля: id, name, description, start_date, end_date,
  venue, city, status, max_participants

## 6. Статусы соревнований
- draft — черновик
- active — идёт регистрация
- completed — завершено

## 7. Логика и поведение
- При загрузке показываются все соревнования
- Поиск через GET /competitions/search (HTMX partial)
- Частичное обновление через partials/competition_items.html
- Фильтры: name (строка), city (строка), status (выбор)
- Пагинация: page параметр

## 8. Состояния
- Loading: skeleton карточек
- Empty: "Соревнований не найдено"
- Error: сообщение об ошибке

## 9. Карточка соревнования
- Название
- Город и место проведения
- Даты (start_date — end_date)
- Статус (бейдж)
- Кнопка "Подробнее" → /competitions/{id}/page

## 10. Связанные файлы
- `app/templates/competitions_list.html`
- `app/templates/partials/competition_items.html`
- `app/routers/competitions.py`
- `app/services/competition_service.py`

## 11. Критерии готовности
- [ ] Список соревнований отображается
- [ ] Поиск и фильтры работают
- [ ] Пагинация работает
- [ ] Empty state есть
- [ ] Карточки ведут на детальную страницу