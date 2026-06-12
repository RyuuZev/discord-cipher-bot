import os
import uuid
import base64
import sqlite3
import hashlib
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord import app_commands
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

DB = sqlite3.connect("database.db")
CURSOR = DB.cursor()

CURSOR.execute("""
CREATE TABLE IF NOT EXISTS secret_messages (
    uuid TEXT PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    ciphertext TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
)
""")
DB.commit()


def derive_key(password: str) -> bytes:
    salt = b"secret-discord-bot-v2"
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        200_000
    )
    return base64.urlsafe_b64encode(key)


def encrypt_message(message: str, password: str) -> str:
    return Fernet(
        derive_key(password)
    ).encrypt(message.encode()).decode()


def decrypt_message(ciphertext: str, password: str) -> str:
    return Fernet(
        derive_key(password)
    ).decrypt(ciphertext.encode()).decode()


class KeyModal(discord.ui.Modal, title="Masukkan Secret Key"):

    key = discord.ui.TextInput(
        label="Secret Key",
        required=True,
        max_length=100
    )

    def __init__(self, secret_uuid: str):
        super().__init__()
        self.secret_uuid = secret_uuid

    async def on_submit(self, interaction: discord.Interaction):

        CURSOR.execute(
            """
            SELECT receiver_id,ciphertext,attempts,created_at
            FROM secret_messages
            WHERE uuid=?
            """,
            (self.secret_uuid,)
        )

        data = CURSOR.fetchone()

        if not data:
            await interaction.response.send_message(
                "❌ Pesan sudah dihapus atau tidak ditemukan.",
                ephemeral=True
            )
            return

        receiver_id, ciphertext, attempts, created_at = data

        if interaction.user.id != receiver_id:
            await interaction.response.send_message(
                "❌ Pesan ini bukan untukmu.",
                ephemeral=True
            )
            return

        created = datetime.fromisoformat(created_at)

        if datetime.utcnow() - created > timedelta(hours=24):
            CURSOR.execute(
                "DELETE FROM secret_messages WHERE uuid=?",
                (self.secret_uuid,)
            )
            DB.commit()

            await interaction.response.send_message(
                "⌛ Pesan sudah kedaluwarsa.",
                ephemeral=True
            )
            return

        if attempts >= 5:
            await interaction.response.send_message(
                "❌ Terlalu banyak percobaan.",
                ephemeral=True
            )
            return

        try:
            plaintext = decrypt_message(
                ciphertext,
                str(self.key)
            )

            CURSOR.execute(
                "DELETE FROM secret_messages WHERE uuid=?",
                (self.secret_uuid,)
            )
            DB.commit()

            await interaction.response.send_message(
                f"🔓 **Pesan Rahasia**\n\n{plaintext}\n\n(Pesan telah dihancurkan)",
                ephemeral=True
            )

        except InvalidToken:

            CURSOR.execute(
                """
                UPDATE secret_messages
                SET attempts = attempts + 1
                WHERE uuid=?
                """,
                (self.secret_uuid,)
            )
            DB.commit()

            await interaction.response.send_message(
                "❌ Secret key salah.",
                ephemeral=True
            )


class OpenMessageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔓 Buka Pesan",
        style=discord.ButtonStyle.green,
        custom_id="secret_open_button_v2"
    )
    async def open_secret(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        try:
            secret_uuid = interaction.message.embeds[0].footer.text.replace(
                "UUID: ",
                ""
            )

            await interaction.response.send_modal(
                KeyModal(secret_uuid)
            )

        except Exception:
            await interaction.response.send_message(
                "❌ Data pesan rusak.",
                ephemeral=True
            )


class SecretBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.default()
        )

    async def setup_hook(self):
        self.add_view(OpenMessageView())
        await self.tree.sync()


bot = SecretBot()


@bot.tree.command(
    name="kirim_rahasia",
    description="Kirim pesan rahasia ke seseorang"
)
async def kirim_rahasia(
    interaction: discord.Interaction,
    penerima: discord.Member,
    pesan: str
):

    class SecretKeyModal(discord.ui.Modal, title="Buat Secret Key"):

        key = discord.ui.TextInput(
            label="Secret Key",
            placeholder="Bagikan key ini ke penerima lewat jalur lain",
            required=True
        )

        async def on_submit(self, modal_interaction):

            secret_uuid = str(uuid.uuid4())

            ciphertext = encrypt_message(
                pesan,
                str(self.key)
            )

            CURSOR.execute(
                """
                INSERT INTO secret_messages
                (
                    uuid,
                    sender_id,
                    receiver_id,
                    ciphertext,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    secret_uuid,
                    interaction.user.id,
                    penerima.id,
                    ciphertext,
                    datetime.utcnow().isoformat()
                )
            )

            DB.commit()

            embed = discord.Embed(
                title="📩 Pesan Rahasia",
                description=(
                    f"Untuk {penerima.mention}\n\n"
                    "Tekan tombol di bawah untuk membuka pesan."
                ),
                color=discord.Color.blurple()
            )

            embed.set_footer(
                text=f"UUID: {secret_uuid}"
            )

            await modal_interaction.response.send_message(
                embed=embed,
                view=OpenMessageView()
            )

    await interaction.response.send_modal(
        SecretKeyModal()
    )


@bot.event
async def on_ready():
    print(f"Login sebagai {bot.user}")


bot.run(TOKEN)