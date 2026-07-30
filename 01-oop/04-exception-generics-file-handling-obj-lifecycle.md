---
title: "Exceptions, Generics, Files & Object Lifecycle"
summary: "Exception handling with try/catch/finally and custom exceptions, generics with bounded types and wildcards, file I/O with try-with-resources, and the Java object lifecycle from creation through garbage collection."
essential: true
---

# Exceptions, Generics, Files & Object Lifecycle

## Exception Handling in Java

Exception handling is a mechanism in Java that helps manage runtime errors and maintain the normal flow of a program. An exception is an unwanted or unexpected event that occurs during program execution, disrupting the normal flow.

Java provides a robust exception-handling framework to catch and handle such situations efficiently.

Consider the following example (If you run the program, it will crash without exception handling):

```java
// expects-exception: shows what an unhandled ArithmeticException looks like
import java.util.*;

// Main class
class Main {
    public static void main(String[] args) {
        int num1 = 10, num2 = 0;

        // This will cause ArithmeticException (division by zero)
        int result = num1 / num2; // Program crashes

        System.out.println("Result: " + result);
    }
}
```

The program crashes, and the remaining code (if any) won't execute.

### Importance of Exception Handling

Exception handling is essential for several reasons:

- **Prevents crashes:** Ensures that a single error doesn't stop the entire program.
- **Improves debugging:** Helps in identifying and resolving errors quickly.
- **Encapsulates error handling:** Separates normal code from error-handling code.
- **Ensures proper resource management:** Prevents memory leaks by ensuring files and connections are properly closed.

Consider the following example (with Exception Handling):

```java
import java.util.*;

// Main class
class Main {
    public static void main(String[] args) {
        int num1 = 10, num2 = 0;

        // Exception handling
        try {
            int result = num1 / num2; // Risky code
            System.out.println("Result: " + result);
        }
        catch (ArithmeticException e) {
            System.out.println("Error: Division by zero is not allowed!");
        }

        // Remaining code
        System.out.println("Program continues...");
    }
}
```

**Output:**

```text
ERROR!
Error: Division by zero is not allowed!
Program continues...
```

The program does not crash and continues execution.

### Mechanism to handle Exception (Try-Catch Block)

Java provides the try-catch mechanism to handle exceptions.

- **try block:** Contains the code that may throw an exception.
- **catch block:** Handles the exception if it occurs.

Syntax:

```java
class Main {
    public static void main(String[] args) {
        // Generic try-catch syntax, shown here with a concrete exception
        try {
            // Code that might cause an exception
            int result = 10 / 0;
        }
        catch (ArithmeticException e) { // ExceptionType -> concrete example
            // Code to handle the exception
            System.out.println("Caught: " + e);
        }
    }
}
```

Consider the following example:

```java
import java.util.*;

class Main {
    public static void main(String[] args) {
        // Try-Catch Block for Exception Handling
        try {
            int[] arr = {1, 2, 3};
            System.out.println(arr[5]); // ArrayIndexOutOfBoundsException
            int result = 10 / 0; // ArithmeticException
        }
        // Catch block to handle ArrayIndexOutOfBoundsException
        catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Error: Array index out of bounds!");
        }
        // Catch block to handle ArithmeticException
        catch (ArithmeticException e) {
            System.out.println("Error: Division by zero is not allowed!");
        }

        // Remaining code
        System.out.println("Program continues...");
    }
}
```

**Output:**

```text
ERROR!
Error: Array index out of bounds!
Program continues...
```

The first exception that occurs is caught, and the program continues.

**Important**

Multiple catch blocks (with each catch block handling different exceptions) can be added as shown in the above example. However, Java does not allow multiple catch blocks of the same exception type within a try-catch block. Try-catch blocks can be nested.

### finally Block (closing Resources)

The finally block is always executed, whether an exception occurs or not. It is used to close resources such as files, database connections, or network sockets. However, it is not necessary to add the finally block in the try-catch ladder.

Consider the following example:

```java
import java.util.*;

// Main class
class Main {
    public static void main(String[] args) {

        // Try-catch ladder
        try {
            int result = 10 / 2;
            System.out.println("Result: " + result);
        }
        catch (Exception e) {
            System.out.println("An error occurred.");
        }
        // finally block
        finally {
            System.out.println("Finally block executed.");
        }

        System.out.println("Program continues...");
    }
}
```

**Output:**

```text
Result: 5
Finally block executed.
Program continues...
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** The finally block always executes, no matter what.

</div>

### throw and throws Keywords

Java provides two important keywords - throw and throws - for handling exceptions effectively. While they might sound similar, they serve different purposes in exception handling.

**1. throw - Manually Throwing an Exception**

The throw keyword is used inside a method or block to explicitly throw an exception.

It is typically used when we want to indicate that an error has occurred due to invalid input or some exceptional condition.

The throw statement is followed by an instance of an exception.

Syntax:

```java
class Main {
    public static void main(String[] args) {
        // Generic throw syntax, shown here with a concrete exception
        try {
            throw new RuntimeException("Error Message"); // ExceptionType -> concrete example
        }
        catch (RuntimeException e) {
            System.out.println("Caught: " + e.getMessage());
        }
    }
}
```

Note that the ExceptionType must be a subclass of Throwable (like ArithmeticException, NullPointerException, or a user-defined exception).

Let's consider an example where we prevent a person from voting if their age is below 18:

```java
// expects-exception: a checked exception thrown with no try-catch — the program terminates abruptly
import java.util.*;

