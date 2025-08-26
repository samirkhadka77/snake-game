pa = float(input("Enter purchased amount:"))
d = 0
if pa >=1000:
    d = pa * 0.05
else:
    d = pa * 0.03
    print("Discount = ",d)

