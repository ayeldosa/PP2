class Reverse:
    def __init__(self, text):
        self.text = text
        self.position = len(text)  

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.position == 0:  
            raise StopIteration  
        self.position -= 1       
        return self.text[self.position]  

word = input()
for letter in Reverse(word):
    print(letter, end="")