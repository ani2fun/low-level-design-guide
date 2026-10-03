---
title: "Encapsulation, Inheritance & Polymorphism"
summary: "Three object-oriented ideas as design tools. Encapsulation keeps a class's rules in one place, so no caller can break them; access modifiers set how much of a class is its public contract. Inheritance models is-a and reuses code, but inheriting methods that break your rules (java.util.Stack) is worse than composing. Polymorphism replaces type checks with one call that each class answers its own way. The Java language rules live in the Java guide; every example here runs in Java and Python, with verified output."
essential: true
---

# Encapsulation, Inheritance & Polymorphism — OOP as a Design Tool

Every OOP course lists the same four pillars: encapsulation, inheritance, polymorphism and abstraction. Learning their syntax is the easy part. The design question is *when each one helps*, and when it quietly makes a system harder to change.

This lesson looks at the first three as design tools. The fourth, abstraction, is covered in the [next lesson](/synapse/low-level-design/oop/abstraction-interfaces-static-members-inner-classes). The Java language rules (`private`, `extends`, `super`, overriding, overloading) are in the Java guide's [Encapsulation & Access Modifiers](/synapse/programming-languages/java/classes-and-objects/encapsulation-and-access-modifiers) and [Inheritance & Polymorphism](/synapse/programming-languages/java/robust-oop/inheritance-and-polymorphism). This lesson links to those pages instead of repeating them.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- **Encapsulation** keeps a class's rules in the same place as its data, so every change to the data goes through code that checks the rules.
- **Inheritance** expresses "is a" and shares code, but a subclass inherits *every* public method of its parent. If some of those methods would break the subclass's rules, use composition instead: hold the other object in a field.
- **Polymorphism** lets one method call do the right thing for each type of object, so supporting a new type means adding a class, not editing every `switch` statement.

</div>

Every output below was produced by running the code on Java 21 and Python 3.11.

