from collections import Counter

def read_file(file):
    words = []
    with open(file, 'r', encoding='utf-8') as flie:
        for line in flie:
            line = line.rstrip()
            words.append(line)
        return words

def find_anagrams(random_word, dictionary):
    input_counter = Counter(random_word)
    result = []
    for word in dictionary:
        word_counter = Counter(word)
        if all(input_counter[ch] >= cnt for ch, cnt in word_counter.items()):
            result.append(word)
    return result

def score_of_anagrams(word):
    score = [1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4]
    total_score = 0
    for char in word:
        total_score += score[ord(char) - ord('a')]
    return total_score

def search_max_score(input_word, dictionary, output_file):
    data_file = read_file(input_word)
    dictionary_file = read_file(dictionary)
    
    with open("output.txt", "w") as output_file:
        for letters in data_file:
            candidates = find_anagrams(letters, dictionary_file)
            if candidates:
                max_score = max(candidates, key=score_of_anagrams)
            else:
                max_score = ""
            output_file.write(f"{max_score}\n")

if __name__ == "__main__":
    search_max_score(
        'large.txt',
        'words.txt',
        'output.txt'
    )
