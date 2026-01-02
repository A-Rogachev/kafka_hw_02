from typing import Final

BADWORD: Final[str] = "badword"
FORBIDDENWORD: Final[str] = "forbiddenword"
DEFAULT_BANNED_WORDS: Final[set[str]] = {BADWORD, FORBIDDENWORD}
DEFAULT_CHAR_MASK: Final[str] = "*"

MIN_MOCK_USER_ID: Final[int] = 1
MAX_MOCK_USER_ID: Final[int] = 10
USER_MESSAGE_MAX_LENGTH: Final[int] = 150
BLOCK_USER_COMMENT_MAX_LENGTH: Final[int] = 10
MOCK_MESSAGES_TIMEOUT: Final[int] = 2

DAY_SECONDS: Final[int] = 24 * 60 * 60
