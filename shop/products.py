# products.py

products = [
    {
        "id": "prod001",
        "name": "Laptop Pro",
        "price": 1200.00,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": "prod002",
        "name": "Wireless Mouse",
        "price": 25.50,
        "category": "Accessories",
        "in_stock": True
    },
    {
        "id": "prod003",
        "name": "Mechanical Keyboard",
        "price": 99.99,
        "category": "Accessories",
        "in_stock": False
    },
    {
        "id": "prod004",
        "name": "External Hard Drive 1TB",
        "price": 75.00,
        "category": "Storage",
        "in_stock": True
    }
]

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        print("Hello my name is "+ self.name)

p1 = Person("Emil", 36)
p1.greet()