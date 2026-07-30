---
title: "Encapsulation, Access Modifiers, Inheritance & Polymorphism"
summary: "Data hiding through encapsulation and access modifiers, code reuse through inheritance hierarchies, and single-interface-many-behaviors through polymorphism — with worked Java examples and practice problems for each."
essential: true
---

# Encapsulation, Access Modifiers, Inheritance & Polymorphism

## Encapsulation (Data Hiding in Java)

Encapsulation is a fundamental concept in object-oriented programming (OOP) where the internal details (data and logic) of an object are hidden from the outside world. It is the process of bundling the object's data (attributes) and methods (functions) together into a single unit or class. The primary goal is to protect the internal state of an object from unintended modifications and provide controlled access to it.

In simple terms, encapsulation ensures that the object's internal workings are hidden from other objects, allowing external entities to interact with the object only through well-defined interfaces (methods).

**Key concept.** Encapsulation enforces data hiding and ensures that attributes (variables) within a class are not directly accessible to other classes or external code. Instead, it provides getter and setter methods to access and modify these private attributes. By making attributes private, encapsulation maintains control over how the data is accessed and modified, preventing unwanted changes or access.

For example:

- Private attributes (fields) ensure that no one can directly alter the object's state.
- Public getter and setter methods allow controlled access and modification of private attributes, enabling additional business logic or validation during the process.

### Importance of Encapsulation

There are several benefits of using encapsulation, which are as follows:

- **Data Security:** The most significant benefit is data protection. Sensitive data can be hidden from external manipulation and can only be accessed or modified in a controlled manner.
- **Flexibility and Maintenance:** If the internal implementation needs to change, encapsulation allows you to modify the code without affecting external code. You can alter the internal representation of the data or how it's accessed, as long as the public interface (methods) remains the same.
- **Modular Code:** Encapsulation promotes cleaner, modular code by bundling related data and behaviors together. It helps in organizing the code, making it more readable and maintainable.
- **Improved Debugging and Testing:** Since all access to an object's internal state is controlled, debugging and testing become easier. You can validate the behavior of methods (like getters and setters) independently.
- **Reduced Complexity:** By hiding complex internal implementations and exposing only what is necessary, encapsulation simplifies the usage of objects and reduces the chances of errors in using the class.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** The flexibility payoff is the one that matters most day to day: because callers only ever touch the public interface, you're free to change how the data is represented or validated internally without breaking a single line of calling code — as long as the public methods keep their same signatures.

</div>

### Example

Consider the following code snippet:

```java
import java.util.*;

class BankAccount {
    // Private attributes
    private String accountHolderName;
    private double balance;

    // Constructor
    public BankAccount(String accountHolderName, double balance) {
        this.accountHolderName = accountHolderName;
        this.balance = balance;
    }

    // Public getter for accountHolderName
    public String getAccountHolderName() {
        return accountHolderName;
    }

    // Public setter for accountHolderName
    public void setAccountHolderName(String accountHolderName) {
        this.accountHolderName = accountHolderName;
    }

    // Public getter for balance
    public double getBalance() {
        return balance;
    }

    // Public setter for balance (only allows positive deposits)
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        } else {
            System.out.println("Deposit amount must be positive.");
        }
    }

    // Public method to withdraw money
    public void withdraw(double amount) {
        if (amount > balance) {
            System.out.println("Insufficient funds.");
        } else {
            balance -= amount;
        }
    }
}

class Main {
    public static void main(String[] args) {
        // Creating an object of BankAccount
        BankAccount account = new BankAccount("John Doe", 5000);

        // Using getter to access private data
        System.out.println("Account Holder: " + account.getAccountHolderName());
        System.out.println("Balance: " + account.getBalance());

        // Modifying balance using setter method
        account.deposit(1500);
        System.out.println("Updated Balance: " + account.getBalance());

        // Trying to withdraw an amount
        account.withdraw(2000);
        System.out.println("Balance after Withdrawal: " + account.getBalance());
    }
}
```

**The same idea in Python**

```python
class BankAccount:
    # Python has no compiler-enforced "private" — encapsulation here is social, not
    # enforced. Two conventions, both breakable:
    #   _balance   single underscore -> "internal, please don't touch" (pure convention,
    #              directly reachable, nothing stops you)
    #   __balance  double underscore -> triggers *name mangling* to _BankAccount__balance;
    #              it discourages accidental access but is still reachable if you know
    #              the mangled name (see the driver below).
    def __init__(self, account_holder_name: str, balance: float) -> None:
        self._account_holder_name = account_holder_name
        self.__balance = balance  # mangled to self._BankAccount__balance

    @property
    def account_holder_name(self) -> str:
        return self._account_holder_name

    @account_holder_name.setter
    def account_holder_name(self, name: str) -> None:
        self._account_holder_name = name

    @property
    def balance(self) -> float:
        return self.__balance

    def deposit(self, amount: float) -> None:
        if amount > 0:
            self.__balance += amount
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount: float) -> None:
        if amount > self.__balance:
            print("Insufficient funds.")
        else:
            self.__balance -= amount


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    account = BankAccount("John Doe", 5000)

    print(f"Account Holder: {account.account_holder_name}")
    print(f"Balance: {account.balance}")

    account.deposit(1500)
    print(f"Updated Balance: {account.balance}")

    account.withdraw(2000)
    print(f"Balance after Withdrawal: {account.balance}")

    # Honest demo: "private" is only a naming convention. Name mangling renames the
    # attribute, it does not block access — this reaches right past it from outside
    # the class, which real Java `private` would never allow.
    print(f"Reached anyway via name mangling: {account._BankAccount__balance}")
```

The class's shape — private state, public interface — looks like this:

```mermaid
classDiagram
    class BankAccount {
        -String accountHolderName
        -double balance
        +getAccountHolderName() String
        +setAccountHolderName(String accountHolderName) void
        +getBalance() double
        +deposit(double amount) void
        +withdraw(double amount) void
    }
```

### Key Takeaways

- **Private Data:** In the example above, the `accountHolderName` and `balance` attributes are made private using the `private` keyword. This restricts direct access to the attributes from outside the class.
- **Getter and Setter Methods:** The `getBalance()` and `deposit()` methods are public and act as controlled interfaces to interact with the private data.
- **Controlled Access:** The `deposit()` method includes a check to ensure that only positive amounts are added to the balance, maintaining data integrity.

