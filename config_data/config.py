from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str         # Название базы данных
    db_host: str          # URL-адрес базы данных
    db_user: str          # Username пользователя базы данных
    db_password: str      # Пароль к базе данных


@dataclass
class TgBot:
    token: str            # Токен бота
    admin_ids: list[int]  # Id администраторов бота
    admin_send_remind_id: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admin_send_remind_id=env('ADMIN_SEND_REMINDER'),
                               admin_ids=list(map(int, env.list('ADMIN_IDS')))),
                  db=DatabaseConfig(database=env('DATABASE'),
                                    db_host=env('DB_HOST'),
                                    db_user=env('DB_USER'),
                                    db_password=env('DB_PASSWORD')))