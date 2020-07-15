import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import re


# # cumsum prototype
# # A = np.array([[1, 3, 4, 5, 6, 100], [2, 3, 10, 1, 10, 100], [10, 1, 1, 1, 1, 100], [1, 10, 3, 3, 3, 100]])
# # print(A)
# # A[:, :-1] = np.cumsum(A[:, :-1], axis=0)
# # print(A)

# # Curve fitting prototype
# data1 = np.array([(1, 1), (2, 4), (3, 1), (9, 3)])
# data2 = np.array([(0.5, 10), (1.8, 3), (2, 3), (8, 4)])
# data3 = np.array([(2, 2), (3, 5), (6, 1), (10, 3)])
#
# x1 = data1[:, 0]
# y1 = data1[:, 1]
#
# x2 = data2[:, 0]
# y2 = data2[:, 1]
#
# x3 = data3[:, 0]
# y3 = data3[:, 1]
#
# z1 = np.polyfit(x1, y1, 3)
# f1 = np.poly1d(z1)
# z2 = np.polyfit(x2, y2, 3)
# f2 = np.poly1d(z2)
# z3 = np.polyfit(x3, y3, 3)
# f3 = np.poly1d(z3)
#
# f = (f1 + f2 + f3) / 3
#
# xplot = np.linspace(0, 11, 50)
# yplot = f(xplot)
# yplot1 = f1(xplot)
# yplot2 = f2(xplot)
# yplot3 = f3(xplot)
# plt.plot(xplot, yplot1, 'x', label='f1')
# plt.plot(xplot, yplot2, 'o', label='f2')
# plt.plot(xplot, yplot3, '*', label='f3')
# plt.plot(xplot, yplot, label='F')
# plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
#
# plt.show()

# src1 = 'r1'
# r_list = ['r' + str(k) for k in range(16)]
# print(r_list)
# print(src1 in r_list)

mat1 = np.full([2, 12], 15)
mat2 = np.full([2, 12], 10)
mat1[0, :] = [11 - i for i in range(12)]
mat2[0, :] = [i for i in range(12, 24)]
mat3 = np.hstack((mat1, mat2))
print(mat3)
mat3_s = mat3[:, mat3[0, :].argsort()]
mat3_s[:, 12:24] += np.array([[15], [1]])
print(mat3_s)



