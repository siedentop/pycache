def func_a(x, y):
    return x+y

def func_b(x,    y):
    return x+y


if __name__ == '__main__':
    print(hash(func_a.__code__.co_code))
    print(hash(func_b.__code__.co_code))
