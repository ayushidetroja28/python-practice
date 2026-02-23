# What will be the output?
a = "10"
b = 5
# print(a * b)

fruit=["apple", "banana"]
veggy=["potato", "Tameto"]
# fruit.append("cherry")
fruit.extend(veggy)
# fruit.pop(-1)
# print(fruit)

for x in range(1,11):
    if (x) % 2 == 0:
        # print(x)
        pass


fruit.sort(reverse = True)
# print(fruit)

tuple_list = tuple(fruit)
# print(tuple_list)


student = {"s1": {"name" : "Ayushi", "age" : 36},"s2":  {"name" : "Rutuja", "age" : 39},"s3":  {"name" : "Swaroop", "age" : 22}}

for x, obj in student.items():
    if obj["age"] > 30:
        pass
        # print(obj['name'])

for i in range(1, 5):
    pass
    # print(i, end=" ")

x = 5
while x > 0:
    x -= 1
# print(x)

sum = 0
for x in range(1, 101):
    sum += x
# print(sum)

def sum_all(n):
    return (n * (n+1))/2

for x in range(1, 11):
    pass
    # print(f"7 * {x} = {7*x}")

def square(n):
    return n*n
# print(square(9))

def largest_num(list):
    if not list:
        return None
    else:
        large = list[0]
        for num in list[1:]:
            if num > large:
                large = num
        return large
    
# print(largest_num([10, 202, 55, 7, 30, 99, 1]))

def isPrime(n):
    if n <= 2:
        return True
    else:
        val = True
        for i in range(2, int(n**0.5) +1):
            if n % i == 0:
                val = False
                break
        return val       
# print(isPrime(16))

x = [i*i for i in range(4)]
pass
# print(x)

nums = [1, 2, 3, 4]
new = [n for n in nums if n % 2 == 0]
pass
# print(new)

list_com = range(1,21)
new_list = [n * n for n in list_com]
# print(new_list)

vowel_str = "ayushi"
new_vowel = [n for n in vowel_str if n in ["a", "e","i","o","u"] ]
# print(new_vowel)

        