By encapsulating the `BankAccount` class, we make sure that the balance cannot be arbitrarily altered from outside the class, which protects it from unintended modifications and ensures proper validation is performed.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** Encapsulation is just a design principle. Access modifiers and getters/setters are mechanisms used to achieve encapsulation.

</div>

Let us now understand access modifiers, which help us achieve encapsulation.

### Your Turn — Practice: Encapsulation

Model a library `Book` catalogue that hides its availability flags behind borrow / return / query methods — encapsulation in a realistic shape.

````problem
Design a class `Book` to manage book details in a library.

**Attributes**

- `title` (`List<String>`) — book titles (public).
- `author` (`List<String>`) — authors (public).
- `isAvailable` (`List<Boolean>`) — availability per book (**private**).

**Methods**

- A parameterised constructor initialising the three lists.
- `borrowBook(String bookName)` — if the book is available, mark it borrowed (flag → `false`). If it is already borrowed, or the name is unknown, print `Book is not available.`.
- `returnBook(String bookName)` — mark the book available again (flag → `true`).
- `getAvailability(String bookName)` — print `true` if available, otherwise `false`.

**Input format.** Four lines on standard input: comma-separated `titles`, comma-separated `authors`, comma-separated availability flags (`true`/`false`), then a semicolon-separated list of operations. Each operation is `<code> <bookName>`, where `1` = borrow, `2` = return, `3` = getAvailability. The provided `Main` parses these and dispatches to your methods — you implement `Book`.

**Example 1**

```text
titles     : Sherlock_Holmes, Frankenstein, King_Arthur_and_the_Round_Table, Treasure_Island
authors    : Arthur_Conan_Doyle, Mary_Shelley, Roger_Lancelyn_Green, Robert_Louis_Stevenson
available  : false, true, false, false
operations : 1 Frankenstein ; 1 Sherlock_Holmes ; 2 King_Arthur_and_the_Round_Table ; 3 Sherlock_Holmes ; 1 Frankenstein
```

Output:

```text
Book is not available.
false
Book is not available.
```

Borrowing `Frankenstein` succeeds silently; borrowing the already-unavailable `Sherlock_Holmes` prints the message; returning `King_Arthur…` succeeds; querying `Sherlock_Holmes` prints `false`; and `Frankenstein` — borrowed in step 1, never returned — can't be borrowed again.

**Constraints:** one copy of each book; a borrowed book stays unavailable until returned.
````

```java run
import java.util.*;

class Book {
    // Encapsulation: keep isAvailable PRIVATE; the only way to change state is via the methods below.
    // TODO: fields — public List<String> title, author; private List<Boolean> isAvailable

    public Book(List<String> title, List<String> author, List<Boolean> isAvailable) {
        // TODO: store the three lists
    }

    public void borrowBook(String bookName) {
        // TODO: find bookName; if available -> set false; else print "Book is not available."
    }

    public void returnBook(String bookName) {
        // TODO: find bookName; mark it available again
    }

    public void getAvailability(String bookName) {
        // TODO: print "true" if available, otherwise "false"
    }
}

// The driver parses stdin and dispatches operations — implement Book above.
class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> title = new ArrayList<>(Arrays.asList(sc.nextLine().split(",")));
        List<String> author = new ArrayList<>(Arrays.asList(sc.nextLine().split(",")));
        List<Boolean> isAvailable = new ArrayList<>();
        for (String s : sc.nextLine().split(",")) isAvailable.add(Boolean.parseBoolean(s.trim()));
        String opsLine = sc.hasNextLine() ? sc.nextLine() : "";

        Book book = new Book(title, author, isAvailable);
        if (!opsLine.trim().isEmpty()) {
            for (String op : opsLine.split(";")) {
                String[] p = op.trim().split("\\s+");
                if (p.length < 2) continue;
                if (p[0].equals("1")) book.borrowBook(p[1]);
                else if (p[0].equals("2")) book.returnBook(p[1]);
                else if (p[0].equals("3")) book.getAvailability(p[1]);
            }
        }
    }
}
```

```testcases
{
  "args": [
    { "id": "titles", "label": "Titles (comma-separated)", "type": "string" },
    { "id": "authors", "label": "Authors (comma-separated)", "type": "string" },
    { "id": "available", "label": "Available (comma-separated)", "type": "string" },
    { "id": "ops", "label": "Operations (semicolon-separated)", "type": "string" }
  ],
  "cases": [
    { "args": {
        "titles": "Sherlock_Holmes,Frankenstein,King_Arthur_and_the_Round_Table,Treasure_Island",
        "authors": "Arthur_Conan_Doyle,Mary_Shelley,Roger_Lancelyn_Green,Robert_Louis_Stevenson",
        "available": "false,true,false,false",
        "ops": "1 Frankenstein;1 Sherlock_Holmes;2 King_Arthur_and_the_Round_Table;3 Sherlock_Holmes;1 Frankenstein"
      },
      "expected": "Book is not available.\nfalse\nBook is not available." }
  ]
}
```

````editorial
`isAvailable` is `private`, so the only way to change a book's state is through `borrowBook` / `returnBook` — that's the encapsulation the problem is really testing. Each method scans the parallel `title` list for the name, then reads or flips the matching flag. Borrowing an unavailable or unknown book prints the message; querying just prints the flag.

```java solution
import java.util.*;

class Book {
    private List<Boolean> isAvailable;
    public List<String> title;
    public List<String> author;

    public Book(List<String> title, List<String> author, List<Boolean> isAvailable) {
        this.title = title;
        this.author = author;
        this.isAvailable = isAvailable;
    }

    public void borrowBook(String bookName) {
        for (int i = 0; i < title.size(); i++) {
            if (title.get(i).equals(bookName)) {
                if (isAvailable.get(i)) {
                    isAvailable.set(i, false);
                    return;
                } else {
                    System.out.println("Book is not available.");
                    return;
                }
            }
        }
        System.out.println("Book is not available.");
    }

    public void returnBook(String bookName) {
        for (int i = 0; i < title.size(); i++) {
            if (title.get(i).equals(bookName)) {
                if (!isAvailable.get(i)) {
                    isAvailable.set(i, true);
                    return;
                }
            }
        }
    }

    public void getAvailability(String bookName) {
        for (int i = 0; i < title.size(); i++) {
            if (title.get(i).equals(bookName)) {
                if (isAvailable.get(i)) {
                    System.out.println("true");
                    return;
                }
            }
        }
        System.out.println("false");
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> title = new ArrayList<>(Arrays.asList(sc.nextLine().split(",")));
        List<String> author = new ArrayList<>(Arrays.asList(sc.nextLine().split(",")));
        List<Boolean> isAvailable = new ArrayList<>();
        for (String s : sc.nextLine().split(",")) isAvailable.add(Boolean.parseBoolean(s.trim()));
        String opsLine = sc.hasNextLine() ? sc.nextLine() : "";

        Book book = new Book(title, author, isAvailable);
        if (!opsLine.trim().isEmpty()) {
            for (String op : opsLine.split(";")) {
                String[] p = op.trim().split("\\s+");
                if (p.length < 2) continue;
                if (p[0].equals("1")) book.borrowBook(p[1]);
                else if (p[0].equals("2")) book.returnBook(p[1]);
                else if (p[0].equals("3")) book.getAvailability(p[1]);
            }
        }
    }
}
```
````