// Main class
class Main {

    // Method to Check Age
    public static void checkAge(int age) throws Exception {
        if (age < 18) {
            // Throwing an exception
            throw new Exception("Not eligible to vote.");
        }
        else {
            System.out.println("Eligible to vote.");
        }
    }

    // Main method
    public static void main(String[] args) throws Exception {
        checkAge(15); // Throws an exception
    }
}
```

Explanation:

- When checkAge(15) is called, the method detects that the age is less than 18.
- The throw keyword manually raises an Exception.
- Since there is no try-catch block to catch the exception thrown, the program terminates abruptly.

**2. throws - Declaring an Exception**

The throws keyword is used in a method signature to indicate that the method might throw an exception.

It does not handle the exception but forces the caller to handle it.

This is useful when a method relies on external resources like files, databases, or network connections.

Syntax:

```java
class Main {
    // Generic method-signature syntax, shown here with concrete types
    static String methodName() throws Exception { // returnType -> String, ExceptionType -> Exception
        // Method code that might throw an exception
        return "no exception this time";
    }

    public static void main(String[] args) throws Exception {
        System.out.println(methodName());
    }
}
```

The method does not handle the exception internally. It leaves the responsibility of handling the exception to the caller method.

Let's consider a method that performs division but might cause an ArithmeticException:

```java
import java.util.*;

// Main class
class Main {
    static void divide() throws ArithmeticException { // Declaring an exception
        int result = 10 / 0; // Risky code (division by zero)
    }

    public static void main(String[] args) {
        // Try-catch ladder
        try {
            divide(); // Calling the method that might throw an exception
        }
        // Catch block to handle ArithmeticException
        catch (ArithmeticException e) {
            System.out.println("Handled exception: " + e);
        }

        System.out.println("Program continues...");
    }
}
```

**Output:**

```text
Handled exception: java.lang.ArithmeticException: / by zero
Program continues...
```

Explanation:

- The divide() method declares that it might throw an ArithmeticException using throws keyword.
- The main() method calls divide(), so it must handle the exception using try-catch.
- When division by zero occurs, the exception is caught and handled without stopping the program.

**Key differences between throw and throws:**

| Feature | throw | throws |
| --- | --- | --- |
| Purpose | Used to explicitly throw an exception inside a method. | Used to declare that a method might throw an exception. |
| Usage | Inside a method or block. | In the method signature. |
| Exception Handling | Throws a specific exception immediately. | Does not handle exceptions; just declares them. |
| Number of Exceptions | Can throw only one exception at a time. | Can declare multiple exceptions (comma-separated). |
| Example | throw new NullPointerException("Null value found"); | void myMethod() throws IOException, SQLException {} |

### Custom Exceptions

In Java, custom exceptions (also known as user-defined exceptions) allow developers to define their own exception classes. This is useful when the built-in Java exceptions (ArithmeticException, IOException, etc.) do not fully describe the error conditions specific to an application.

By creating a custom exception, we can provide more meaningful error messages and handle specific cases more effectively.

Let's understand this with the following example:

```java
import java.util.*;

// Custom Exception class
class CustomException extends Exception {
    // Constructor
    CustomException(String message) {
        super(message);
    }
}

// Main class
class Main {
    public static void main(String[] args) {

        // try-catch ladder
        try {
            // throwing custom made exception
            throw new CustomException("This is a custom exception!");
        }
        catch (CustomException e) {
            System.out.println("Caught: " + e.getMessage());
        }

        System.out.println("Program continues...");
    }
}
```

**Output:**

```text
Caught: This is a custom exception!
Program continues...
```

It is useful when the need is to define application-specific errors.

### Real-Life Example of Exception Handling

In real-world applications, exceptions frequently occur due to external dependencies, such as file handling, database access, or network communication. Proper exception handling ensures that the program does not crash and provides a meaningful error message to the user.

Consider a requirement of a program to read the content of another file (that may not exist). In such cases, file handling exceptions must be implemented properly.

```java
import java.util.*;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

// Main class
class Main {
    public static void main(String[] args) {
        try {
            // Trying to read a file that does not exist
            File file = new File("nonexistent.txt");

            // FileNotFoundException may occur
            Scanner reader = new Scanner(file);
        }
        catch (FileNotFoundException e) {
            System.out.println("Error: File not found!");
        }

        System.out.println("Program continues...");
    }
}
```

**Output:**

```text
ERROR!
Error: File not found!
Program continues...
```

### Checked & Unchecked Exceptions

**Checked Exceptions:**

These are exceptions that the compiler forces you to handle using try-catch or declare using throws (e.g., IOException, SQLException).

Example:

```java
import java.util.*;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Scanner;

