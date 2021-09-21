# # importing the threading module
# import threading

# X1 = []

# def print_cube(num):
#     # x.append(3)
#     return 2

# def print_square(num):
#     # x.append(2)
#     return 3
  
# if __name__ == "__main__":
#     # creating thread
#     t1 = threading.Thread(target=print_square, args=(10,))
#     t2 = threading.Thread(target=print_cube, args=(10,))
  
#     # starting thread 1
#     t1.start()
#     # starting thread 2
#     t2.start()

#     # print(a , b)
#     # wait until thread 1 is completely executed
#     a = t1.join()
#     # wait until thread 2 is completely executed
#     b = t2.join()
    

#     # both threads completely executed
#     print("Done!")
#     print(a , b)

# def remove_specific_row_from_csv(file, args):
#     df = pd.read_csv(file)
#     res = df[['']]
#     df = df.drop(index=args)
#     df.to_csv(file, index=False)

import pandas as pd
data = pd.read_csv("./result/net_result.csv")
print(data)