from typing import Callable
from difflib import SequenceMatcher


remove_non_ascii: Callable[[str], str] = lambda text: "".join(
    char for char in text if 31 < ord(char) & ord(char) < 127
)

remove_cp932: Callable[[str], str] = lambda text: text.encode("cp932", "ignore").decode(
    "cp932"
)

################################################################
# n-gram algorithms implementation
################################################################


def __split_text(n: int, text: str) -> list[str]:
    return [text[i : i + n] for i in range(len(text) - (n - 1))]


def __get_ngram_score(text1_list: list[str], text2_list: list[str]) -> float:
    total_check_count = 0
    equal_count = 0

    for text1_word in text1_list:
        total_check_count = total_check_count + 1
        equal_flag = 0
        for text2_word in text2_list:
            if text1_word == text2_word:
                equal_flag = 1
        equal_count = equal_count + equal_flag

    return equal_count / total_check_count, (equal_count, total_check_count)


def get_similarity_score(text1: str, text2: str, n=2) -> float:
    """Returns n-gram score between two texts."""
    if len(text1) == 0 or len(text2) == 0:
        # print(
        #     f"WARNING: Text_list is empty. list1:{text1_list} , list2:{text2_list}"
        # )
        return 0

    # splitting text by 2-words (for bi-gram)
    text1_list = __split_text(n, text1)
    text2_list = __split_text(n, text2)

    # Check the text length and change the order before performing n-gram,
    # to take care if one of the texts are included in the another one.
    if len(text2_list) > len(text1_list):
        _tmp = text1_list
        text1_list = text2_list
        text2_list = _tmp

    score, _ = __get_ngram_score(text1_list, text2_list)

    return score


################################################################


def calc_text_length_rate(text1, text2):
    """Returns (text1_len / text2_len, text2_len / text1_len)"""
    text1_len = len(text1)
    text2_len = len(text2)

    return text1_len / text2_len, text2_len / text1_len


def calc_text_similarity(
    text1: str,
    text2: str,
):
    """Returns (n-gram score, text sequence similarity)"""
    # Calculate n-gram score
    similarity_ngram = get_similarity_score(
        text1,
        text2,
    )

    # Calculate characters similarity
    similarity_sqmatch = SequenceMatcher(None, text1, text2).ratio()

    return similarity_ngram, similarity_sqmatch