// Main class
class Main {
    public static void main(String[] args) throws IOException {
        File file = new File("test.txt");
        file.createNewFile(); // ensures the file exists so this block is self-contained

        Scanner reader = new Scanner(file); // Must handle or declare exception
        System.out.println("Scanner opened on: " + file.getName());
        reader.close();
    }
}
```

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** Must be handled using try-catch or declared using throws. Otherwise, the compiler throws an error while trying to compile the program.

</div>

**Unchecked Exceptions:**

These occur at runtime and do not require explicit handling. They are usually due to logical errors in the code (e.g., NullPointerException, ArithmeticException).

Example:

```java
// expects-exception: shows an unchecked ArithmeticException with no try-catch at all
import java.util.*;

class Main {
    public static void main(String[] args) {
        int result = 10 / 0; // ArithmeticException (unchecked and uncaught)
    }
}
```

Occurs at runtime, no compilation error.

## Generics

### Generics in Java

Generics were introduced in Java 5 to ensure type safety and code reusability. They allow defining classes, interfaces, and methods that can operate on various data types without sacrificing type safety.

**Key Benefits:**

- Prevents ClassCastException (occurs when you try to cast an object to a class that it is not an instance of, leading to a runtime error).
- Provides Strong Type Checking at Compile Time.
- Reduces Code Redundancy.

Example without Generics (before Java 5):

```java
import java.util.*;

// Main class without Generics
class Main {
    public static void main(String[] args) {
        ArrayList list = new ArrayList(); // No type safety
        list.add("Hello");
        list.add(100);  // No compile-time error

        // Type casting is required
        String str = (String) list.get(0);
        System.out.println(str);
    }
}
```

In the above code, there are following drawbacks:

- Allows different types in the same list (which is risky).
- Because of different types being added to the same list, explicit type casting is required every time any operation needs to be performed.
- No compile-time error is shown increasing the risk of ClassCastException.

Example with Generics:

```java
import java.util.*;
import java.util.ArrayList;

// Main class with Generics
class Main {
    public static void main(String[] args) {
        ArrayList<String> list = new ArrayList<>(); // Type-safe list
        list.add("Hello");
        // list.add(100);  // Compile-time error

        String str = list.get(0); // No casting required
        System.out.println(str);
    }
}
```

Using generics provide the following advantages:

- Type Safety is ensured (cannot add elements of other types)
- No explicit type casting is required for different operations.

### Advantages of using Generics

There are various advantages that comes with working with Generics. These are:

- **Type Safety:** Avoids ClassCastException (thrown to indicate that the code has attempted to cast an object to a subclass of which it is not an instance).
- **Reusability:** Write code that works with different data types.
- **Eliminates Explicit Type Casting:** No need to cast objects.

Example:

```java
import java.util.*;

// Generic Class
class GenericExample<T> { // T is a type parameter
    T obj;

    // Constructor
    GenericExample(T obj) {
        this.obj = obj;
    }

    // Method to display type T
    void displayType() {
        System.out.println("Type: " + obj.getClass().getName());
    }
}

// Main class
class Main {
    public static void main(String[] args) {
        GenericExample<Integer> intObj = new GenericExample<>(10);
        GenericExample<String> strObj = new GenericExample<>("Hello");

        intObj.displayType();  // Output: Type: java.lang.Integer
        strObj.displayType();  // Output: Type: java.lang.String
    }
}
```

**Key Points:**

- Same class works for multiple types.
- No need to write separate classes for different data types

### Generic Classes

A Generic Class works with different types without rewriting the code.

Syntax:

```java
class ClassName<T> {
    // T is a type parameter
    private T value;

    ClassName(T value) { this.value = value; }

    T get() { return value; }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        ClassName<String> holder = new ClassName<>("Generic syntax demo");
        System.out.println(holder.get());
    }
}
```

Example:

```java
import java.util.*;

// Generic Class
class Box<T> { // T is the data type
    private T value;

    public void set(T value) { this.value = value; }

    public T get() { return value; }
}

class Main {
    public static void main(String[] args) {
        Box<Integer> intBox = new Box<>();
        intBox.set(100);
        System.out.println(intBox.get()); // Output: 100

        Box<String> strBox = new Box<>();
        strBox.set("Hello Generics");
        System.out.println(strBox.get()); // Output: Hello Generics
    }
}
```

**Key Points:**

- Works for any data type.
- Code reusability.

### Generic Methods

A generic method allows different data types within a single method.

Syntax:

```java
class ClassName {
    // Generic method syntax
    <T> void methodName(T param) {
        System.out.println("methodName received: " + param);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        ClassName obj = new ClassName();
        obj.methodName("Generic syntax demo");
    }
}
```

Example:

```java
import java.util.*;

