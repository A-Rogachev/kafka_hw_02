from typing import Final

BADWORD: Final[str] = "badword"
FORBIDDENWORD: Final[str] = "forbiddenword"

MIN_MOCK_USER_ID: Final[int] = 1
MAX_MOCK_USER_ID: Final[int] = 10


DEFAULT_BANNED_WORDS: Final[set[str]] = {BADWORD, FORBIDDENWORD}

DEFAULT_CHAR_MASK: Final[str] = "*"

BLOCK_USER_COMMENT_MAX_LENGTH: Final[int] = 100
USER_MESSAGE_MAX_LENGTH: Final[int] = 150

MOCK_MESSAGES_TIMEOUT: Final[int] = 2
