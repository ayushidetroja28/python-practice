import numpy as np
from numpy import random

arr = np.array(range(10,51))
# print(arr.ndim)
# print(arr.dtype)
# print(arr.size)

A = np.array([[2, 3], [4, 5]])
B = np.array([[1, 2], [3, 4]])

# print(A * B)

data = np.arange(1, 26)

matrix5 = data.reshape((5,5))
# print(matrix5[:])
# print(matrix5[2,:])
# print(matrix5[:, -1])
# print(matrix5[0:2, 3:5])  //a 2×2 submatrix from the top-right corner.

# Select only elements greater than 10 and return them.
arr2 = np.array([5, 12, 7, 20, 3, 18])
newarr = arr2 > 10
# print(arr2[newarr]) 

v = np.array([1, 2, 3])
M = np.ones((3, 3))
# Add v to each row of M:

result = M + v
# print(result)
# =============================
x = np.random.rand(4,4)
# print(x)

x_min = x.min()
x_max = x.max()

x_norm = (x - x_min) / (x_max - x_min)
# print(x_norm)


# =============================

arr4 = np.random.randn(100)
# print(arr4)
mean_val = arr4.mean()
median_val = np.median(arr4)
standard_deviation_val = arr4.std()
variance_val = arr4.var()

# print(mean_val)
# print(median_val)
# print(standard_deviation_val)
# print(variance_val)



# =================================

arr6 = random.randint(10, 51, size=(5, 5))
# print(arr6)
# 2️⃣ Random choice of 5 numbers from 1 to 100 (without replacement)
choices = np.random.choice(np.arange(1, 101), size=5, replace=False)
# print(choices)


a = np.arange(6)
b = np.arange(6, 12)
x = a.reshape((2,3))
y = b.reshape((2,3))
print(x)
print(y)

z = np.vstack((x,y))
print(z)