## Access Modifiers

Access modifiers in object-oriented programming are keywords that define the visibility and accessibility of classes, methods, variables, and other members of a program. They determine which parts of the program can interact with a particular component, ensuring that code adheres to encapsulation, a key principle of object-oriented programming.

Access modifiers control interactions between objects and help enforce good design practices, making programs more reliable, scalable, and easier to debug.

### Purpose of Access Modifiers

In object-oriented programming, the access modifiers play a key role and serve the following purposes:

- **Encapsulation:** Ensures sensitive data and methods are protected from unintended access.
- **Controlled Access:** Allows programmers to specify which parts of the program can interact with certain components.
- **Modularity and Security:** Helps in maintaining the integrity of data by restricting unwanted modifications.
- **Flexibility:** Provides mechanisms for controlled sharing of data between classes and packages.

### Types of Access Modifiers

Most of the Object Oriented Programming languages provide the following four access levels:

- **Public:** Accessible everywhere (within the same class, same package, and outside the package).
- **Private:** Accessible only within the class where it is declared.
- **Protected:** Accessible within the same package and by subclasses in other packages.
- **Default:** (No Modifier) Accessible within the same package (package-private).

### Public Access Modifier

The public access modifier can make the attributes and methods of a class accessible from anywhere in the program, including classes outside the package. For example, consider the following code snippet:

```java
import java.util.*;

class Employee {
    public String name; // Public attribute

    public void displayName() { // Public method
        System.out.println("Employee Name: " + name);
    }
}

class Main {
    public static void main(String[] args) {
        Employee emp = new Employee();
        emp.name = "Alice"; // Accessible globally
        emp.displayName();  // Accessible globally
    }
}
```

Here, the `name` attribute and the `displayName()` method are set to public so they can be accessed from outside the class (in the main method).

**Keypoints:**

- Used to provide attributes and methods global access.
- Best suited for methods and attributes that need to be universally available.
- Does not restrict usage or visibility.
- Used for APIs.

### Private Access Modifier

The private access modifier can make the attributes and methods of a class accessible only within the class where they were declared. For example, consider the following code snippet:

```java
import java.util.*;

class BankAccount {
    private double balance; // Private attribute

    // Getter to provide controlled access
    public double getBalance() {
        return balance;
    }

    // Public method to deposit money
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        }
    }
}

// Main Class
class Main {
    public static void main(String[] args) {
        // Creating an object
        BankAccount acnt = new BankAccount();

        // System.out.println(acnt.balance); // ❌ won't compile: balance has private access in BankAccount
        System.out.println(acnt.getBalance());
    }
}
```

Here, the `balance` attribute is set to private, so it can only be accessed from within the class (using the `getBalance()` method) and throws an error when accessed outside of the class.

**Keypoints:**

- Restricts access to sensitive data (`balance`) during compile-time providing compile-time protection.
- Encourages the use of getter and setter methods to provide controlled access.
- Not visible to subclasses or classes within the same package.

### Protected Access Modifier

The protected access modifier can make the attributes and methods of a class accessible within the same package and in subclasses (even if they are in different packages). For example, consider the following code snippet:

```java
import java.util.*;

class Vehicle {
    protected String type; // Protected attribute

    protected void displayType() { // Protected method
        System.out.println("Vehicle Type: " + type);
    }
}

class Car extends Vehicle {
    public Car() {
        this.type = "Car"; // Accessible in the subclass
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Car car = new Car();
        car.displayType();
    }
}
```

Here, the subclasses can inherit and use the `type` attribute and `displayType()` method.

**Keypoints:**

- Promotes inheritance by allowing child classes to access certain members of the parent class.
- Provides more visibility than private but less than public.
- Not accessible to unrelated classes outside the package.

### Default (No modifier)

When there is no access modifier specified, by default, the member is package-private in Java. This means that the member is accessible only in the package in which the class is declared, and nowhere else.

Consider the following code snippet:

```java
import java.util.*;

class PackageDemo {
    void showMessage() { // Default access
        System.out.println("Default access in the same package.");
    }
}

public class Main {
    public static void main(String[] args) {
        PackageDemo demo = new PackageDemo();
        demo.showMessage(); // Accessible because it's in the same package
    }
}
```

Here, the `showMessage()` method can be accessed from the `Main` class because it is set to package-private by default.

**Keypoints:**

- Accessible only within classes in the same package.
- Not accessible in subclasses or classes outside the package.
- Helps in maintaining package-level encapsulation.

### Comparison table

Here's a table showing whether different scopes like Class, Package, Subclass, or World can access the members and attributes defined under different access specifiers:

| Access Modifier | Class | Package (Same Package) | Subclass (Different Package) | World (Different Package) |
| --- | --- | --- | --- | --- |
| Public | ✔️ | ✔️ | ✔️ | ✔️ |
| Protected | ✔️ | ✔️ | ✔️ | ❌ |
| Default | ✔️ | ✔️ | ❌ | ❌ |
| Private | ✔️ | ❌ | ❌ | ❌ |

**The same idea in Python**

Python has no compiler-enforced access modifiers at all — only the naming conventions below (public by default, `_name` for "internal", `__name` for name-mangled), so there's no direct four-way public/protected/default/private mapping to draw.

```python
class Employee:
    def __init__(self, name: str, employee_id: int, salary: float) -> None:
        self.name = name                   # public: no leading underscore
        self._employee_id = employee_id    # "protected"-ish: internal by convention
        self.__salary = salary             # name-mangled to _Employee__salary


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    emp = Employee("Alice", 101, 75000.0)
    print(f"Name: {emp.name}")
    print(f"Employee id (protected by convention): {emp._employee_id}")
    print(f"Salary (mangled, still reachable): {emp._Employee__salary}")
```

