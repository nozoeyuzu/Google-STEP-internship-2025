def find_anagrams(random_word, dictionary):
    sorted_word = ''.join(sorted(random_word))

    new_dictionary = []
    for word in dictionary:
        new_dictionary.append((''.join(sorted(word)), word))
    new_dictionary.sort(key=lambda x: x[0])

    anagram = binary_search(new_dictionary, sorted_word)
    print(anagram)
    return anagram

def binary_search(words, target):
    first = 0
    last = len(words) - 1
    
    while first <= last:
        mid = (first + last)//2
        if words[mid][0] == target:
            left = mid
            right = mid
            while left >= 0 and words[left][0] == target:
                left -= 1
            while right < len(words) and words[right][0] == target:
                right += 1
            return [words[i][1] for i in range(left+1, right)]
        elif words[mid][0] < target:
            first = mid + 1
        else:
            last = mid - 1 
    return []

with open('words.txt') as file:
    dictionary = [line.strip() for line in file if line.rstrip()]

random_word = input()
anagrams = find_anagrams(random_word, dictionary)

