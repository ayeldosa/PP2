class Animal:
    def speak(self):
        print("Some sound")

class Cat(Animal):
    def speak(self):
        print("Meow")

c = Cat()
c.speak()

class Cat(Animal):
    def speak(self):
        super().speak()
        print("Meow")

isinstance(c, Cat)      # True
isinstance(c, Animal)  # True

issubclass(Cat, Animal)  # True

