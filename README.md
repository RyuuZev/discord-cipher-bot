# 🔐 Discord Cipher Bot

A Discord bot that enables users to send encrypted messages to each other with advanced security features including automatic expiration, attempt limiting, and secure key derivation.

## ✨ Features

- **🔒 End-to-End Encryption**: Messages are encrypted using Fernet (symmetric encryption) with PBKDF2-derived keys
- **👤 User Verification**: Only the intended recipient can open the encrypted message
- **⏰ Auto-Expiration**: Messages automatically delete after 24 hours
- **🔐 Attempt Limiting**: Maximum 5 failed decryption attempts before access is blocked
- **🗑️ Auto-Deletion**: Messages are deleted immediately after successful decryption
- **🎯 Interactive UI**: Discord modals and buttons for seamless user experience
- **📊 SQLite Database**: Persistent storage with message tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Discord Bot Token
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/RyuuZev/discord-cipher-bot.git
cd discord-cipher-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN
```

4. **Run the bot**
```bash
python main.py
```

## 📖 Usage

### Sending an Encrypted Message

1. Use the `/kirim_rahasia` command in Discord
2. Select the recipient user
3. Enter the message you want to encrypt
4. Create a **Secret Key** (share this with the recipient through a separate secure channel)
5. The bot sends an encrypted message card to the recipient

### Opening an Encrypted Message

1. Click the **🔓 Buka Pesan** button on the encrypted message
2. Enter the **Secret Key** in the modal dialog
3. If correct, the message is decrypted and displayed (then automatically deleted)
4. If incorrect, you can try again (max 5 attempts)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### Bot Permissions

The bot requires the following Discord permissions:
- `Send Messages`
- `Embed Links`
- `Use Slash Commands`
- `Use Application Commands`

## 🏗️ Project Structure

```
discord-cipher-bot/
├── main.py              # Main bot application
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🔐 Security Details

### Encryption Method

- **Algorithm**: Fernet (AES-128 in CBC mode with HMAC authentication)
- **Key Derivation**: PBKDF2-HMAC-SHA256 (200,000 iterations)
- **Salt**: Fixed salt for consistent key derivation across sessions

### Database

- **Type**: SQLite3 (`database.db`)
- **Tables**: 
  - `secret_messages` - Stores encrypted messages with metadata

### Data Storage

Each encrypted message record contains:
- `uuid` - Unique identifier for the message
- `sender_id` - Discord ID of the sender
- `receiver_id` - Discord ID of the intended recipient
- `ciphertext` - Encrypted message content
- `attempts` - Number of failed decryption attempts
- `created_at` - Message creation timestamp

## 🛡️ Security Features

- **Recipient Verification**: Messages can only be opened by the intended recipient
- **Expiration**: Messages expire after 24 hours
- **Attempt Limiting**: Access denied after 5 failed attempts
- **Message Destruction**: Messages are deleted from database immediately after successful decryption
- **Ephemeral Responses**: All responses are only visible to the relevant user
- **No Key Storage**: Secret keys are never stored, only used for encryption/decryption

## 📋 Commands

### `/kirim_rahasia`

Send an encrypted message to another user.

**Parameters:**
- `penerima` (Member) - The recipient of the message
- `pesan` (String) - The message content to encrypt

**Usage:**
```
/kirim_rahasia @User Pesan saya yang rahasia
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot doesn't respond to commands | Ensure bot has `/` slash command permissions in your server |
| "Secret key salah" error | Double-check the key was shared correctly |
| "Pesan sudah kedaluwarsa" | Message expired - messages only last 24 hours |
| "Terlalu banyak percobaan" | Exceeded 5 attempts, message is now locked |
| ImportError with dependencies | Run `pip install -r requirements.txt` again |

## 📦 Dependencies

- **discord.py** - Discord Bot API wrapper
- **cryptography** - Encryption library with Fernet support
- **python-dotenv** - Environment variable management

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs through GitHub Issues
- Suggest new features
- Submit pull requests with improvements

## 📝 License

This project is currently unlicensed. Feel free to use, modify, and distribute as needed.

## ⚠️ Disclaimer

This bot is provided as-is for educational purposes. While security best practices have been implemented, always ensure you understand the security implications of using this bot for sensitive information.

## 📞 Support

If you encounter issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review Discord.py documentation: https://discordpy.readthedocs.io/
3. Open an issue on GitHub

---

**Happy encrypting! 🔐**
