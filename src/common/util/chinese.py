import random

from pathlib import Path

word_list_file_path = Path(__file__).parent / "chinese_word_list.txt"

index = 0

word_list = []
with open(word_list_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        word = line.strip()
        words = word.split(" ")
        word_list.extend(words)
total_len = len(word_list)
has_choiced = set()

def random_word() -> str:
    return random.choice(word_list)

def random_word_no_repeat() -> str:
    while True:
        word = random_word()
        if word not in has_choiced:
            has_choiced.add(word)
            return word
        
def next_word() -> str:
    global index
    if index >= total_len:
        index = 0
    word = word_list[index]
    index += 1
    return word