// Class having generic method
class GenericMethodExample {

    // Generic method with T data type
    public <T> void print(T data) {
        System.out.println("Data: " + data);
    }
}

// Main class
class Main {
    public static void main(String[] args) {
        GenericMethodExample obj = new GenericMethodExample();

        obj.print(100);        // Output: Data: 100
        obj.print("Generics"); // Output: Data: Generics
        obj.print(3.14);       // Output: Data: 3.14
    }
}
```

**Key Points:**

- Works for multiple types
- No need for method overloading

**Important Note:** It is important to take declare the generic either in the class or in the method. Otherwise, the compiler will not be able to understand the generic used and will throw an compiler-time error.

### Bounded Type Parameters

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** Bounded type parameters restrict the type of values that can be used as generic arguments, ensuring type safety and enabling operations specific to that type.

</div>

Syntax:

```java
// Minimal stub so the bounded-type syntax below compiles
class SomeClass {
    void describe() { System.out.println("SomeClass instance"); }
}

class ClassName<T extends SomeClass> {
    // Only classes extending SomeClass are allowed as T
    private T value;

    ClassName(T value) { this.value = value; }

    T get() { return value; }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        ClassName<SomeClass> holder = new ClassName<>(new SomeClass());
        holder.get().describe();
    }
}
```

Here, T must be a subclass of SomeClass.

It cannot be any random class, and must match the bounded condition.

Example: Restricting to Number and its Subclasses

```java
import java.util.*;

// Class implemeting Bounded Type Parameters
class NumericBox<T extends Number> { // Only Number types allowed
    private T num;

    public NumericBox(T num) { this.num = num; }

    public double square() {
        return num.doubleValue() * num.doubleValue();
    }
}

// Main class
class Main {
    public static void main(String[] args) {
        NumericBox<Integer> intBox = new NumericBox<>(10);
        System.out.println(intBox.square()); // Output: 100.0

        NumericBox<Double> doubleBox = new NumericBox<>(5.5);
        System.out.println(doubleBox.square()); // Output: 30.25

        // Compile-time error!
        // NumericBox<String> strBox = new NumericBox<>("Hello");
    }
}
```

Explanation:

- NumericBox<Integer> - Allowed (because Integer extends Number)
- NumericBox<Double> - Allowed (because Double extends Number)
- NumericBox<String> - Not Allowed (because String does not extend Number)

### Wildcard Types

Wildcard types (?) in Java Generics are used when the exact type parameter is unknown. They provide flexibility in method parameters, allowing a range of types instead of a specific one.

**Benefits of using Wildcard Types:**

- Supports method parameters with unknown generic types.
- Allows flexibility in accepting multiple subtypes or supertypes.
- Reduces redundant code and enhances reusability.

**Types of Wildcard:**

- **Upper Bounded Wildcard (? extends T):** Allows reading, but restricts writing.
- **Lower Bounded Wildcard (? super T):** Allows writing, but restricts reading.

**1. Upper Bounded Wildcard (? extends T)**

? extends T allows a type parameter that is T or any subclass of T. It allows read access but restricts modification. It is useful when you need to process elements but not modify the collection.

Example: Reading from a List of Numbers or Its Subtypes

```java
import java.util.*;
import java.util.List;
import java.util.Arrays;

// Example of Upper Bound Wildcard Types
class UpperBoundExample {
    // Accepts Number and its subtypes
    public static void printList(List<? extends Number> list) {
        for (Number num : list) {
            System.out.print(num + " "); // Reading is allowed
        }
        System.out.println("");

        // Compilation error:
        // Cannot add elements to a list of `? extends Number`
        // list.add(10);
    }
}

// Main class
class Main {
    public static void main(String[] args) {
        List<Integer> intList = Arrays.asList(1, 2, 3);
        List<Double> doubleList = Arrays.asList(1.1, 2.2, 3.3);

        UpperBoundExample obj = new UpperBoundExample();

        obj.printList(intList);    // Allowed (as Integer extends Number)
        obj.printList(doubleList); // Allowed (as Double extends Number)
    }
}
```

Key Takeaways:

- Allows reading elements of type Number or its subtypes (Integer, Double, etc.).
- Prevents adding new elements (except null), as the exact subtype is unknown.

**2. Lower Bounded Wildcard (? super T)**

? super T means any type that is T or a superclass of T. It allows write access but restricts reading. It is useful when adding elements to a collection.

Example: Adding Elements to a List of Integers or Its Supertypes

```java
import java.util.*;
import java.util.List;
import java.util.ArrayList;

// Example of Lower Bound Wildcard Types
class LowerBoundExample {
    // Accepts Integer and its supertypes
    public static void addNumbers(List<? super Integer> list) {
        list.add(10); // Allowed
        list.add(20);

        // Reading AND Storing is not Allowed
        // Integer num = list.get(0); // Error: Cannot guarantee it’s an Integer

        System.out.println(list);
    }
}

