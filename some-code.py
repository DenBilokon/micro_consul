# Variant 1
print("Variant 1")

my_string = "python"
x = 0

for i in my_string:
    x = x + 1
    print(my_string[0:x])

for i in my_string:
    x = x - 1
    print(my_string[0:x])

# Variant 2
print("Variant 2")

lst = [word for word in ]


def remov_nb(n):
    sum_lst = sum(list(range(1, n+1)))
    out = []
    i = 1
    j = n
    while i < j:
        product = i*j
        diff = sum_lst-i-j
        if product == diff:
            out.append((i, j))
            out.append((j, i))
            i += 1
        elif product > diff:
            j -= 1
        else:
            i += 1
    return out