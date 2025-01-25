from aiogram import Bot, Dispatcher, types
    from aiogram.contrib.middlewares.logging import LoggingMiddleware
    from fastapi import FastAPI
    import sqlite3
    import uvicorn

    # Initialize FastAPI
    app = FastAPI()

    # Initialize SQLite database
    conn = sqlite3.connect('epicbot.db')
    c = conn.cursor()

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                 username TEXT,
                 language TEXT,
                 first_name TEXT,
                 last_name TEXT)''')
    conn.commit()

    # Mock wallet data
    mock_wallet = {
        'balance': 100.0,
        'address': 'epic1mockaddress1234567890',
        'transactions': []
    }

    # FastAPI Endpoints
    @app.get("/balance")
    async def get_balance():
        return {"balance": mock_wallet['balance']}

    @app.get("/address")
    async def get_address():
        return {"address": mock_wallet['address']}

    @app.post("/send")
    async def send_funds(amount: float, address: str):
        if amount > mock_wallet['balance']:
            return {"error": "Insufficient funds"}
        mock_wallet['balance'] -= amount
        mock_wallet['transactions'].append({
            'type': 'send',
            'amount': amount,
            'to': address
        })
        return {"status": "success", "new_balance": mock_wallet['balance']}

    # Telegram Bot Setup
    API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())

    @dp.message_handler(commands=['start'])
    async def send_welcome(message: types.Message):
        user = message.from_user
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?)",
                 (user.id, user.username, user.language_code, user.first_name, user.last_name))
        conn.commit()
        await message.reply("Welcome to Epic Tip Bot!")

    @dp.message_handler(commands=['balance'])
    async def send_balance(message: types.Message):
        await message.reply(f"Your balance: {mock_wallet['balance']} EPIC")

    if __name__ == '__main__':
        # Start FastAPI server
        uvicorn.run(app, host="0.0.0.0", port=8000)