// Main class
class Main {
    public static void main(String[] args) {
        LowerBoundExample obj = new LowerBoundExample();

        // Number is a superclass of Integer
        List<Number> numList = new ArrayList<>();
        obj.addNumbers(numList); // Allowed

        // Object is also a superclass of Integer
        List<Object> objList = new ArrayList<>();
        obj.addNumbers(objList); // Allowed
    }
}
```

Key Takeaways:

- Allows adding elements of type Integer because List<? super Integer> ensures that Integer is a valid type.
- Prevents retrieving elements as List<? super Integer> might contain Integer, Number, or Object, making it unsafe to cast directly to Integer.

### Raw Type

A raw type in Java is a generic class or interface that is used without specifying a type parameter. Before Java 5, collections and generic classes operated without type safety, leading to potential runtime errors.

A raw type is when you omit the type parameter while declaring an instance of a generic class.

Example: Using a Raw Type

```java
import java.util.*;

// Generic class
class Box<T> {
    T value;

    void set(T value) { this.value = value; }
    T get() { return value; }
}

// Main class
class Main {
    public static void main(String[] args) {
        // Raw Type (because no type is given while declaration)
        Box rawBox = new Box();

        rawBox.set("Hello");
        rawBox.set(100); // No compile-time error, but runtime issues may occur

        System.out.println("rawBox now holds: " + rawBox.get());
    }
}
```

The above code compiles without errors, but mixing different types can cause runtime exceptions.

**Why are Raw Types Problematic?**

Using raw types can lead to unchecked warnings and runtime exceptions.

Example: Runtime Error with Raw Types

```java
// expects-exception: type erasure lets this compile; the ClassCastException only surfaces when the mistyped value is read back
import java.util.*;

// Generic class
class Box<T> {
    T value;

    void set(T value) { this.value = value; }
    T get() { return value; }
}

// Main class
class Main {
    public static void main(String[] args) {
        Box rawBox = new Box(); // Raw Type
        rawBox.set("Hello");

        Box<Integer> intBox = rawBox; // Unsafe assignment (No type check)

        // No error at compile-time, but type mismatch at runtime:
        // intBox believes it holds an Integer, but rawBox actually stored a String
        Integer num = intBox.get(); // ClassCastException: String cannot be cast to Integer
        System.out.println("Never reached: " + num);
    }
}
```

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** The above code exhibits the risk of mixing String and Integer in rawBox that causes a ClassCastException at runtime.

</div>

Hence, it is not considered a good practice to use Raw Types.

### Type Erasure

Type Erasure is a fundamental concept in Java Generics, where generic type parameters (<T>) are removed at compile-time. This ensures backward compatibility with legacy Java versions (before Java 5), where generics did not exist.

**Key Points:**

- Generics exist only at compile-time; they do not exist at runtime.
- The JVM does not retain type parameters () after compilation.
- The compiler replaces generic types with raw types (Object or bound type).

Example: Generic Class Before Compilation

```java
import java.util.*;

// Generic Class before compilation
class Box<T> {
    private T value;

    void set(T value) { this.value = value; }
    T get() { return value; }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Box<String> box = new Box<>();
        box.set("Before erasure");
        System.out.println(box.get());
    }
}
```

After Compilation (Type Erasure)

```java
import java.util.*;

// Generic Class after compilation
class Box {  // `<T>` is erased
    private Object value;

    // `<T>` replaced with `Object`
    void set(Object value) { this.value = value; }
    Object get() { return value; }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Box box = new Box();
        box.set("After erasure");
        String value = (String) box.get(); // explicit cast is exactly what the compiler now inserts for you
        System.out.println(value);
    }
}
```

At runtime, all generic types are treated as Object or their upper bound.

Reasons for Type Erasure in Java:

- **Backward Compatibility:** Allows generic code to work with older Java versions.
- **Performance Optimization:** Avoids unnecessary runtime overhead.
- **Simplifies JVM Implementation:** Keeps bytecode simple.

Impact of Type Erasure on Code:

Since generics are removed at compile-time, certain operations become restricted. For instance, using instanceof with generic types is not allowed, as the type information is erased. Similarly, creating generic arrays is not possible, since the runtime does not retain the actual type of the generic parameter.

These limitations arise because Java replaces generic types with Object or their upper bound, making it impossible to perform certain type-specific operations at runtime.

## File Handling in Java

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** File handling refers to the process of reading from and writing to files to store and retrieve data persistently.

</div>

It allows programs to interact with files stored on disk, enabling long-term data storage and retrieval.

There are various operations involved in File Handling, some of which are:

- Creating a file
- Reading from a file
- Writing to a file
- Appending data to a file
- Deleting a file

Example: Creating a File

Java provides the File class from the java.io package to handle file operations.

```java
import java.util.*;
import java.io.File;
import java.io.IOException;

