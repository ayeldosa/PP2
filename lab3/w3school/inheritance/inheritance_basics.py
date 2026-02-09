class Animal:
    def speak(self):
        print("Animal makes a sound")

class Dog(Animal):
    def bark(self):
        print("Woof!")

d = Dog()
d.speak()  # метод родителя
d.bark()   # метод потомка

