class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    def __init__(self, name, grade):
        super().__init__(name)   # вызов родительского __init__
        self.grade = grade

s = Student("Dias", 11)
print(s.name)
print(s.grade)
