import json
import math
import numpy as np

# This project is made by: Mina Ihab Aziz Hanna Ibrahim, ID: 24010762

# Functions Section:
def suggest_guess(guessesEntropy):
    max = -1
    suggestedGuess = None
    for guess, entropy in guessesEntropy.items():
        if entropy > max:
            suggestedGuess = guess
            max = entropy

    return suggestedGuess

def get_pattern(guess, target):

    pattern = ["", "", "", "", ""]
    letters = {}

    for i in range(5):
        if guess[i] not in letters.keys():
            letters[guess[i]] = 0
        if guess[i] == target[i]:
            pattern[i] = "g"
            letters[guess[i]] += 1

    for i in range(5):
        if pattern[i] == "":
            if str.find(target, guess[i]) == -1:
                pattern[i] = "r"

    for i in range(5):
        if pattern[i] == "":
            letterCount = str.count(target, guess[i])
            if letters[guess[i]] < letterCount:
                pattern[i] = "y"
                letters[guess[i]] += 1
            else:
                pattern[i] = "r"

    patternStr = ""
    for i in range(5):
        patternStr += pattern[i]

    return patternStr

def pattern_str_to_code(patternStr):
    code = [0,0,0,0,0]

    for i in range(len(patternStr)):
        if patternStr[i] == "g":
            code[i] = 2
        elif patternStr[i] == "y":
            code[i] = 1
        else:
            code[i] = 0

    patternCode = 0
    for i in range(len(code)):
        patternCode += code[i]*(3**i)

    return patternCode

def pattern_code_to_str(code):
    patternCode = [0,0,0,0,0]
    patternLetters = ["", "", "", "", ""]
    index = 0
    while code > 0 and index < 5:
        if code % 3 != 0:
            patternCode[index] = code % 3

        code //= 3
        index += 1

    pattern = ""
    for index, num in enumerate(patternCode):
        if num == 0:
            patternLetters[index] = "r"
        elif num == 1:
            patternLetters[index] = "y"
        else:
            patternLetters[index] = "g"

        pattern += patternLetters[index]

    return pattern

def add_to_pattern_matrix(guess, target, row, col, patternMatrix):

    pattern = get_pattern(guess, target)
    patternCode = pattern_str_to_code(pattern)
    patternMatrix[row][col] = patternCode

def compute_pattern_matrix(patternMatrix, guessWords, targetWords):

    for row in range(len(patternMatrix)):
        for col in range(len(patternMatrix[row])):
            add_to_pattern_matrix(guessWords[row], targetWords[col], row, col, patternMatrix)

            if row % 100 == 0 and col % 100 == 0:
                print("Computing Pattern...")
                print("Guess Words: ", row, "/", len(guessWords), " - Target Words: ", col, "/", len(targetWords))

def filter_target(patternMatrix, patternCode, remainingTargetInidicies, guess, guessWords):

    targetIndicies = []
    guessIndex = guessWords.index(guess)

    for targetIndex in remainingTargetInidicies:
        if patternMatrix[guessIndex][targetIndex] == patternCode:
            targetIndicies.append(targetIndex)

    return targetIndicies

def pattern_code_frequency_counter(patternMatrix, remainingTargetInidicies, guessIndex):

    patternsCodesFrequency = {}

    for targetIndex in remainingTargetInidicies:
        patternCode = patternMatrix[guessIndex][targetIndex]
        if patternCode not in patternsCodesFrequency:
            patternsCodesFrequency[patternCode] = 1
        else:
            patternsCodesFrequency[patternCode] += 1

    return patternsCodesFrequency

def pattern_code_probability_calculator(remainingTargetInidicies, patternFrequencies):

    patternProbability = {}

    for patternCode, frequency in patternFrequencies.items():
        patternProbability[patternCode] = frequency / len(remainingTargetInidicies)

    return patternProbability

def pattern_code_surprise_calculator(patternProbability):
    patternSurprise = {}

    for patternCode, probability in patternProbability.items():
        patternSurprise[patternCode] = -math.log2(probability)

    return patternSurprise

