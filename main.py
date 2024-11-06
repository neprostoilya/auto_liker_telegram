import asyncio
import os
import re
from datetime import datetime, time
from dotenv import load_dotenv
from pyrogram import Client, filters

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

async def choose_reaction():
    print("\nВыберите эмодзи для реакции:")
    print("1. ❤️")
    print("2. 👍") 
    print("3. 🔥")
    print("4. 👏")
    print("5. 💩")
    print("6. 🎉")
    
    choice = input("Введите номер эмодзи (1-6): ")
    reactions = {"1": "❤️", "2": "👍", "3": "🔥", "4": "👏", "5": "💩", "6": "🎉"}
    return reactions.get(choice, "❤️")

async def main():
    print("\nПодключение к Telegram...")
    async with Client("my_account", API_ID, API_HASH) as app:
        me = await app.get_me()
        print(f"Успешная авторизация как: {me.first_name} (@{me.username})")
        
        dialogs = []
        print("\nПолучение списка супергрупп...")
        async for dialog in app.get_dialogs():
            print(f"Проверка диалога: {dialog.chat.type} - {getattr(dialog.chat, 'title', 'Без названия')}")
            if str(dialog.chat.type) == "ChatType.SUPERGROUP": 
                dialogs.append(dialog)
                print(f"✅ Добавлена супергруппа: {dialog.chat.title}")
                
        print(f"\nВсего найдено супергрупп: {len(dialogs)}")
        
        if not dialogs:
            print("\nНе найдено доступных супергрупп.")
            print("Убедитесь, что:")
            print("1. Вы состоите хотя бы в одной супергруппе")
            print("2. У вас есть доступ к этим группам")
            print("3. Группы действительно являются супергруппами (обычно большие группы автоматически становятся супергруппами)")
            return
            
        print(f"\nДоступные супергруппы ({len(dialogs)}):")
        for i, dialog in enumerate(dialogs, 1):
            chat_type = {
                "private": "Личный чат",
                "group": "Группа",
                "supergroup": "Супергруппа",
                "channel": "Канал"
            }.get(dialog.chat.type, dialog.chat.type)
            
            print(f"{i}. {dialog.chat.title or dialog.chat.first_name} [{chat_type}]")
        
        while True:
            try:
                group_index = int(input("\nВыберите номер чата: ")) - 1
                if 0 <= group_index < len(dialogs):
                    break
                print(f"Пожалуйста, введите число от 1 до {len(dialogs)}")
            except ValueError:
                print("Пожалуйста, введите корректное число")
        
        selected_chat = dialogs[group_index].chat.id
        
        print("\nВыберите режим работы:")
        print("1. Лайкать сообщения определенного пользователя")
        print("2. Лайкать сообщения по времени")
        print("3. Лайкать сообщения по ключевому слову")
        
        mode = input("Выберите режим (1-3): ")
        reaction = await choose_reaction()
        
        if mode == "1":
            user_id = input("Введите username пользователя (без @): ")
            
            @app.on_message(filters.chat(selected_chat) & filters.user(user_id))
            async def like_user_messages(client, message):
                await message.react(reaction)
                print(f"Поставлена реакция {reaction} на сообщение от {user_id}")
                
        elif mode == "2":
            start_time = input("Введите время начала (ЧЧ:ММ): ")
            end_time = input("Введите время окончания (ЧЧ:ММ): ")
            start_h, start_m = map(int, start_time.split(":"))
            end_h, end_m = map(int, end_time.split(":"))
            
            @app.on_message(filters.chat(selected_chat))
            async def like_time_messages(client, message):
                current_time = datetime.now().time()
                start = time(start_h, start_m)
                end = time(end_h, end_m)
                
                if start <= current_time <= end:
                    await message.react(reaction)
                    
        elif mode == "3":
            keyword = input("Введите ключевое слово для поиска: ")
            
            @app.on_message(filters.chat(selected_chat))
            async def like_keyword_messages(client, message):
                if message.text and re.search(keyword, message.text, re.IGNORECASE):
                    await message.react(reaction)
        
        print("\nАвто-лайкер запущен! Нажмите Ctrl+C для остановки.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nРабота автолайкера завершена.")

asyncio.run(main())