### Your Turn — Practice: Access Modifiers

Give `Employee` a `public` name, a `protected` id, and a `private` salary — then guard the salary against negative values on both the constructor and the setter.

````problem
Design a class `Employee` that manages employee details using proper access modifiers.

**Attributes**

- `name` (`String`) — **public**.
- `employeeId` (`int`) — **protected**.
- `salary` (`double`) — **private**.

**Methods**

- A parameterised constructor initialising the attributes. If `salary` is negative, print `Invalid salary` and set it to `0`.
- `setSalary(double salary)` — same rule: if negative, print `Invalid salary` and set it to `0`; otherwise store it.
- `getSalary()` — returns the salary.
- `displayEmployeeDetails()` — prints the name, id, and salary (two decimal places).

**Input format.** Four lines on standard input: `name`, `employeeId`, initial `salary`, then `newSalary`. The provided `Main` constructs the employee, prints `getSalary()`, calls `setSalary(newSalary)`, then `displayEmployeeDetails()`.

**Example 1** — Input: `Sam`, `9656`, `10000`, `15840`

```text
Salary : 10000.00
Name : Sam
Employee Id : 9656
Salary : 15840.00
```

**Example 2** — Input: `Sam`, `9656`, `-1050`, `-9315`

```text
Invalid salary
Salary : 0.00
Invalid salary
Name : Sam
Employee Id : 9656
Salary : 0.00
```

The negative initial salary trips the constructor's guard; the negative `newSalary` trips the setter's.

**Constraints:** valid salaries satisfy 1 ≤ salary ≤ 10⁶ (the negatives above exercise the guard).
````

```java run
import java.util.*;

class Employee {
    // TODO: public String name; protected int employeeId; private double salary;

    public Employee(String name, int employeeId, double salary) {
        // TODO: set name and employeeId; if salary < 0 -> print "Invalid salary", salary = 0; else store it
    }

    public void setSalary(double salary) {
        // TODO: if salary < 0 -> print "Invalid salary", set 0; else store it
    }

    public double getSalary() {
        // TODO: return the salary
        return 0;
    }

    public void displayEmployeeDetails() {
        // TODO: print Name, Employee Id, and Salary (2 decimals)
    }
}

// The driver is complete — implement Employee above.
class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String name = sc.nextLine().trim();
        int employeeId = Integer.parseInt(sc.nextLine().trim());
        double salary = Double.parseDouble(sc.nextLine().trim());
        double newSalary = Double.parseDouble(sc.nextLine().trim());

        Employee emp = new Employee(name, employeeId, salary);
        System.out.printf(Locale.US, "Salary : %.2f\n", emp.getSalary());
        emp.setSalary(newSalary);
        emp.displayEmployeeDetails();
    }
}
```

```testcases
{
  "args": [
    { "id": "name", "label": "Name", "type": "string" },
    { "id": "employeeId", "label": "Employee Id", "type": "int" },
    { "id": "salary", "label": "Salary", "type": "double" },
    { "id": "newSalary", "label": "New Salary", "type": "double" }
  ],
  "cases": [
    { "args": { "name": "Sam", "employeeId": "9656", "salary": "10000", "newSalary": "15840" }, "expected": "Salary : 10000.00\nName : Sam\nEmployee Id : 9656\nSalary : 15840.00" },
    { "args": { "name": "Sam", "employeeId": "9656", "salary": "-1050", "newSalary": "-9315" }, "expected": "Invalid salary\nSalary : 0.00\nInvalid salary\nName : Sam\nEmployee Id : 9656\nSalary : 0.00" }
  ]
}
```

````editorial
The access modifiers encode intent: `name` is `public` (freely readable), `employeeId` is `protected` (subclasses and same-package only), and `salary` is `private` — reachable exclusively through `getSalary` / `setSalary`. That private-ness is what lets the setter *enforce* the "no negative salary" rule; if callers could touch `salary` directly, the invariant couldn't hold. The constructor repeats the same guard so an object can never start in an invalid state.

```java solution
import java.util.*;

class Employee {
    public String name;
    protected int employeeId;
    private double salary;

    public Employee(String name, int employeeId, double salary) {
        this.name = name;
        this.employeeId = employeeId;
        if (salary >= 0) {
            this.salary = salary;
        } else {
            this.salary = 0.0;
            System.out.println("Invalid salary");
        }
    }

    public void setSalary(double salary) {
        if (salary < 0) {
            System.out.println("Invalid salary");
            this.salary = 0.0;
            return;
        }
        this.salary = salary;
    }

    public double getSalary() {
        return this.salary;
    }

    public void displayEmployeeDetails() {
        System.out.println("Name : " + name);
        System.out.println("Employee Id : " + employeeId);
        System.out.printf(Locale.US, "Salary : %.2f\n", salary);
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String name = sc.nextLine().trim();
        int employeeId = Integer.parseInt(sc.nextLine().trim());
        double salary = Double.parseDouble(sc.nextLine().trim());
        double newSalary = Double.parseDouble(sc.nextLine().trim());

        Employee emp = new Employee(name, employeeId, salary);
        System.out.printf(Locale.US, "Salary : %.2f\n", emp.getSalary());
        emp.setSalary(newSalary);
        emp.displayEmployeeDetails();
    }
}
```
````

## Inheritance

Inheritance is a fundamental concept in object-oriented programming (OOP) that allows a class (subclass) to inherit the attributes (fields) and behaviors (methods) of another class (superclass). It is the mechanism that promotes code reuse and establishes a hierarchical relationship between classes.

In Java, this concept allows a subclass to inherit or extend the functionality of a superclass, enabling the subclass to reuse code and, in many cases, modify or add new behavior.

Consider the following example where a super class (parent/base class) `School` has a method `printSchoolName()`, which is inherited by the subclass `Student`. Because of this, the program can call the `printSchoolName()` method from an object of the `Student` class without causing any errors. Find the code snippet below:

```java
import java.util.*;
import java.util.*;

// Parent class or super class
class School {
    // Private attribute for school name
    private String schoolName;

    // Constructor initializes the school name
    School() {
        schoolName = "DPS"; // Default school name
    }

    // Method to print the school name
    void printSchoolName() {
        System.out.println("School name: " + schoolName);
    }
}

// Subclass or child class
class Student extends School {
    // Private attribute for student name
    private String studentName;

    // Constructor initializes the student name
    Student(String name) {
        this.studentName = name;
    }

    // Method to print the student name
    void printStudentName() {
        System.out.println("Student name: " + studentName);
    }
}

// Main class to execute the program
class Main {
    public static void main(String[] args) {
        // Create a new student object with the name "Alex"
        Student student = new Student("Alex");

        // Print the student's name
        student.printStudentName();

        // Print the school's name
        student.printSchoolName();
    }
}
```