def guesses_entropy_calculator(patternSurprise, patternProbability):

    entropy = 0
    for patternCode in patternSurprise.keys():
        entropy += (patternSurprise[patternCode]*patternProbability[patternCode])

    return entropy

def guesses_entropy(patternMatrix, remainingTargetIndicies, guessWords):

    guessesEntropy = {}

    for guessIndex, guess in enumerate(guessWords):
        patternFrequency = pattern_code_frequency_counter(patternMatrix, remainingTargetIndicies, guessIndex)
        patternProbability = pattern_code_probability_calculator(remainingTargetIndicies, patternFrequency)
        patternSurprise = pattern_code_surprise_calculator(patternProbability)
        guessEntropy = guesses_entropy_calculator(patternSurprise, patternProbability)

        guessesEntropy[guess] = guessEntropy

    return guessesEntropy

# Code:
try:
    dictionaryFile = open("dictionary_5_letter.json", "r")
    targetsFile = open("targets_5_letter.json", "r")
except FileNotFoundError:
    print("System: There is an error in finding the files.")
    exit()

guessWords = json.load(dictionaryFile)
targetsWords = json.load(targetsFile)

try:
    patternMatrix = np.load("pattern_matrix.npy")
except:
    patternMatrix = np.zeros((len(guessWords),len(targetsWords)), dtype=int)
    compute_pattern_matrix(patternMatrix, guessWords, targetsWords)
    np.save("pattern_matrix.npy", patternMatrix)

remainingPossibleAnswers = np.arange(len(targetsWords))

uncertainty = math.log2(len(remainingPossibleAnswers))
print("Prior entropy H(W) =", round(uncertainty, 3), "bits")

start = False

while len(remainingPossibleAnswers) > 1:

    if not start:
        print("Enter guess word (Suggestion: Start with 'soare'):")
        start = True
    else:
        print("Enter guess word:")

    guessInput = input().lower()

    if guessInput not in guessWords:
        print("System: You must enter a guess word in the dictionary file.")
        continue

    print("Enter pattern (r - wrong, y - letter exist, g - letter correct):")
    guessPattern = input().lower()

    print()

    wrongPatternFlag = False

    for letter in guessPattern:
        if letter != "r" and letter != "y" and letter != "g":
            print("System: Pattern must contain information letters (g - y - r).")
            wrongPatternFlag = True
            break

    if wrongPatternFlag:
        continue

    if len(guessPattern) != 5:
        print("System: Pattern must be with the same length of the word (5 letters).")
        continue

    guessedCorrectFlag = False
    if guessPattern == "ggggg":
        guessedCorrectFlag = True
        break

    patternCode = pattern_str_to_code(guessPattern)

    remainingPossibleAnswers = filter_target(patternMatrix, patternCode, remainingPossibleAnswers, guessInput, guessWords)

    if len(remainingPossibleAnswers) == 0:
        print("System: There is no possible answer.")
        exit()

    if (len(remainingPossibleAnswers) == 1):
        break

    uncertainty = math.log2(len(remainingPossibleAnswers))
    print("Prior entropy H(W) =",round(uncertainty, 3), "bits")
    guessesEntropy = guesses_entropy(patternMatrix, remainingPossibleAnswers, guessWords)
    suggestedGuess = suggest_guess(guessesEntropy)

    print("Best-Guess entropy H(Y) =",round(guessesEntropy[suggestedGuess], 3), "bits")
    print("Expected posterior entropy H(W|Y) =",round(uncertainty - guessesEntropy[suggestedGuess], 3), "bits")
    print("Information gain I(W;Y) =",round(guessesEntropy[suggestedGuess], 3), "bits")
    print()
    print("BEST=" + suggestedGuess)
    print()

if guessedCorrectFlag:
    print("BEST=" + guessInput)
else:
    print("BEST=" + targetsWords[remainingPossibleAnswers[0]])