class Main {
    public static void main(String[] args) {
        try {
            File file = new File("example.txt");
            if (file.createNewFile()) {
                System.out.println("File created: " + file.getName());
            } else {
                System.out.println("File already exists.");
            }
            // Clean up so re-running this example starts from the same state.
            file.delete();
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }
}
```

Here, try-catch block is used to handle the potential IOException from the createNewFile(). The createNewFile() method in Java throws an IOException if an error occurs while creating the file (e.g., insufficient permissions, invalid file path, or disk-related issues).

### Importance of File Handling in OOPs

File handling is crucial in object-oriented programming (OOPs) because it provides mechanisms for:

- **Logging:** Storing logs for debugging and monitoring.
- **Configuration Management:** Reading and writing configuration settings from files.
- **Data Storage:** Storing user-generated content, records, or database backups.

### File Class

The File class in Java provides various methods for manipulating files and directories. Some of the commonly used methods are:

- **createNewFile():** Creates a new empty file.
- **exists():** Checks if a file exists.
- **delete():** Deletes a file.
- **getAbsolutePath():** Returns the file's absolute path.
- **length():** Returns the size of the file in bytes.
- **canRead(), canWrite():** Checks file permissions.

Example: Checking File Properties

```java
import java.util.*;
import java.io.File;

// Main class
class Main {
    public static void main(String[] args) {
        File file = new File("example.txt");

        if (file.exists()) {
            System.out.println("File Name: " + file.getName());
            System.out.println("Absolute Path: " + file.getAbsolutePath());
            System.out.println("Writable: " + file.canWrite());
            System.out.println("Readable: " + file.canRead());
            System.out.println("File Size in bytes: " + file.length());
        } else {
            System.out.println("The file does not exist.");
        }
    }
}
```

### FileWriter and BufferedWriter

The FileWriter class is used to write character-based data to a file, and BufferedWriter improves efficiency by buffering large amounts of data before writing.

Example: Writing Data using BufferedWriter

```java
import java.util.*;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

// Main class
class Main {
    public static void main(String[] args) {
        BufferedWriter writer = null;

        // Try-catch block to handle exception
        try {
            writer = new BufferedWriter(new FileWriter("output.txt"));

            // Writing in the file
            writer.write("Hello, world!\n");
            writer.write("This is a sample file.");

            // Closing the file after writing
            writer.close();
            System.out.println("File written successfully.");
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Remaining section of the code
    }
}
```

### FileReader and BufferedReader

The FileReader class is used to read data from a file as a stream of characters, while BufferedReader improves efficiency by reading large chunks of data at once.

Example: Reading a File Using BufferedReader

```java
import java.util.*;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

// Main class
class Main {
    public static void main(String[] args) {

        // Create the file first so this block is self-contained
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("example.txt"))) {
            writer.write("Hello, world!");
            writer.newLine();
            writer.write("This is a sample file.");
        } catch (IOException e) {
            e.printStackTrace();
        }

        BufferedReader reader = null;

