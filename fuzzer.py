import string
from typing import *
import random
from tqdm import tqdm

# Required packets is tqdm for the loading bar


'''
Usage:
import fuzzing
fuzzer = fuzzing.Fuzzer()
fuzzer.add_mutator(custom_mutator_method)
inputs = [...] or "test_input"
fuzzer.run(inputs, test_function)
fuzzer.print_candidates()
'''
class Fuzzer:
    
    RUNTIME = 100 # Time the different mutators should try to mutate a string
    SPECIAL_CHANCE = 0.1 # The chance that after it was determined that a string should be mutated a special character mutation happens


    '''
    __init__ takes no input
    Below all the different lists of characters are defined
    _mutators is a list of mutator functions used for mutation
    _candidates is a list of candidates. Can be printed after fuzzing
    '''
    def __init__(self):
        # Defining character lists
        self._lowercase = list(string.ascii_lowercase)
        self._special =  list(".*#")
        self._uppercase = list(string.ascii_uppercase)
        self._numbers = list(string.digits)
        self._leet = {"a": "4", "A": "4", "i": "1", "I": "1", "t": "7", "T": "7", "o": "0", "O": "0", "s": "5", "S": "5", "i": "!",
                      "I": "!", "V": "\\/", "v": "\\/", "e": "3", "E": "3", "g": "9", "G": "9", "C": "(", "c": "(", "a": "@", "A": "@", "c": "k",
                      "C": "K", "K": "C", "k": "c"}

        # Defining mutator list for use in mutation
        self._mutators = [self._leet_replace, self._lowercase_replace, self._uppercase_replace, self._special_replace]

        #List of candidates
        self._candidates = []


    '''
    Function for starting the fuzzing
    - inputs can either be a single value that will be mutated or a list
    - func is the function that you want to test. It should raise an exception if the input is not allowed to pass
      or return True if with_ret_val is set 
    - mutation_percentage is the chance that a specific string is mutated once
    - run_time is the number of trials the programm should try to mutate the given inputs
    - with_ret_val must be set if the test function is validated with true and false
    '''
    def run(self, inputs, func: Callable, mutation_percentage=0.5, runtime=100, with_ret_val=False):
        if not isinstance(inputs, list):
            inputs = [inputs]
        for timer in tqdm(range(runtime),desc="Loading ...", ascii=False, ncols=runtime):
            for input in inputs:
                output = self._run(input, func, with_ret_val)
                if output:
                    self._candidates.append(input)
            inputs = self._mutate_all(inputs, mutation_percentage)
    

    '''
    Adds a mutator to the list of mutators that will be used for mutating a string
    - mutator is the mutator method
    Layout of the mutator function:
    - input: Takes as input a string that should be mutated
    - returns: Returns the mutated string
    How the string is mutated is left to the mutator
    '''
    def add_mutator(self, mutator: Callable):
        self._mutators.append(mutator)

    '''
    Prints the found candidated after fuzzing
    '''
    def print_candidates(self):
        print(set(self._candidates))


    '''
    Internal run function. Should not be used on the outside.
    It runs the test function and returns true if it found a potential fuzz
    '''
    def _run(self, input, func: Callable, with_ret_val=False) -> bool:
        try:
            return_value = func(input)
            return (with_ret_val and return_value)
        except:
            return True


    '''
    This function will mutate a given list with each element having a change of mutation_percentage
    - inputs is a list of strings that will be mutated
    - mutation_percentage is the change of mutating any given string. Default: 0.5
    '''
    def _mutate_all(self, inputs: list, mutation_percentage):
        ret = []
        for input in inputs:
            if random.random() < mutation_percentage:
                input = self._mutate(input)
            ret.append(input)
        return ret
            

    '''
    Mutates a single string 100% of the time with a random mutator
    - input is the string that will be mutated
    - special_mutation_chance is the chance that a special character mutation happens after
      it has been chosen for mutation already. This is due to that a special character
      replacment is a strong replacment altering the word in a "big" way.
    '''
    def _mutate(self, input, special_mutation_chance=SPECIAL_CHANCE) -> str:
        while True:
            mutator = random.choice(self._mutators)
            if mutator == self._special_replace and random.random() < special_mutation_chance:
                return mutator(input)
            if mutator != self._special_replace:
                return mutator(input)
    
    # Start of Mutators

    '''
    Replaces a character in a string with a leet like replacement
    - mutatable is the string that will be mutated
    - runtime is the amount it should be tried to find a leet replaceable character
    '''
    def _leet_replace(self, mutatable: str, runtime=RUNTIME) -> str:
        mutatable = list(mutatable)
        for _ in range(runtime):
            index, letter = self._indexed_choice(mutatable)
            if letter in self._leet:
                mutatable[index] = self._leet[letter]
                mutatable = "".join(mutatable)
                return mutatable
        mutatable = "".join(mutatable)
        return mutatable
    

    '''
    Replaces a character in a string with a uppercase version of it if it is lowercase
    - mutatable is the string that will be mutated
    - runtime is the amount it should be tried to find a leet replaceable character
    '''
    def _uppercase_replace(self, mutatable: str, runtime=RUNTIME) -> str:
        mutatable = list(mutatable)
        for _ in range(runtime):
            index, letter = self._indexed_choice(mutatable)
            if letter in self._lowercase:
                index_of_replacement = self._lowercase.index(letter)
                mutatable[index] = self._uppercase[index_of_replacement]
                mutatable = "".join(mutatable)
                return mutatable
        mutatable = "".join(mutatable)
        return mutatable

    '''
    Replaces a character in a string with a lowercase version of it if it is uppercase
    - mutatable is the string that will be mutated
    - runtime is the amount it should be tried to find a leet replaceable character
    '''
    def _lowercase_replace(self, mutatable: str, runtime=RUNTIME) -> str:
        mutatable = list(mutatable)
        for _ in range(runtime):
            index, letter = self._indexed_choice(mutatable)
            if letter in self._uppercase:
                index_of_replacement = self._uppercase.index(letter)
                mutatable[index] = self._lowercase[index_of_replacement]
                mutatable = "".join(mutatable)
                return mutatable
        mutatable = "".join(mutatable)
        return mutatable
        
    '''
    Replaces a character in a string with a special character
    - mutatable is the string that will be mutated
    - runtime is the amount it should be tried to find a leet replaceable character
    '''
    def _special_replace(self, mutatable: str): 
        mutatable = list(mutatable)
        index, letter = self._indexed_choice(mutatable)
        mutatable[index] = random.choice(self._special)
        mutatable = "".join(mutatable)
        return mutatable


    '''
    Returns a random letter, index pair for the given string. The index is the
    index of the letter that was chosen
    - mutatable is the string that should be mutated
    '''
    def _indexed_choice(self, mutatable: str):
        index, letter = random.choice(list(enumerate(mutatable)))
        return index, letter