### Parent Class

The parent class (also known as the superclass) is the class that provides common properties (attributes) and behaviors (methods) that are shared by one or more subclasses. It serves as a template or blueprint from which other classes (subclasses) can inherit. For example, `School` class.

### Subclass (Child Class)

A subclass (also known as a child class) is a class that inherits from a parent class. The subclass can reuse, extend, or override the attributes and methods of the parent class to specialize or modify the inherited functionality. For example, `Student` class.

In Java, there are three major types of inheritance:

- Single Inheritance
- Multilevel Inheritance
- Hierarchical Inheritance

```mermaid
classDiagram
    Animal <|-- Dog
    Animal <|-- Cat
    Animal <|-- Mammal
    Mammal <|-- Puppy

    class Animal {
        +eat() void
    }
    class Dog {
        +bark() void
    }
    class Cat {
        +meow() void
    }
    class Mammal {
        +walk() void
    }
    class Puppy {
        +bark() void
    }
```

`Animal <|-- Dog` and `Animal <|-- Cat` on their own would each be single inheritance; together, two children off one parent, that's hierarchical. `Animal <|-- Mammal <|-- Puppy` is a chain, one level becoming the next level's parent — that's multilevel.

### Single Inheritance

In Single Inheritance, a child class inherits from one parent class. This is the simplest and most common form of inheritance. Consider the following code snippet:

```java
import java.util.*;
// Parent class
class Animal {
    // Method to represent the eating behavior of an animal
    void eat() {
        System.out.println("This animal eats food.");
    }
}

// Child class inheriting from the Animal class
class Dog extends Animal {
    // Method specific to the Dog class to represent barking behavior
    void bark() {
        System.out.println("This dog barks.");
    }
}

// Main class to execute the program
class Main {
    public static void main(String[] args) {
        // Create an object of the Dog class
        Dog dog = new Dog();

        // Call the eat method inherited from the Animal class
        dog.eat();  // Output: This animal eats food.

        // Call the bark method defined in the Dog class
        dog.bark(); // Output: This dog barks.
    }
}
```

**Keypoints:**

- In a single inheritance, a one-to-one relationship is established.
- The child class inherits methods and properties from a single parent class.

### Multilevel Inheritance

In Multilevel Inheritance, a class derives from a child class, creating a chain of inheritance. Here, the child class of one level becomes the parent class for the next level. Consider the code snippet below:

```java
import java.util.*;
// Parent class representing general animals
class Animal {
    // Method to define the eating behavior of animals
    void eat() {
        System.out.println("This animal eats food.");
    }
}

// Intermediate class representing mammals, inheriting from Animal
class Mammal extends Animal {
    // Method to define the walking behavior of mammals
    void walk() {
        System.out.println("This mammal walks.");
    }
}

// Subclass representing dogs, inheriting from Mammal
class Dog extends Mammal {
    // Method to define the barking behavior specific to dogs
    void bark() {
        System.out.println("This dog barks.");
    }
}

// Main class to demonstrate multilevel inheritance
class Main {
    public static void main(String[] args) {
        // Create an object of the Dog class
        Dog dog = new Dog();

        // Call the eat method inherited from the Animal class
        dog.eat(); // Output: This animal eats food.

        // Call the walk method inherited from the Mammal class
        dog.walk(); // Output: This mammal walks.

        // Call the bark method defined in the Dog class
        dog.bark(); // Output: This dog barks.
    }
}
```

**Keypoints:**

- In a multilevel inheritance, a one-to-one-to-one relationship across multiple levels is established.
- Each child class inherits from its immediate parent, and the chain continues.

### Hierarchical Inheritance

In Hierarchical Inheritance, multiple child classes inherit from a single parent class. Consider the code snippet below:

```java
import java.util.*;
// Parent class representing general animals
class Animal {
    // Method to define the eating behavior common to all animals
    void eat() {
        System.out.println("This animal eats food.");
    }
}

// Subclass representing dogs, inheriting from Animal
class Dog extends Animal {
    // Method to define the barking behavior specific to dogs
    void bark() {
        System.out.println("This dog barks.");
    }
}

// Subclass representing cats, inheriting from Animal
class Cat extends Animal {
    // Method to define the meowing behavior specific to cats
    void meow() {
        System.out.println("This cat meows.");
    }
}

// Main class to demonstrate hierarchical inheritance
class Main {
    public static void main(String[] args) {
        // Create an object of the Dog class
        Dog dog = new Dog();

        // Create an object of the Cat class
        Cat cat = new Cat();

        // Call the eat method inherited from the Animal class using the Dog object
        dog.eat(); // Output: This animal eats food.

        // Call the bark method specific to the Dog class
        dog.bark(); // Output: This dog barks.

        // Call the eat method inherited from the Animal class using the Cat object
        cat.eat(); // Output: This animal eats food.

        // Call the meow method specific to the Cat class
        cat.meow(); // Output: This cat meows.
    }
}
```

**Keypoints:**

- In a hierarchical inheritance, a one-to-many relationship is established between classes.
- The child classes share the common methods and properties of the parent class but can also define their unique features.

#### The same idea in Python

Single, multilevel, and hierarchical inheritance translate directly — the shape comes from how the classes derive from one another, not from special syntax per case:

```python
class Animal:
    def eat(self) -> None:
        print("This animal eats food.")


class Mammal(Animal):  # single inheritance: Mammal derives from one parent, Animal
    def walk(self) -> None:
        print("This mammal walks.")


class Dog(Mammal):  # multilevel: Animal -> Mammal -> Dog
    def bark(self) -> None:
        print("This dog barks.")


class Cat(Animal):  # hierarchical: Cat and Mammal are both direct children of Animal
    def meow(self) -> None:
        print("This cat meows.")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    dog = Dog()
    dog.eat()   # inherited from Animal, two levels up
    dog.walk()  # inherited from Mammal, one level up
    dog.bark()  # defined directly on Dog

    cat = Cat()
    cat.eat()   # inherited from Animal, sibling branch to Mammal/Dog
    cat.meow()  # defined directly on Cat
```

### Advantages of Using Inheritance

Inheritance is a cornerstone of object-oriented programming, offering significant benefits such as:

