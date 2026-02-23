from models.student import Student
from utils.formatter import print_student
from pathlib import Path

def main():
    s1 = Student(1, "Ayushi", 55)
    s2 = Student(1, "Rutuja", 12)
    s3 = Student(1, "Swaroop", 20)

    students = [s1, s2, s3]

    for stu in students:
        print_student(stu)

# main()

try:
    with open('demo.txt',"a") as f:
        print(f.read(2))
except:
     pass
    # print("Error ")
finally:
     pass
    # print("try except is finished!")

with open('demo.json') as f:
        print(f.read())