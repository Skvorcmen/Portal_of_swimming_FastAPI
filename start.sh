#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Запуск Swimming Portal в Docker...${NC}"

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Файл .env не найден, создаем из .env.example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Пожалуйста, отредактируйте .env и установите SECRET_KEY${NC}"
fi

# Останавливаем старые контейнеры
echo -e "${GREEN}🛑 Останавливаем старые контейнеры...${NC}"
docker-compose down

# Собираем и запускаем
echo -e "${GREEN}🏗️  Собираем и запускаем контейнеры...${NC}"
docker-compose up --build -d

# Ждем запуска
echo -e "${GREEN}⏳ Ждем запуска сервисов...${NC}"
sleep 10

# Проверяем статус
echo -e "${GREEN}📊 Статус контейнеров:${NC}"
docker-compose ps

# Выводим логи
echo -e "${GREEN}📋 Логи приложения:${NC}"
docker-compose logs --tail=20 web

echo -e "${GREEN}✅ Готово!${NC}"
echo -e "${GREEN}🌐 Приложение доступно по адресу: http://localhost:8000${NC}"
echo -e "${YELLOW}📝 Для просмотра логов: docker-compose logs -f${NC}"
echo -e "${YELLOW}🛑 Для остановки: docker-compose down${NC}"