- **Reusability:** It allows you to reuse the code of an existing class in a new class. Instead of rewriting code, the subclass (child class) can inherit the methods and attributes of the parent class. This reduces redundancy and promotes efficient coding.
- **Modularity:** It promotes a modular structure by separating concerns into different classes. Each class focuses on a specific part of the program, improving clarity and manageability.
- **Extensibility:** It enables adding new features or extending existing functionality without modifying the base class. This makes it easy to adapt to changing requirements.
- **Maintainability:** Inheritance makes code easier to maintain by centralizing common features in a parent class. Changes to shared functionality only need to be made in one place, reducing the risk of errors.

Inheritance also touches a few other important concepts, covered next: access modifiers (see [Access Modifiers](#access-modifiers) above), method overriding, and the `super` keyword.

### Method Overriding

Method overriding allows a subclass to provide a specific implementation of a method already defined in its parent class. This supports runtime polymorphism and enables dynamic behavior. There are some key rules for overriding:

- The method must have the same name, parameters, and return type as the parent class.
- The method in the child class cannot have a more restrictive access modifier than the parent method.
- Only inheritable methods (public or protected) can be overridden.
- The `@Override` annotation is recommended for clarity.

### The "super" Keyword

The `super` keyword is used in inheritance to:

- **Access Parent Class Members:** Refer to parent class methods or variables when they are shadowed by child class members.
- **Invoke Parent Class Constructor:** Call the parent class constructor to initialize the inherited state.

### Difference between Method Overloading and Method Overriding

**Definition:**

- Method Overloading occurs when two or more methods in the same class have the same name but different parameter lists (number, type, or order of parameters).
- Method Overriding occurs when a subclass provides a specific implementation of a method already defined in its parent class.

**Inheritance Dependency:**

- Method Overloading does not require inheritance. It happens within the same class.
- Method Overriding requires inheritance; occurs between a parent class and its subclass.

**Parameters:**

- In Method Overloading, methods must have different parameter lists (number, type, or order).
- In Method Overriding, the method must have the same parameter list as the method in the parent class.

**Access Modifiers:**

- In Method Overloading, methods can have any access modifier; no restrictions.
- The access modifier in the overriding method cannot be more restrictive than in the parent class.

### Multiple Inheritance

Along with the three types of inheritances discussed above, there is another type of inheritance — Multiple Inheritance.

Multiple inheritance refers to a feature in object-oriented programming where a class can inherit properties and methods from more than one parent class. This allows the child class to combine the functionality of multiple parent classes.

**Diamond Problem:** Diamond Problem occurs when a class inherits from two classes that have methods with the same name. The compiler cannot determine which method to execute.

If both `B` and `C` inherit from `A` and override a method, and `D` inherits from both `B` and `C`, which version of the method should `D` inherit? This ambiguity is why Java restricts multiple inheritance for classes.

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** Java does not allow multiple inheritance using classes to avoid the diamond problem — it allows multiple inheritance through interfaces, as interfaces only declare method signatures (no method bodies initially), thus preventing conflicts.

</div>

### Your Turn — Practice: Inheritance

Build a small hierarchy — a base `Employee`, with `Manager` and `Engineer` deriving from it — where each subclass overrides `displayDetails()` but reuses the parent's version via `super`.

````problem
Implement a base class `Employee` and two derived classes, `Manager` and `Engineer`. Each subclass calls the parent constructor with `super(...)` and extends the parent's `displayDetails()` rather than rewriting it.

**Base class `Employee`**

- Attributes: `name` (`String`), `id` (`int`).
- `displayDetails()` — prints the name and id.

**`Manager extends Employee`**

- Adds `teamSize` (`int`).
- `displayDetails()` — calls `super.displayDetails()`, then prints the team size.

**`Engineer extends Employee`**

- Adds `specialization` (`String`).
- `displayDetails()` — calls `super.displayDetails()`, then prints the specialization.

**Input format.** Six lines on standard input: `M_name`, `M_id`, `M_teamSize`, then `E_name`, `E_id`, `E_specialization`. The provided `Main` builds a `Manager` and an `Engineer`, printing a header before each (and a blank line between them — you don't add it yourself).

**Example 1**

```text
Manager  : Jax, 101, 8
Engineer : William, 202, Backend Developer
```

Output:

```text
Manager Details
Name : Jax
Id : 101
Team Size : 8

Engineer Details
Name : William
Id : 202
Specialization : Backend Developer
```

**Constraints:** 1 ≤ id ≤ 10⁵ · 1 ≤ teamSize ≤ 10⁵
````

```java run
import java.util.*;

class Employee {
    // TODO: protected String name; protected int id;

    public Employee(String name, int id) {
        // TODO: initialise name and id
    }

    public void displayDetails() {
        // TODO: print "Name : <name>" and "Id : <id>"
    }
}

class Manager extends Employee {
    // TODO: private int teamSize;

    public Manager(String name, int id, int teamSize) {
        super(name, id);
        // TODO: set teamSize
    }

    @Override
    public void displayDetails() {
        // TODO: call super.displayDetails(), then print "Team Size : <teamSize>"
    }
}

class Engineer extends Employee {
    // TODO: private String specialization;

    public Engineer(String name, int id, String specialization) {
        super(name, id);
        // TODO: set specialization
    }

    @Override
    public void displayDetails() {
        // TODO: call super.displayDetails(), then print "Specialization : <specialization>"
    }
}

// The driver is complete — implement the three classes above.
class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String mName = sc.nextLine().trim();
        int mId = Integer.parseInt(sc.nextLine().trim());
        int mTeamSize = Integer.parseInt(sc.nextLine().trim());
        String eName = sc.nextLine().trim();
        int eId = Integer.parseInt(sc.nextLine().trim());
        String eSpecialization = sc.nextLine().trim();

        Manager manager = new Manager(mName, mId, mTeamSize);
        System.out.println("Manager Details");
        manager.displayDetails();

        System.out.println();

        Engineer engineer = new Engineer(eName, eId, eSpecialization);
        System.out.println("Engineer Details");
        engineer.displayDetails();
    }
}
```

```testcases
{
  "args": [
    { "id": "mName", "label": "Manager name", "type": "string" },
    { "id": "mId", "label": "Manager id", "type": "int" },
    { "id": "mTeamSize", "label": "Team size", "type": "int" },
    { "id": "eName", "label": "Engineer name", "type": "string" },
    { "id": "eId", "label": "Engineer id", "type": "int" },
    { "id": "eSpecialization", "label": "Specialization", "type": "string" }
  ],
  "cases": [
    { "args": { "mName": "Jax", "mId": "101", "mTeamSize": "8", "eName": "William", "eId": "202", "eSpecialization": "Backend Developer" }, "expected": "Manager Details\nName : Jax\nId : 101\nTeam Size : 8\n\nEngineer Details\nName : William\nId : 202\nSpecialization : Backend Developer" },
    { "args": { "mName": "Sam", "mId": "10434", "mTeamSize": "50", "eName": "Siddhant", "eId": "41241", "eSpecialization": "Full Stack Developer" }, "expected": "Manager Details\nName : Sam\nId : 10434\nTeam Size : 50\n\nEngineer Details\nName : Siddhant\nId : 41241\nSpecialization : Full Stack Developer" }
  ]
}
```

````editorial
The shared `name`/`id` and their printing live once, in `Employee`. Each subclass adds only its extra field and constructor, delegating the common part with `super(name, id)` and `super.displayDetails()` — so there's no duplicated printing logic. Marking the base fields `protected` is what lets the subclasses reach them; overriding `displayDetails()` while still calling `super` is the classic "extend, don't replace" pattern.

```java solution
import java.util.*;

class Employee {
    protected String name;
    protected int id;

    public Employee(String name, int id) {
        this.name = name;
        this.id = id;
    }

    public void displayDetails() {
        System.out.println("Name : " + name);
        System.out.println("Id : " + id);
    }
}

class Manager extends Employee {
    private int teamSize;

    public Manager(String name, int id, int teamSize) {
        super(name, id);
        this.teamSize = teamSize;
    }

    @Override
    public void displayDetails() {
        super.displayDetails();
        System.out.println("Team Size : " + teamSize);
    }
}

class Engineer extends Employee {
    private String specialization;

    public Engineer(String name, int id, String specialization) {
        super(name, id);
        this.specialization = specialization;
    }

    @Override
    public void displayDetails() {
        super.displayDetails();
        System.out.println("Specialization : " + specialization);
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String mName = sc.nextLine().trim();
        int mId = Integer.parseInt(sc.nextLine().trim());
        int mTeamSize = Integer.parseInt(sc.nextLine().trim());
        String eName = sc.nextLine().trim();
        int eId = Integer.parseInt(sc.nextLine().trim());
        String eSpecialization = sc.nextLine().trim();

        Manager manager = new Manager(mName, mId, mTeamSize);
        System.out.println("Manager Details");
        manager.displayDetails();

        System.out.println();

        Engineer engineer = new Engineer(eName, eId, eSpecialization);
        System.out.println("Engineer Details");
        engineer.displayDetails();
    }
}
```
````

## Polymorphism

Polymorphism is one of the key concepts in object-oriented programming (OOP) and refers to the ability of a single entity (like a method, operator, or object) to behave differently in different contexts. The term "polymorphism" is derived from Greek, meaning "many forms." In programming, it allows the same method or object to perform different tasks depending on the context.

There are two main types of polymorphism in Java:

- Compile-Time Polymorphism (Static Polymorphism)
- Run-Time Polymorphism (Dynamic Polymorphism)

### Compile-Time Polymorphism (Static Polymorphism)

In compile-time polymorphism, the method to be called is resolved at compile time. When we say the method is "resolved" at compile-time, it means that the compiler determines the correct method to invoke based on the method's signature (such as method name, parameters, etc.). It is achieved through method overloading or operator overloading (not supported in Java).

```java
import java.util.*;
// Calculator Class
class Calculator {
    // Method to add two integers
    int add(int a, int b) {
        return a + b;
    }

    // Method to add two decimal values
    double add(double a, double b) {
        return a + b;
    }
}

// Main class
class Main {
    public static void main(String[] args) {
        Calculator calc = new Calculator();

        // Method resolution happens here based on the argument types (int vs double)
        System.out.println(calc.add(5, 3));          // Calls int version
        System.out.println(calc.add(5.5, 3.3));      // Calls double version
    }
}
```

In this case, the compiler determines whether to call `add(int, int)` or `add(double, double)` at compile-time based on the types of arguments passed.

**Keypoints:**

- Determined at compile-time.
- Faster execution since the binding is done early.
- Examples: Method Overloading.

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** The return type cannot be a differentiator for Method Overloading — the compiler resolves which overload to call from the argument list alone, so two methods that differ only in return type are a compile error, not an overload.

</div>

**The same idea in Python**

```python
class Calculator:
    # Python has no method overloading — a later `def add` simply replaces an earlier
    # one, it doesn't add a second signature. Java needs two overloads here because it
    # dispatches on static parameter *type* (int vs double); Python has no static types
    # to dispatch on, so one implementation already covers both callers below. Where the
    # branching genuinely has to depend on argument type, reach for
    # `functools.singledispatch` instead of hand-rolling overload resolution.
    def add(self, a: float, b: float) -> float:
        return a + b


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    calc = Calculator()

    print(calc.add(5, 3))       # ints in -> 8
    print(calc.add(5.5, 3.3))   # floats in -> 8.8
```

### Run-Time Polymorphism (Dynamic Polymorphism)

In run-time polymorphism, the method is resolved during the runtime. It is achieved through method overriding. When we say the method is "resolved" at run-time, it refers to the decision about which method (in the case of method overriding) to call being made at the time the program is actually running. This occurs due to the dynamic method dispatch mechanism, where the JVM decides which method of a subclass to call based on the actual object type (not the reference type) at runtime.

```java
import java.util.*;
// Parent class
class Animal {
    void sound() {
        System.out.println("Animal makes a sound");
    }
}

// Child class
class Dog extends Animal {
    @Override
    void sound() {
        System.out.println("Dog barks");
    }
}


// Main class
class Main {
    public static void main(String[] args) {
        Animal myAnimal = new Dog();  // Animal reference but Dog object

        // Method resolution happens here at runtime based on the object type (Dog)
        myAnimal.sound();  // Calls Dog's sound() method at runtime
    }
}
```

Here, the method to be executed is decided at runtime based on the object type.

**Keypoints:**

- Determined at runtime.
- Slower execution compared to compile-time polymorphism due to late binding.
- Examples: Method Overriding.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** `myAnimal` is declared as `Animal` but actually points to a `Dog` — calling `myAnimal.sound()` still runs `Dog`'s version, because dynamic dispatch resolves the call against the object's actual runtime type, not the type of the reference used to call it.

</div>

**The same idea in Python**

```python
class Animal:
    def sound(self) -> None:
        print("Animal makes a sound")


class Dog(Animal):
    def sound(self) -> None:  # overrides Animal.sound
        print("Dog barks")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    my_animal: Animal = Dog()  # Animal-typed reference, Dog object

    my_animal.sound()  # resolved at runtime against the object's actual type
```

Both flavors of polymorphism can be seen side by side: overloading picks a signature at compile time, overriding picks an implementation at runtime.

```mermaid
classDiagram
    class Calculator {
        +add(int a, int b) int
        +add(double a, double b) double
    }
    class Animal {
        +sound() void
    }
    class Dog {
        +sound() void
    }
    Animal <|-- Dog
```

### Your Turn — Practice: Polymorphism

Overload one method name — `area` — three ways, and let the compiler pick the right version by the number of arguments. This is compile-time polymorphism.

````problem
Design a class `ShapeCalculator` that computes areas using **method overloading** — three methods, all named `area`, distinguished by their parameter lists.

**Methods**

- `area(int radius)` — circle, `π × radius²`.
- `area(int length, int width)` — rectangle, `length × width`.
- `area(int base1, int base2, int height)` — trapezoid, `((base1 + base2) × height) / 2`.

Use `π = 3.14`. Print each area as an integer, **rounded down** (cast to `int`), in the format shown.

**Input format.** Six lines on standard input: `radius`, `length`, `width`, `base1`, `base2`, `height`. The provided `Main` calls `area(radius)`, then `area(length, width)`, then `area(base1, base2, height)`.

**Example 1** — Input: `radius=2`, `length=2`, `width=3`, `base1=2`, `base2=3`, `height=2`

```text
Area of Circle : 12
Area of Rectangle : 6
Area of Trapezoid : 5
```

**Example 2** — Input: `radius=3`, `length=2`, `width=5`, `base1=4`, `base2=3`, `height=5`

```text
Area of Circle : 28
Area of Rectangle : 10
Area of Trapezoid : 17
```

`3.14 × 2² = 12.56`, cast to `int` → `12`; `(2 + 3) × 2 / 2 = 5`.

**Constraints:** 1 ≤ radius, length, width, base1, base2, height ≤ 10⁴
````

```java run
import java.util.*;

class ShapeCalculator {
    // Three overloads of `area` — same name, different parameter lists.

    public void area(int radius) {
        // TODO: circle — 3.14 * radius * radius, cast to int; print "Area of Circle : <n>"
    }

    public void area(int length, int width) {
        // TODO: rectangle — length * width; print "Area of Rectangle : <n>"
    }

    public void area(int base1, int base2, int height) {
        // TODO: trapezoid — 0.5 * (base1 + base2) * height, cast to int; print "Area of Trapezoid : <n>"
    }
}

// The driver is complete — implement the three overloads above.
class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int radius = Integer.parseInt(sc.nextLine().trim());
        int length = Integer.parseInt(sc.nextLine().trim());
        int width = Integer.parseInt(sc.nextLine().trim());
        int base1 = Integer.parseInt(sc.nextLine().trim());
        int base2 = Integer.parseInt(sc.nextLine().trim());
        int height = Integer.parseInt(sc.nextLine().trim());

        ShapeCalculator calc = new ShapeCalculator();
        calc.area(radius);
        calc.area(length, width);
        calc.area(base1, base2, height);
    }
}
```

```testcases
{
  "args": [
    { "id": "radius", "label": "Circle radius", "type": "int" },
    { "id": "length", "label": "Rectangle length", "type": "int" },
    { "id": "width", "label": "Rectangle width", "type": "int" },
    { "id": "base1", "label": "Trapezoid base1", "type": "int" },
    { "id": "base2", "label": "Trapezoid base2", "type": "int" },
    { "id": "height", "label": "Trapezoid height", "type": "int" }
  ],
  "cases": [
    { "args": { "radius": "2", "length": "2", "width": "3", "base1": "2", "base2": "3", "height": "2" }, "expected": "Area of Circle : 12\nArea of Rectangle : 6\nArea of Trapezoid : 5" },
    { "args": { "radius": "3", "length": "2", "width": "5", "base1": "4", "base2": "3", "height": "5" }, "expected": "Area of Circle : 28\nArea of Rectangle : 10\nArea of Trapezoid : 17" }
  ]
}
```

````editorial
All three methods share the name `area`; the compiler chooses which to call purely from the argument count (one, two, or three ints) — that resolution-by-signature is **compile-time (static) polymorphism**. The casts to `int` truncate toward zero, matching the "round down" rule; the trapezoid uses `0.5 * (base1 + base2) * height` in `double` before the cast so the halving isn't lost to integer division.

```java solution
import java.util.*;

class ShapeCalculator {
    public void area(int radius) {
        double ans = 3.14 * radius * radius;
        System.out.println("Area of Circle : " + (int) ans);
    }

    public void area(int length, int width) {
        int ans = length * width;
        System.out.println("Area of Rectangle : " + (int) ans);
    }

    public void area(int base1, int base2, int height) {
        double ans = 0.5 * (base1 + base2) * height;
        System.out.println("Area of Trapezoid : " + (int) ans);
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int radius = Integer.parseInt(sc.nextLine().trim());
        int length = Integer.parseInt(sc.nextLine().trim());
        int width = Integer.parseInt(sc.nextLine().trim());
        int base1 = Integer.parseInt(sc.nextLine().trim());
        int base2 = Integer.parseInt(sc.nextLine().trim());
        int height = Integer.parseInt(sc.nextLine().trim());

        ShapeCalculator calc = new ShapeCalculator();
        calc.area(radius);
        calc.area(length, width);
        calc.area(base1, base2, height);
    }
}
```
````

## Summary

- **Encapsulation** bundles an object's data and behavior together and hides the data behind a controlled public interface (getters/setters), so internal representation can change without breaking callers.
- **Access modifiers** (`public`, `private`, `protected`, default/package-private) are the mechanism Java gives you to enforce that hiding, each with a different visibility scope across class, package, subclass, and world.
- **Inheritance** lets a subclass reuse a superclass's fields and methods, in single, multilevel, or hierarchical shapes — it also introduces method overriding, the `super` keyword, and the constraint that Java disallows multiple inheritance via classes (the diamond problem) while allowing it via interfaces.
- **Polymorphism** lets the same method name behave differently depending on context: compile-time (method overloading, resolved by signature) or run-time (method overriding, resolved by the object's actual type via dynamic dispatch).
