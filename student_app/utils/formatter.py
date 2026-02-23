def print_student(student):
    print("---------------------")
    print(student.details())
    print("---------------------")
    print("Result: ", "PASS" if student.isPass() else "FAIL")