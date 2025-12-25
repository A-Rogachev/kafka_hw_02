import ahocorasick

from ..core.const import DEFAULT_CHAR_MASK


class WordCensor:
    """
    Класс для цензуры слов в тексте.
    """

    def __init__(self, mask_char: str | None = None) -> None:
        self._automaton: ahocorasick.Automaton | None = None
        self._words_hash: int = 0
        self.mask_char: str = mask_char or DEFAULT_CHAR_MASK

    def build_automaton(self, banned_words: set[str]) -> None:
        """
        Строит автомат Aho-Corasick из списка запрещенных слов.

        :param banned_words: set[str], множество запрещенных слов

        :return: None
        """
        if not banned_words:
            self._automaton = None
            self._words_hash = 0
            return

        new_hash = hash(frozenset(banned_words))
        if new_hash == self._words_hash and self._automaton is not None:
            return

        A = ahocorasick.Automaton()
        for word in banned_words:
            if word:
                A.add_word(word.lower(), word)

        A.make_automaton()
        self._automaton = A
        self._words_hash = new_hash

    def censor_text(
        self, text: str, banned_words: set[str], mask_char: str | None
    ) -> str:
        """
        Маскировка запрещенных слов в тексте.

        :param text: str, исходный текст
        :param banned_words: set[str], множество запрещенных слов
        :param mask_char: str, символ для маскировки

        :return: str, текст с замаскированными словами
        """
        if not text or not banned_words:
            return text

        self.build_automaton(banned_words)
        if self._automaton is None:
            return text

        mask_char = mask_char or self.mask_char
        result = list(text)
        for end_index, original_word in self._automaton.iter(text.lower()):
            start = end_index - len(original_word) + 1
            for i in range(start, end_index + 1):
                if result[i] not in (" ", "\n", "\t"):
                    result[i] = mask_char
        return "".join(result)


_censor_instance = WordCensor(mask_char=DEFAULT_CHAR_MASK)


def censor_text(
    text: str,
    banned_words: set[str],
    mask_char: str | None = None,
) -> str:
    """
    Маскировка запрещенных слов в тексте.

    :param text: str, исходный текст
    :param banned_words: set[str], множество запрещенных слов
    :param mask_char: str | None, символ для маскировки запрещенных слов
        :default None, значение маски по-умолчанию

    :return: str, текст с замаскированными словами
    """
    return _censor_instance.censor_text(text, banned_words, mask_char)
