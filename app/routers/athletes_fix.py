# Временно заменим зависимость
# В файле app/routers/athletes.py найдите строки с @router.get("/my/personal-bests")
# и замените current_user: User = Depends(get_current_active_user)
# на current_user: User = Depends(get_current_user_optional_cookie)
