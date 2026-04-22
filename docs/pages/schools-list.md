# Список школ плавания

## 1. Маршрут
`GET /schools/`
Шаблон: `app/templates/schools_list.html`

## 2. Назначение
Каталог всех школ плавания на портале.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Заголовок
- Поиск по школам
- Список карточек школ
- Пагинация

## 5. Данные
Поля School:
- id, name, city, description
- logo_url, cover_url
- phone, email, website
- branches (количество филиалов)

## 6. Карточка школы
- Логотип
- Название
- Город
- Краткое описание
- Количество тренеров и спортсменов
- Кнопка "Подробнее" → /schools/{id}

## 7. Логика и поведение
- Показывать только is_active=True школы
- Поиск по названию и городу
- Частичное обновление через partials/school_items.html

## 8. Состояния
- Loading: skeleton
- Empty: "Школы не найдены"
- Error: сообщение

## 9. Связанные файлы
- `app/templates/schools_list.html`
- `app/templates/partials/school_items.html`
- `app/routers/schools.py`
- `app/services/school_service.py`

## 10. Критерии готовности
- [ ] Список школ отображается
- [ ] Поиск работает
- [ ] Карточки ведут на детальную страницу
- [ ] Empty state есть