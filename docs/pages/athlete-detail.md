# Профиль спортсмена

## 1. Маршрут
`GET /athletes/{athlete_id}`
Шаблон: `app/templates/athlete_detail.html`

## 2. Назначение
Публичный профиль спортсмена:
личные данные, школа, тренер, личные рекорды,
история участия в соревнованиях.

## 3. Доступ
Публичная страница.

## 4. Основные блоки
- Обложка (cover_url или от школы)
- Фото спортсмена (photo_url)
- Имя, дата рождения, пол, разряд
- Школа и тренер (со ссылками)
- Личные рекорды (PersonalBest)
  - по дисциплинам (дистанция + стиль + время)
- История заявок и результатов (Entry + HeatEntry)

## 5. Данные
- AthleteProfile (все поля)
- User (full_name)
- School (name)
- CoachProfile (имя тренера)
- PersonalBest[] (личные рекорды)
- Entry[] с результатами

## 6. Личные рекорды
Дисциплины:
- Дистанции: 50, 100, 200, 400, 800, 1500 м
- Стили: freestyle, breaststroke, backstroke,
  butterfly, medley
- Время в формате MM:SS.ms

## 7. Логика и поведение
- Если спортсмен не найден — 404
- Обложка: своя → школьная → заглушка
- Кнопка редактирования видна только самому
  спортсмену (current_user.id == athlete.user_id)
  или admin/coach

## 8. Связанные файлы
- `app/templates/athlete_detail.html`
- `app/routers/athletes.py`
- `app/services/athlete_service.py`
- `app/repositories/athlete_profile_repository.py`
- `app/repositories/personal_best_repository.py`

## 9. Критерии готовности
- [ ] Данные спортсмена отображаются
- [ ] Личные рекорды видны в удобном формате
- [ ] Ссылки на школу и тренера работают
- [ ] 404 при отсутствии
- [ ] Редактирование только для своих