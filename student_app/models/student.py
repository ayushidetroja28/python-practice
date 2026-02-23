class Student:
    def __init__(self,id, name, marks):
        self.id = id
        self.name = name
        self.marks = marks

    def isPass(self):
        return self.marks >= 40
    
    def details(self):
        return f"ID: {self.id}, Name: {self.name}, Marks: {self.marks}"