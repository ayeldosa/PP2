def my_function(name = "friend"):
  print("Hello", name)

my_function("Emil")
my_function("Tobias")
my_function()
my_function("Linus")

def my_func(person):
  print("Name:", person["name"])
  print("Age:", person["age"])

my_person = {"name": "Emil", "age": 25}
my_func(my_person)

def my_fun(a, b, /, *, c, d):
  return a + b + c + d

result = my_fun(5, 10, c = 15, d = 20)
print(result)