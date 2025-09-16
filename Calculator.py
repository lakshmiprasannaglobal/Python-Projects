# calculator.py

print("=== Simple Calculator ===")

while True:
    num1 = float(input("Enter first number: "))
    op = input("Enter operator (+, -, *, /): ")
    num2 = float(input("Enter second number: "))

    if op == "+":
        print("Result:", num1 + num2)
    elif op == "-":
        print("Result:", num1 - num2)
    elif op == "*":
        print("Result:", num1 * num2)
    elif op == "/":
        if num2 != 0:
            print("Result:", num1 / num2)
        else:
            print("Error: Division by zero")
    else:
        print("Invalid operator!")

    # option to quit
    choice = input("Do you want to continue? (y/n): ")
    if choice.lower() != "y":
        break
