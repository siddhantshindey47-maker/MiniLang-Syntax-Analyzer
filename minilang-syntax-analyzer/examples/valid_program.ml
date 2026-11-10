// MiniLang Valid Program Example
// This demonstrates all supported language features

// Variable declarations with types
int x = 10;
float price = 25.5;
bool isActive = true;

// Simple assignment
x = x + 5;

// Arithmetic with correct precedence
int result = (x + 20) * 2 - 5;
print(result);

// If-else statement
if (x > 10) {      print(x);
    }
} else {
    print("x is 10 or less");
}

// While loop
int count = 0;
while (count < 5) {
    print(count);
    count = count + 1;
}

// Logical operators
bool check = x > 5 && price < 100.0 || !isActive;

// Complex expressions
int complex = (x + 10) * (price - 5) / 2 % 3;

// Print statements
print("Program completed!");
print(complex);

    print("x is greater than 10");
    
    // Nested if
    if (x > 20) {
  