        // try-catch block to handle the exception
        try {
            reader = new BufferedReader(new FileReader("example.txt"));
            String line;

            int i = 1;

            // Read each line until nothing is left
            while((line = reader.readLine()) != null) {
                System.out.println("Line " + i + ": " + line);
                i++;
            }

            reader.close(); //Close the file after reading
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### Try-with-Resources

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** The try-with-resources statement automatically closes the file resource after execution, ensuring proper resource management. This eliminates the chances of missing closing any file used in the codebase, preventing resource leakage.

</div>

The try-with-resource is nothing but a try block with the resources declared in its arguments.

Example: Using Try-with-Resources for File Reading

```java
import java.util.*;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

// Main class
class Main {
    public static void main(String[] args) {

        // Create the file first so this block is self-contained
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("example.txt"))) {
            writer.write("Hello from try-with-resources!");
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Try with Resources (removes the need to close the file explicitly)
        try (BufferedReader reader = new BufferedReader(new FileReader("example.txt"))) {
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### Logging Application Data

Logging is essential for debugging and monitoring an application. The java.util.logging package provides built-in support for logging.

Example: Logging to a file

```java
import java.util.*;
import java.io.*;

// Logger class
class Logger {
    private String path; // to store the path of file

    // Constructor
    Logger(String path) throws IOException {
        File file = new File(path); // Open the file path

        // Create the file if it does not exist
        if (!file.exists()) {
            file.createNewFile();
        }
        this.path = path;
    }

    // Log the message in the file
    public void log(String message) {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(path, true))) {
            bw.write(message);
            bw.newLine();
        } catch (Exception e) {
            System.out.println("Failed to log this message " + message);
        }
    }
}

// Main class
class Main {
    public static void main(String[] args) {
        try {
            // Create a Logger instance with a specified log file path
            Logger myLogger = new Logger("application.log");

            // Log some messages
            myLogger.log("Application started...");
            myLogger.log("User logged in.");
            myLogger.log("Error: Unable to connect to the database.");
            myLogger.log("Application closed.");

            System.out.println("Logs have been written successfully.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

**Code Breakdown:**

- **Instance Variable:** private String path; → Stores the file path where logs will be written.
- **Constructor (Logger(String path)):**
  - Takes the log file path as a parameter.
  - Uses the File class to check if the file exists. If not, it creates a new file.
  - Initializes the path variable with the given file path.
- **log(String message) Method:**
  - Uses BufferedWriter and FileWriter to write messages to the log file.
  - The second argument true in FileWriter(path, true) enables appending mode, ensuring logs are added instead of overwriting the file.
  - Writes the message to the file and adds a new line (newLine()).
  - Handles exceptions and prints a failure message if writing fails.

The above code provides a simple example of the Logger class. You can build a more feature-rich (timestamps, data information, etc.) Logger class as per your convenience using Java's built-in java.util.logging package.

### Common File Handling Issues

Several issues can arise while handling files, such as:

- **FileNotFoundException:** Occurs when the specified file does not exist. It can be avoided by checking if the file exists before attempting to read it.
- **IOException:** Occurs due to issues like permission restrictions, insufficient disk space, or network failure. It can be handled using try-catch blocks.
- **Resource Leaks:** Forgetting to close file streams can lead to memory leaks. To avoid this, the best practice is to use try-with-resources to automatically close resources.

## Object Lifecycle in Java

In Java, the object lifecycle refers to the various stages an object goes through during its existence—from creation to destruction. Understanding this lifecycle is crucial for efficient memory management and avoiding issues like memory leaks.

An object in Java typically follows this lifecycle: Creation → Usage → Garbage Collection → Destruction

- **Creation:** Allocated memory on the heap using new.
- **Usage:** Methods and fields of the object are used.
- **Garbage Collection:** When no references point to the object, it becomes eligible for GC.
- **Destruction:** JVM garbage collector destroys and reclaims the memory.

To understand this better, consider the following code:

```java
import java.util.*;

class Demo {
    void performTask() {
        System.out.println("Task performed");
    }
}

class Main {
    public static void main(String[] args) {
        Demo obj = new Demo();
        obj.performTask();
    }
}
```

**What happens in memory?**

- obj (the reference variable) is stored in stack memory.
- new Demo() creates an object that is stored in the heap memory.
- After the execution of main(), the obj reference goes out of scope.
- Now, no reference points to the Demo object in heap memory.
- Hence, Java's Garbage Collector will identify it as unreachable and destroy the object, freeing up memory.

This illustrates the automatic memory management Java provides and forms the foundation of the object lifecycle.

### Object Creation

Objects are created using the new keyword, which allocates memory on the heap.

```java
import java.util.*;

class Student {
    String name;

    Student(String name) {
        this.name = name;
    }
}

class Main {
    public static void main(String[] args) {
        Student s = new Student("Alex");
        System.out.println(s.name);
    }
}
```

Here in the above code, the Student object is created using the constructor. The new keyword allocates memory for the object on the heap, and the reference variable s points to that memory location.

### Reference Counting

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** Reference counting is a memory management technique used in computer science to track how many parts of a program are using a specific resource (like an object or memory block).

</div>

In Object Oriented Programming, each object keeps track of the number of references pointing to it. When an object's reference count drops to zero, it is considered unreachable and can be deallocated.

In simpler words, an object is eligible for GC (garbage collection) when it is no longer referenced from any live thread.

Note that, Java does not actually use reference counting as its garbage collection mechanism, but understanding reference counting can still help us conceptually understand when objects become eligible for garbage collection.

**Why is it not used in Java?**

- Java uses reachability-based garbage collection instead of reference counting.
- It uses graph traversal algorithms like Mark-and-Sweep to find all objects that are reachable from active threads.
- Even if reference count is 1 (in theory), an object could still be unreachable (like in the case of cyclic references).
- Java's GC handles cyclic references, which reference counting fails to clean up.

```java
import java.util.*;

class A {}

class Main {
    public static void main(String[] args) {
        A a1 = new A(); // Object created
        A a2 = a1;      // Two references
        System.out.println("a1 and a2 reference the same object: " + (a1 == a2));

        a1 = null;      // One reference remains
        System.out.println("a1 set to null; a2 still references the object: " + (a2 != null));

        a2 = null;      // Now zero references -> Eligible for GC
        System.out.println("a2 set to null; object is now unreachable and eligible for GC");
    }
}
```

While Java doesn't actually count references, this example helps learners understand how and when objects become unreachable.

### Garbage Collection in Java

Java uses automatic garbage collection. The garbage collector (GC) identifies unused objects and frees memory. It is important to understand that the Garbage Collector isn't a single unified concept, but has multiple implementations. Let's understand the Garbage Collection process in Java.

**Garbage Collection Process in Java**

At a broad level, Java's garbage collection (GC) process operates in three primary stages: marking, sweeping, and compacting. Depending on the specific garbage collector (like G1, ZGC, etc.), these stages may include more granular sub-steps, but the core concepts remain consistent across implementations.

- **Mark Phase:** When a new object is created, the Java Virtual Machine (JVM) assigns it a marking flag, initially set to false (or 0). This bit serves as an indicator of whether the object is still reachable. The GC starts by marking all reachable objects, beginning from the root set (like local variables, static fields, etc.). It traverses the object graph, marking each object it encounters.
- **Sweep Phase:** Once marking is complete, the GC proceeds to the sweeping phase. Here, it goes through the heap and looks for objects that remain unmarked — meaning they were not found during the marking phase. These are considered garbage, as nothing in the program can access them anymore. Such unreachable objects are then deleted, and their memory is reclaimed, making room for future allocations.
- **Compaction Phase:** Over time, object deletion creates gaps in memory, leading to fragmentation. The compaction phase addresses this by reorganizing live (reachable) objects to eliminate those gaps. This is done by moving objects closer together, which not only optimizes memory usage but also improves cache performance.

Note that not all garbage collectors perform compaction. For example, the G1 garbage collector does this in a more sophisticated way, focusing on regions rather than the entire heap.

**GC Pauses: Stop-the-World Events**

During garbage collection, there can be moments when the JVM must pause application execution to safely manage memory. These are known as Stop-the-World (STW) events.

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** Because heap memory is not inherently thread-safe, allowing normal application threads to run while the GC is modifying object references could cause unpredictable behavior or errors.

</div>

To prevent this, the JVM may halt all or parts of the program temporarily until the GC finishes its current phase, especially marking and compacting.

Some advanced garbage collectors (like G1, ZGC, or Shenandoah) try to minimize pause times, but some amount of pausing is usually unavoidable.

**System.gc();**

The System.gc() method is a request to the JVM to perform garbage collection. However, it is not a guarantee that the GC will run immediately. The JVM may choose to ignore this request based on its own heuristics and optimizations.

It is generally not recommended to call System.gc() in production code, as it can lead to unpredictable performance and may interfere with the JVM's own garbage collection strategy.

### Memory Leaks

A memory leak happens when a program allocates memory but fails to release it after it's no longer needed. Over time, these unused memory blocks accumulate, leading to reduced available memory and potentially causing the program (or even the whole system) to slow down or crash.

Even though Java has an automatic garbage collection, a memory leak can still happen if the code unintentionally keeps references to objects that are no longer needed. As a result, the garbage collector cannot reclaim that memory, leading to increased memory usage over time.

A memory leak in Java typically happens when:

- Objects are stored in a static field, collection, or long-lived object and are not removed when no longer needed.
- Listeners or callbacks are added but not unregistered.
- Caches or maps grow indefinitely without proper cleanup.

Consider the following example to understand it better:

```java
import java.util.*;
import java.util.*;

class MemoryLeakExample {
    // Static list holds references for the entire life of the program
    private static List<Object> staticList = new ArrayList<>();

    public void addToStaticList(Object obj) {
        // Every object added here is never removed, so memory keeps growing
        staticList.add(obj);
    }
}

class Main {
    public static void main(String[] args) {
        MemoryLeakExample example = new MemoryLeakExample();

        for (int i = 0; i < 1000000; i++) {
            // Adding new objects continuously without freeing them
            example.addToStaticList(new Object());
        }

        System.out.println("Objects added to static list.");
    }
}
```

**Understanding**

In this example, the staticList holds references to all objects added to it. Since the list is static, it lives for the entire duration of the program. As a result, even though the loop creates a million objects, they are never eligible for garbage collection because they are still referenced in staticList.

Over time, this can lead to a java.lang.OutOfMemoryError, especially in long-running applications like servers or GUI apps.

### Cyclic Reference

A cyclic reference occurs when two or more objects reference each other directly or indirectly, forming a loop, so none of them can be garbage collected—even if they are no longer accessible from the rest of the program.

The following example shows the formation of cyclic reference in a program:

```java
import java.util.*;

class Node {
    Node next;
}

class Main {
    public static void main(String[] args) {
        Node a = new Node();
        Node b = new Node();
        a.next = b;
        b.next = a; // Cyclic reference formed

        System.out.println("Cycle formed: a.next == b? " + (a.next == b));
        System.out.println("Cycle formed: b.next == a? " + (b.next == a));
    }
}
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Unlike some languages, cyclic references do not cause memory leaks in Java, thanks to the reachability algorithm.

</div>

Java's garbage collector is smart enough to detect unreachable objects, even if they reference each other in a cycle.

### Best Practices

Here are some key best practices for managing the object lifecycle efficiently:

- **Avoid Explicit Null Assignments:** Manually setting objects to null rarely helps GC and can reduce readability.
- **Avoid Memory Leaks:** This can be done by clearing listeners and callbacks. Avoid overly complex or deeply nested data structures that are hard to track and clean up, especially when storing long-lived references.
- **Minimize Scope of Variables:** The sooner a reference goes out of scope, the earlier it becomes eligible for GC.
