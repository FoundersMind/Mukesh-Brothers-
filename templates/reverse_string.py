def reverse(arr):
    x=[]
    for i in range(len(arr)):
        x+=arr[i].pop()
    return x
def main():
    x=[]
    arr=[3,4,5,6,7]
    reverse(arr)
    print(x)