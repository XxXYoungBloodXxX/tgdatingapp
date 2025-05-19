# 🇵🇭 Pinoy Anonymous Dating Telegram Bot

Welcome to the Pinoy Anonymous Dating Bot!  
This Telegram bot lets users chat and date anonymously, similar to Omegle or Tinder, but focused on the Philippines.  
Users can set their gender, age, and location preferences, and the bot will match them with others who are also searching.

---

## 🚀 Features

- **Anonymous Chat:** Users are matched and chat without revealing their identity.
- **Preferences:** Match by gender, age group, and Philippine city/province.
- **Content Filtering:** Blocks offensive words.
- **Admin Reporting:** Users can report bad behavior.
- **Simple Commands:** Easy to use for everyone.

---

## 🛠️ How to Run This Bot

### 1. Clone the Repository

git clone
https://github.com/XxXYoungBloodXxX/tgdatingapp/
cd tgdatingapp
pip install -r requirements.txt

### 2. Install Requirements

Make sure you have Python 3.9+ and Redis installed.  
Install the required Python libraries:



### 3. Set Up Your Environment Variables

- Copy `.env.example` to `.env`:

run this on termux terminal
`cp .env.example .env`
- Edit `.env` and fill in your **Telegram bot token**, **admin Telegram ID**, and other settings:
`BOT_TOKEN=your-telegram-bot-token-here
ADMIN_IDS=your-telegram-user-id
REDIS_URL=redis://localhost:6379/0
BLOCKED_WORDS=badword1,badword2`


> **Never share your real `.env` file publicly!**

### 4. Run Redis

If you’re on Termux or Linux, start Redis with:
redis-server


Or, if you use Docker:

docker run -p 6379:6379 redis


### 5. Start the Bot



You should see `Bot started!` in your terminal.

---

## 💬 How Users Use the Bot

1. **Start the bot:**  
   `/start`

2. **Set your preferences:**  
   `/gender male`  
   `/age 18-25`  
   `/location cebu city`

3. **Find a match:**  
   `/find`  
   (Wait for the bot to notify you when matched.)

4. **Chat anonymously!**

5. **Stop chatting:**  
   `/stop`

6. **Report a user:**  
   `/report [reason]`

---

## 📝 Example Commands

/gender female
/age 26-35
/location manila
/find
/stop
/report spammer


---

## 🛡️ Safety

- The bot filters offensive words (set in `.env`).
- Users can report bad behavior to admins.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first.

---

## 📄 License

MIT License

---

**Enjoy chatting and making new friends anonymously!**  
If you have any issues, please open an issue on GitHub or contact the repo owner.


