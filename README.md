# Проект нового телеграм- и вконтакте-бота  
## Цель  
Создать бота с возможностью более свободно отвечать на вопросы.  

## Технологии  
- Telegram
- VK API
- Python 3.10
- DialogFlow

## Инсталляция
1. Создать окружение  
> python -m venv venv  
> source venv/bin/activate  
2. Установить зависимости  
> python -m pip install --upgrade pip  
> pip install -r requirements.txt  
3. Завести (создать) переменные среды окружения:  
- TG_TOKEN=  
- VK_TOKEN=  
Для работы с DialogFlow:  
- GOOGLE_APPLICATION_CREDENTIALS=  
4. Загрузить список "intent" (образец в questions.json.example)  
> python upload_intents.py  
5. Запустить бота  
> python main.py или python main_vk.py  
