import string
from typing import *
import random
from tqdm import tqdm

# Required packets is tqdm for the loading bar



class Fuzzer:
    '''
    Usage:
    import fuzzing
    fuzzer = fuzzing.Fuzzer()
    fuzzer.add_mutator(custom_mutator_method)
    inputs = [...] or "test_input"
    fuzzer.run(inputs, test_function)
    fuzzer.print_candidates()
    '''
    SPECIAL_CHANCE = 0.1 # The chance that after it was determined that a string should be mutated a special character mutation happens
    
    def __init__(self):
        # Defining character lists
        self._lowercase = list(string.ascii_lowercase)
        self._special =  list(".*#")
        self._uppercase = list(string.ascii_uppercase)
        self._numbers = list(string.digits)
        self._leet = {"a": ["4","@"], "A": ["4","@"], "i": ["1","!"], "I": ["1","!"], "t": ["7"], "T": ["7"], "o": ["0"], "O": ["0"], "s": ["5"], "S": ["5"],"V": ["\\/"],
                      "v": ["\\/"], "e": ["3"], "E": ["3"], "g": ["9"], "G": ["9"], "C": ["(","K"], "c": ["(","k"], "K": ["C"], "k": ["c"]}
        self._non_latin = {"c": ["¢", "©", "Ç", "ç"], "S": ["$"], "E": ["€", "È", "É", "Ê", "Ë"], "C": ["©","Ç", "ç"], "a": ["ª"], "R": ["®"], "A": ["À", "Á", "Â", "Ã", "Ä", "Å"],
                            "I": ["Ì", "Í", "Î", "Ï"], "D": ["Ð"], "N": ["Ñ"], "O": ["Ò", "Ó", "Ô", "Õ", "Ö", "Ø", "ð","ø"], "X": ["×"], "x": ["×"], "U": ["Ù", "Ú", "Û", "Ü"],
                            "Y": ["Ý"], "P": ["Þ"], "p": ["Þ"], "B": ["ß"], "a": ["à", "á", "â", "ã", "ä", "å"], "e": ["è", "é", "ê", "ë"], "i": ["ì","í","î","ï"],
                            "o": ["ð", "ò","ó","ô","õ","ö","ø"], "n": ["ñ"], "u": ["ù","ú","û","ü"], "y": ["ý","ÿ"], "H": ["Ĥ", "Ħ"], "h": ["ĥ"], "k": ["ķ"]}

        # Defining mutator list for use in mutation
        self._mutators = [self._leet_replace, self._lowercase_replace, self._uppercase_replace, self._special_replace, self._non_latin_replace]

        # List of candidates
        self._candidates = []

        # Default error limit
        self._error_limit = 100



    def run(self, inputs, func: Callable, mutation_chance=0.5, trials=100,  mutation_depth: int=10, with_ret_val=False):
        '''
        Function for starting the fuzzing
        - inputs can either be a single value that will be mutated or a list
        - func is the function that you want to test. It should raise an exception if the input is not allowed to pass
        or return True if with_ret_val is set 
        - mutation_chance is the chance that a specific string is mutated once
        - trials is the number of tries the fuzzer should start with the original inputs
        - mutation_depth is the times it should try to mutate the list of inputs
        - with_ret_val must be set if the test function is validated with true and false
        '''
        if not isinstance(inputs, list):
            inputs = [inputs]
        original_input = inputs
        for _ in tqdm(range(trials),desc="Loading ...", ascii=False, ncols=trials):
            inputs = original_input
            for _ in range(mutation_depth):
                for input in inputs:
                    output = self._run(input, func, with_ret_val)
                    if output:
                        self._candidates.append(input)
                inputs = self._mutate_all(inputs, mutation_chance)
    


    def add_mutator(self, mutator: Callable):
        '''
        Adds a mutator to the list of mutators that will be used for mutating a string
        - mutator is the mutator method
        Layout of the mutator function:
        - input: Takes as input a string that should be mutated
        - returns: Returns the mutated string
        How the string is mutated is left to the mutator method
        '''
        self._mutators.append(mutator)

    
    def print_candidates(self):
        '''
        Prints the found candidated after fuzzing
        '''
        print(set(self._candidates))

    def set_error_limit(self, error_limit):
        '''
        Sets the limit for non successful tries of mutating a string
        - error_limit is the limit that should be set
        '''
        self.error_limit = self._error_limit
        

    
    def _run(self, input, func: Callable, with_ret_val=False) -> bool:
        '''
        Internal run function. Should not be used on the outside.
        It runs the test function and returns true if it found a potential fuzz
        '''
        try:
            return_value = func(input)
            return (with_ret_val and return_value)
        except:
            return True


    
    def _mutate_all(self, inputs: list, mutation_chance):
        '''
        This function will mutate a given list with each element having a change of mutation_chance
        - inputs is a list of strings that will be mutated
        - mutation_chance is the change of mutating any given string. Default: 0.5
        '''
        ret = []
        for input in inputs:
            if random.random() < mutation_chance:
                input = self._mutate(input)
            ret.append(input)
        return ret
            

   
    def _mutate(self, input, special_mutation_chance=SPECIAL_CHANCE) -> str:
        '''
        Mutates a single string 100% of the time with a random mutator
        - input is the string that will be mutated
        - special_mutation_chance is the chance that a special character mutation happens after
        it has been chosen for mutation already. This is due to that a special character
        replacment is a strong replacment altering the word in a "big" way.
        The total probablity of a special character mutation is given by special_mutation_chance*mutation_chance
        '''
        while True:
            mutator = random.choice(self._mutators)
            if mutator == self._special_replace and random.random() < special_mutation_chance:
                return mutator(input)
            if mutator != self._special_replace:
                return mutator(input)
    
    # Start of Mutators

    def _leet_replace(self, mutatable: str) -> str:
        '''
        Replaces a character in a string with a leet like replacement
        - mutatable is the string that will be mutated
        '''
        mutatable = list(mutatable)
        for _ in range(self._error_limit):
            index, letter = self._indexed_choice(mutatable)
            if letter in self._leet:
                mutatable[index] = random.choice(self._leet[letter])
                mutatable = "".join(mutatable)
                return mutatable
        mutatable = "".join(mutatable)
        return mutatable
    

    def _uppercase_replace(self, mutatable: str) -> str:
        '''
        Replaces a character in a string with a uppercase version of it if it is lowercase
        - mutatable is the string that will be mutated
        '''
        mutatable = list(mutatable)
        for _ in range(self._error_limit):
            index, letter = self._indexed_choice(mutatable)
            if letter in self._lowercase:
                index_of_replacement = self._lowercase.index(letter)
                mutatable[index] = self._uppercase[index_of_replacement]
                mutatable = "".join(mutatable)
                return mutatable
        mutatable = "".join(mutatable)
        return mutatable

    
    def _lowercase_replace(self, mutatable: str) -> str:
        '''
        Replaces a character in a string with a lowercase version of it if it is uppercase
        - mutatable is the string that will be mutated
        '''
        mutatable = list(mutatable)
        for _ in range(self._error_limit):
            index, letter = self._indexed_choice(mutatable)
            if letter in self._uppercase:
                index_of_replacement = self._uppercase.index(letter)
                mutatable[index] = self._lowercase[index_of_replacement]
                mutatable = "".join(mutatable)
                return mutatable
        mutatable = "".join(mutatable)
        return mutatable
        
    def _special_replace(self, mutatable: str): 
        '''
        Replaces a character in a string with a special character
        - mutatable is the string that will be mutated
        '''
        mutatable = list(mutatable)
        index, letter = self._indexed_choice(mutatable)
        mutatable[index] = random.choice(self._special)
        mutatable = "".join(mutatable)
        return mutatable

    
    def _non_latin_replace(self, mutatable: str):
        '''
        Replaces a character in a string with a similar non latin character
        - mutatable is the string that will be mutated
        '''
        self._error_limit=self._error_limit
        mutatable = list(mutatable)
        for _ in range(self._error_limit):
            index, letter = self._indexed_choice(mutatable)
            if letter in self._non_latin:
                mutatable[index] = random.choice(self._non_latin[letter])
                mutatable = "".join(mutatable)
                return mutatable
        mutatable = "".join(mutatable)
        return mutatable


    
    def _indexed_choice(self, mutatable: str):
        '''
        Returns a random letter, index pair for the given string. The index is the
        index of the letter that was chosen
        - mutatable is the string that should be mutated
        '''
        index, letter = random.choice(list(enumerate(mutatable)))
        return index, letter