**You'll be able to:** explain what encapsulation protects, and choose the smallest visibility for each member; spot inheritance that exposes methods the subclass should not have, and replace it with composition; replace a `switch` on a type code with polymorphism, and explain what that gains when a new type is added.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the design does to the code that uses it.
2. **A concrete bite** — a specific, runnable program where the design choice produces a bug or prevents one.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [Encapsulation: keep the rules next to the data](#1-encapsulation-keep-the-rules-next-to-the-data)
2. [Inheritance: is-a, and what you inherit](#2-inheritance-is-a-and-what-you-inherit)
3. [Polymorphism: one call, many behaviours](#3-polymorphism-one-call-many-behaviours)
4. [Mental-model summary](#4-mental-model-summary)
5. [Gotcha checklist](#5-gotcha-checklist)
6. [Check yourself](#-check-yourself)
7. [Sources](#-sources)

---

## 1. Encapsulation: keep the rules next to the data

A bank account has one rule: the balance never goes below zero. Here the balance is a public field:

```java run
// ⚠️ ANTI-PATTERN — the balance is a public field. Do not copy it.
class BankAccount {
    public long balance;  // anyone can write anything here
}

public class Main {
    public static void main(String[] args) {
        BankAccount account = new BankAccount();
        account.balance = 100;
        account.balance -= 250;  // a withdrawal that nobody checked
        System.out.println("balance = " + account.balance);
    }
}
```

```python run
# ⚠️ ANTI-PATTERN — the balance is a plain public attribute. Do not copy it.
class BankAccount:
    def __init__(self) -> None:
        self.balance = 0  # anyone can write anything here


account = BankAccount()
account.balance = 100
account.balance -= 250  # a withdrawal that nobody checked
print("balance =", account.balance)
```

**Output:**
```
balance = -150
```

**Analysis.** Nothing stopped the overdraft. The rule "no negative balance" exists only in the memory of each programmer who writes code that uses the account, and every one of them must remember it. With a hundred places in the code that change the balance, one will forget.

**Encapsulation** makes the field private, and offers methods that enforce the rule:

```java run
class BankAccount {
    private long balance;  // only this class can touch it

    void deposit(long amount) {
        if (amount <= 0) throw new IllegalArgumentException("deposit must be positive");
        balance += amount;
    }

    boolean withdraw(long amount) {
        if (amount <= 0 || amount > balance) return false;  // the rule lives here, once
        balance -= amount;
        return true;
    }

    long balance() {
        return balance;
    }
}

public class Main {
    public static void main(String[] args) {
        BankAccount account = new BankAccount();
        account.deposit(100);
        System.out.println("withdraw 250: " + account.withdraw(250));
        System.out.println("withdraw 40:  " + account.withdraw(40));
        System.out.println("balance = " + account.balance());
    }
}
```

```python run
class BankAccount:
    def __init__(self) -> None:
        self._balance = 0  # leading underscore: "internal, don't touch"

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def withdraw(self, amount: int) -> bool:
        if amount <= 0 or amount > self._balance:  # the rule lives here, once
            return False
        self._balance -= amount
        return True

    @property
    def balance(self) -> int:  # read-only from outside
        return self._balance


account = BankAccount()
account.deposit(100)
print("withdraw 250:", account.withdraw(250))
print("withdraw 40: ", account.withdraw(40))
print("balance =", account.balance)
```

**Output** *(Java; Python prints `False` and `True`)*:
```
withdraw 250: false
withdraw 40:  true
balance = 60
```

**Analysis.** The overdraft was refused, and the valid withdrawal went through. The rule now lives in exactly one place, `withdraw`, and no other code can get around it: the Java compiler rejects any access to `balance` from outside the class. Python has no `private` keyword. Instead, a leading underscore is a convention that means "internal, don't touch", and a read-only `@property` lets callers read the value without being able to set it.

**Intuition.**
*Mechanism.* A class's **invariants** are the rules that must be true for every object of that class at all times: a balance is never negative, an order's total equals the sum of its lines. With encapsulation, the class is the only code that can change its own state, so it is the only code that has to enforce those rules.

*Concrete bite.* Adding a getter and a setter for every field (`getBalance()`, `setBalance()`) is not encapsulation. `setBalance(-150)` breaks the rule just as the public field did. Offer methods that mean something in the business (`deposit`, `withdraw`), not setters for raw fields.

**Access modifiers** decide which parts of a class other code may use, and so which parts are the class's promise to the outside world:

| Java modifier | Visible to | Use it for |
|---|---|---|
| `private` | the class itself | all fields; helper methods |
| *(none)*, package-private | classes in the same package | collaborators that work closely together |
| `protected` | the package, plus subclasses | hooks meant for subclasses |
| `public` | everyone | the contract: what callers may rely on |

Everything public is a promise: changing it can break code you don't know about. The Java guide's [Encapsulation & Access Modifiers](/synapse/programming-languages/java/classes-and-objects/encapsulation-and-access-modifiers) covers the language rules <abbr title="The Java Language Specification, Java SE 21, §6.6 Access Control">[1]</abbr>.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Make every field private. Give the class methods named after what happens in the business, and let each one check the rules. Make each method only as visible as the code that calls it needs.

The cost is writing methods instead of exposing data directly. The benefit is that each rule is enforced in one place, and you can change how the data is stored (whole cents instead of a `double`, say) without changing any code that uses the class.

</div>

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

---

## 2. Inheritance: is-a, and what you inherit

**Inheritance** lets a subclass reuse its parent's code, and lets it be used anywhere the parent is expected. It models an **is-a** relationship: a `Manager` is an `Employee`. The catch is that a subclass inherits *all* of its parent's public methods, whether or not they make sense for it.

Java's own `java.util.Stack` class shows the problem. It extends `Vector`, which is a list:

```java run
// ⚠️ ANTI-PATTERN — java.util.Stack inherits every Vector method. Do not copy it.
import java.util.Stack;

public class Main {
    public static void main(String[] args) {
        Stack<String> undo = new Stack<>();  // java.util.Stack extends Vector
        undo.push("type 'a'");
        undo.push("type 'b'");
        undo.add(0, "delete line");          // inherited from Vector: inserts at the BOTTOM
        undo.push("type 'c'");

        System.out.println("pop: " + undo.pop());
        System.out.println("get(0): " + undo.get(0) + "   <- a stack should not allow this");
        System.out.println("whole stack: " + undo);
    }
}
```

```python run
# ⚠️ ANTI-PATTERN — a stack that inherits every list method. Do not copy it.
class Stack(list):
    def push(self, item: str) -> None:
        self.append(item)


undo = Stack()
undo.push("type 'a'")
undo.push("type 'b'")
undo.insert(0, "delete line")  # inherited from list: inserts at the BOTTOM
undo.push("type 'c'")

print("pop:", undo.pop())
print("undo[0]:", undo[0], "  <- a stack should not allow this")
print("whole stack:", undo)
```

**Output** *(Java; Python prints the same with `undo[0]` and quotes around the items)*:
```
pop: type 'c'
get(0): delete line   <- a stack should not allow this
whole stack: [delete line, type 'a', type 'b']
```

**Analysis.** A stack should only let you add and remove items at the top. Because `Stack` *is a* `Vector`, it also has `add(index, …)`, `get(index)` and every other list method. The "delete line" action was inserted at the bottom, so the undo history is no longer in the order things actually happened. The `Stack` documentation itself recommends `Deque` instead <abbr title="Java SE 21 API, java.util.Stack">[2]</abbr>.

**Composition** gives a class only the methods it should have. Here the stack *has* a deque as a private field, and offers only push and pop:

```java run
import java.util.ArrayDeque;
import java.util.Deque;

// Composition: the stack HAS a deque and exposes only stack operations.
class UndoStack {
    private final Deque<String> actions = new ArrayDeque<>();

    void push(String action) { actions.push(action); }
    String pop() { return actions.pop(); }
    boolean isEmpty() { return actions.isEmpty(); }
}

public class Main {
    public static void main(String[] args) {
        UndoStack undo = new UndoStack();
        undo.push("type 'a'");
        undo.push("type 'b'");
        // undo.add(0, "delete line");  // does not compile: UndoStack has no add()
        while (!undo.isEmpty()) System.out.println("undo " + undo.pop());
    }
}
```

```python run
from collections import deque


# Composition: the stack HAS a deque and exposes only stack operations.
class UndoStack:
    def __init__(self) -> None:
        self._actions: deque[str] = deque()

    def push(self, action: str) -> None:
        self._actions.append(action)

    def pop(self) -> str:
        return self._actions.pop()

    def is_empty(self) -> bool:
        return not self._actions


undo = UndoStack()
undo.push("type 'a'")
undo.push("type 'b'")
# undo.insert(0, "delete line")  # AttributeError: UndoStack has no insert()
while not undo.is_empty():
    print("undo", undo.pop())
```

**Output:**
```
undo type 'b'
undo type 'a'
```

**Intuition.**
*Mechanism.* Inheritance ties the subclass to its parent's entire public interface, and to how the parent is implemented. Composition ties a class only to the methods it chooses to call. "Favor object composition over class inheritance" has been standard design advice since 1994 <abbr title="Gamma, Helm, Johnson and Vlissides, Design Patterns, 1994">[3]</abbr>, and Bloch makes the same case with Java examples <abbr title="Joshua Bloch, Effective Java, 3rd ed., 2018, Item 18">[4]</abbr>.

*Concrete bite.* The test for good inheritance is substitution: everything that is true of the parent must stay true of the subclass. This is the Liskov Substitution Principle from the [SOLID chapter](/synapse/low-level-design/solid-principles/solid-principles). Any code that receives a `Stack` as a `Vector` can treat it as a list, and so can break its stack behaviour, as the example showed.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use inheritance only when the subclass truly *is a* kind of its parent, everywhere the parent is used, and needs all of the parent's public methods. Otherwise use composition: hold the other object in a private field, and offer only the methods you intend to. [Relationships and Object Behaviour](/synapse/low-level-design/oop/relationships-and-object-behaviour) covers composition in depth.

The cost of composition is writing small methods that pass calls on to the inner object. The cost of the wrong inheritance is a set of public methods you can never take back.

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

---

## 3. Polymorphism: one call, many behaviours

A ride app prices each vehicle type differently. The first version chooses the pricing rule with a `switch` on a type code, a string that names the vehicle type:

```java run
// ⚠️ ANTI-PATTERN — behaviour chosen by a type code. Do not copy it.
public class Main {
    static double fare(String vehicle, double km) {
        switch (vehicle) {
            case "BIKE": return 10 + 5 * km;
            case "CAR":  return 30 + 12 * km;
            default:     return 0;  // a new vehicle type silently costs nothing
        }
    }

    public static void main(String[] args) {
        System.out.println("BIKE, 10 km: " + fare("BIKE", 10));
        System.out.println("CAR, 10 km:  " + fare("CAR", 10));
        System.out.println("AUTO, 10 km: " + fare("AUTO", 10) + "   <- added to the app, forgotten here");
    }
}
```

```python run
# ⚠️ ANTI-PATTERN — behaviour chosen by a type code. Do not copy it.
def fare(vehicle: str, km: float) -> float:
    if vehicle == "BIKE":
        return 10 + 5 * km
    if vehicle == "CAR":
        return 30 + 12 * km
    return 0  # a new vehicle type silently costs nothing


print("BIKE, 10 km:", fare("BIKE", 10))
print("CAR, 10 km: ", fare("CAR", 10))
print("AUTO, 10 km:", fare("AUTO", 10), "  <- added to the app, forgotten here")
```

**Output** *(Java; Python prints whole numbers)*:
```
BIKE, 10 km: 60.0
CAR, 10 km:  150.0
AUTO, 10 km: 0.0   <- added to the app, forgotten here
```

**Analysis.** When the `AUTO` type was added to the app, this `switch` was forgotten, so auto-rickshaw rides became free. Every place in the code that switches on the vehicle type (fares, icons, seat counts, insurance) must be found and edited for each new type.

**Polymorphism** moves each rule into the class for its type. The caller makes one method call, and each object responds in its own way:

```java run
import java.util.List;

// Each vehicle type knows its own fare rule.
interface Vehicle {
    String name();
    double fare(double km);
}

record Bike() implements Vehicle {
    public String name() { return "BIKE"; }
    public double fare(double km) { return 10 + 5 * km; }
}

record Car() implements Vehicle {
    public String name() { return "CAR"; }
    public double fare(double km) { return 30 + 12 * km; }
}

// Adding a type means adding a class; no existing code changes,
// and the compiler refuses an Auto that forgets fare().
record Auto() implements Vehicle {
    public String name() { return "AUTO"; }
    public double fare(double km) { return 20 + 8 * km; }
}

public class Main {
    public static void main(String[] args) {
        for (Vehicle v : List.of(new Bike(), new Car(), new Auto())) {
            System.out.println(v.name() + ", 10 km: " + v.fare(10));  // one call, many behaviours
        }
    }
}
```

```python run
from abc import ABC, abstractmethod


# Each vehicle type knows its own fare rule.
class Vehicle(ABC):
    name = ""

    @abstractmethod
    def fare(self, km: float) -> float: ...


class Bike(Vehicle):
    name = "BIKE"

    def fare(self, km: float) -> float:
        return 10 + 5 * km


class Car(Vehicle):
    name = "CAR"

    def fare(self, km: float) -> float:
        return 30 + 12 * km


# Adding a type means adding a class; no existing code changes,
# and Python refuses to instantiate an Auto that forgets fare().
class Auto(Vehicle):
    name = "AUTO"

    def fare(self, km: float) -> float:
        return 20 + 8 * km


for v in (Bike(), Car(), Auto()):
    print(f"{v.name}, 10 km: {v.fare(10)}")  # one call, many behaviours
```

**Output** *(Java; Python prints whole numbers)*:
```
BIKE, 10 km: 60.0
CAR, 10 km: 150.0
AUTO, 10 km: 100.0
```

**Analysis.** `v.fare(10)` ran a different method for each vehicle. Adding `Auto` meant adding one class, and no existing code changed. Forgetting to write `fare()` no longer gives a silent `0` either: Java won't compile an `Auto` class without it, and Python won't create an `Auto` object without it.

**Intuition.**
*Mechanism.* With **runtime polymorphism**, the method that runs is chosen by the class of the actual object, not by the type the variable was declared with <abbr title="The Java Language Specification, Java SE 21, §15.12.4.4">[5]</abbr>. Overloading, where several methods share a name but take different parameters, is resolved by the compiler. It is a naming convenience, not a design tool. The Java guide's [Inheritance & Polymorphism](/synapse/programming-languages/java/robust-oop/inheritance-and-polymorphism) covers both.

*Concrete bite.* This is the Open/Closed Principle from the [SOLID chapter](/synapse/low-level-design/solid-principles/solid-principles): the code is open to new vehicle types, but the existing pricing code doesn't need to change. It is also a small example of the Strategy pattern.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** When the same `switch` or `if` chain on a type code appears in more than one place, move each branch into its own class, behind a shared interface.

The cost is more classes, and one more step to follow when reading the code. For a single `switch` over a fixed set of types that will never grow, a `switch` is simpler. In Java, a `sealed` interface combined with a `switch` over its types makes the compiler check that every type is handled.

</div>

---

## 4. Mental-model summary

| Principle | Consequence |
|---|---|
| Encapsulation: private state, and methods that check the rules | Each rule is enforced in one place, and no other code can break it |
| A setter for every field is not encapsulation | Offer business methods (`withdraw`), not raw setters |
| Everything public is a promise | Make each member only as visible as the code that uses it needs |
| A subclass inherits every public method | It can end up offering methods that break its own rules (`Stack.add(0, …)`) |
| Composition offers only the methods you choose | Prefer it, unless the subclass truly is a kind of its parent everywhere |
| Runtime polymorphism picks the method by the object's class | One call, many behaviours; a new type is just a new class |
| The same type-code `switch` in many places | Every new type means finding and editing each one |

## 5. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

| Symptom | Likely cause | Fix |
|---|---|---|
| Objects end up in impossible states (negative stock, empty names) | public fields or raw setters | private fields; operations that check the rules |
| A rule is checked in some callers but not others | the rule lives outside the class | move it into the class's operations |
| A subclass has methods that make no sense for it | inheritance used only for code reuse | composition: hold the other object, forward what you need |
| Code that takes the parent type breaks with the subclass | the subclass is not substitutable (LSP) | change the hierarchy, or compose |
| A new type silently gets default behaviour | a type-code `switch` was missed | polymorphism, or a `sealed` type with an exhaustive `switch` |
| The same `switch` appears in five classes | behaviour keyed on a type code | one method per behaviour, on each type |

</div>

---

## ✅ Check yourself

One check per objective. Answer before you open anything.

```quiz
{"prompt": "A Product class has a private stock field with a public setStock(int) setter. Is the rule 'stock never negative' protected?", "options": ["No: setStock(-5) breaks it unless the setter checks", "Yes: the field is private", "Yes: Java forbids negative ints in fields"], "answer": "No: setStock(-5) breaks it unless the setter checks"}
```

```quiz
{"prompt": "A Playlist extends ArrayList<Song> so it can reuse add and remove. What is the design risk?", "options": ["Callers also get every other list method, such as add(index, song) and clear()", "Playlist cannot be instantiated", "None: inheriting from a library class is always safe"], "answer": "Callers also get every other list method, such as add(index, song) and clear()"}
```

```quiz
{"prompt": "Four classes each switch on vehicle type. A new type, TRUCK, is added. With polymorphism instead, what changes?", "options": ["Only a new Truck class is written", "All four switches still need a new case", "Every existing vehicle class must change"], "answer": "Only a new Truck class is written"}
```

<details>
<summary>An <code>Order</code> has a list of lines and a <code>total</code> field that must always equal the sum of the lines. How would you encapsulate it?</summary>

Make both fields private. Offer `addLine(...)` and `removeLine(...)` methods that update `total` in the same step. Or drop the field and compute `total()` from the lines whenever it is asked for, so there is no second copy of the information to keep in sync. Don't hand out the list itself; return a read-only view or a copy, or other code could add lines without updating the total.

</details>

---

## 📚 Sources

1. *The Java Language Specification, Java SE 21*, §6.6 "Access Control" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-6.html#jls-6.6>
2. `java.util.Stack`, Java SE 21 API ("A more complete and consistent set of LIFO stack operations is provided by the Deque interface") — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Stack.html>
3. Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software* (Addison-Wesley, 1994), ch. 1.
4. Joshua Bloch, *Effective Java*, 3rd ed. (Addison-Wesley, 2018), Item 18, "Favor composition over inheritance".
5. *The Java Language Specification, Java SE 21*, §15.12.4.4 "Locate Method to Invoke" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.12.4.4>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.**

1. In the §1 encapsulated account, call `withdraw(-50)`. Predict the result and the balance.
2. In the §2 composed `UndoStack`, uncomment the `add(0, …)` line. Predict what happens in Java and in Python.
3. In §3, add a `Truck` with `fare = 50 + 15 * km` to the polymorphic version. Predict the line it prints, and which other classes you had to change.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
