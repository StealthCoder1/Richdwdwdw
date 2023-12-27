from enum import StrEnum, auto


class LogLevel(StrEnum):
    DEBUG = auto()
    WARN = auto()
    ERROR = auto()
    INFO = auto()


class TaskType(StrEnum):
    AUTHORIZATION = auto()
    MAILER = auto()
    FIRST_MESSAGER = auto()
    INVITER = auto()


class Messages:
    RECONNECTING_ACCOUNT = "Переподключение к аккаунту..."
    ACCOUNT_CONNECTED = "Аккаунт подключен"
    LOGIN_ERROR = "Ошибка входа {}"

    NEW_CHANNEL_POST = 'Новая публикация в канале "{}"'

    LIMIT_REACHED = "Достигнут лимит отправленных сообщений"

    CHAT_NOT_CHANNEL = "Чат {} не является каналом"

    CONTACT_ADDED = "Добавил в контакты {}"
    JOINED_CHANNEL = "Вступил в канал {}"
    JOINED_CHAT = "Вступил в чат {}"
    MESSAGE_SENT = "Сообщение отправлено {}"
    COMMENTED_IN_CHANNEL = 'Оставил комментарий в канале "{}"'
    USER_INVITED_TO_CHAT = "Пользователь {} приглашён в {}"
    USERS_INVITED_TO_CHAT = "Пользователи приглашены в {}"
    MEMBER_PROMOTED = "Выдал права администратора пользователю {}"

    FAILED_ADD_CONTACT = "Не удалось добавить в контакты {} {}"
    FAILED_JOIN_CHANNEL = "Не удалось вступить в канал {} {}"
    FAILED_JOIN_CHAT = "Не удалось вступить в чат {} {}"
    FAILED_SEND_MESSAGE = "Не удалось отправить сообщение {} {}"
    FAILED_COMMENT = 'Не удалось оставить комментарий в канале "{}" {}'
    FAILED_INVITE_USER_TO_CHAT = "Не удалось пригласить пользователя {} в чат {} {}"
    FAILED_INVITE_USERS_TO_CHAT = "Не удалось пригласить пользователей в чат {} {}"
    FAILED_GET_MESSAGES = "Не удалось получить сообщения {} {}"

    FAILED_RESOLVE_USERNAME = "Не удалось"

    INTERNAL_ERROR = "Произошла внутренняя ошибка"
    FAILED_GET_CHAT_ADMINISTRATORS = "Ошибка получения администраторов, убедитесь, что Вы добавили бота @{} в администраторы чата или канала и разрешили добавлять новых участников и администраторов"
    FAILED_CHECK_PERMISSIONS = "Ошибка прав, убедитесь, что у бота @{} есть разрешения на добавление новых участников и администраторов"
    FAILED_GET_ME = "Не удалось получить информацию об аккаунте {}"
    FAILED_PROMOTE_MEMBER = "Не удалось выдать права администратора"


TELEGRAM_ERROR_CODES = {
    "PEER_FLOOD": "В настоящее время ваша учетная запись ограничена",
    "CHAT_ADMIN_REQUIRED": "Требуются права администратора чата",
    "FLOOD_WAIT_X": "Требуется ожидание в течение X секунд",
    "SLOWMODE_WAIT_X": "Для отправки сообщений в этом чате требуется ожидание в течение X секунд",
    "CHAT_ADMIN_INVITE_REQUIRED": "У вас нет прав приглашать других пользователей",
    "USER_IS_BLOCKED": "Пользователь заблокирован",
    "USER_NOT_MUTUAL_CONTACT": "Указанный пользователь не является общим контактом",
    "USER_PRIVACY_RESTRICTED": "Настройки конфиденциальности пользователя не позволяют вам выполнить это действие",
    "USERNAME_NOT_OCCUPIED": "Это имя пользователя никем не занято",
}
