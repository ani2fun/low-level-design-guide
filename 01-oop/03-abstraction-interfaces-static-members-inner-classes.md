---
title: "Abstraction & Interfaces"
summary: "Abstraction as a design tool: depend on what something does, not how it does it. An interface is a contract that lets a service swap email for SMS, or for a test fake, without changing a line; an abstract class fixes the steps and lets subclasses fill in the parts that vary (the template method). When to choose which, why static state and static calls make code hard to change and test, and where nested classes fit. The Java language rules live in the Java guide; every example here runs in Java and Python, with verified output."
essential: true
---

# Abstraction & Interfaces — Depending on What, Not How

An order service must tell customers when their order is confirmed. Today it does that by email. Next quarter it must also send an SMS, and in tests it should send nothing at all. If the service creates an `EmailSender` itself, each of those changes means editing the service. If it depends only on "something that can send a notification", none of them do.

That is **abstraction** used as a design tool: give a name to what another object *does*, hide *how* it does it, and let the rest of the system depend only on the name. This lesson covers the two ways to express that, interfaces and abstract classes, and the costs of `static`. The Java language rules (declaring interfaces, `abstract`, default methods, nested classes) are in the Java guide's [Abstract Classes & Interfaces](/synapse/programming-languages/java/robust-oop/abstract-classes-and-interfaces), [static vs Instance](/synapse/programming-languages/java/classes-and-objects/static-vs-instance) and [Nested & Anonymous Classes; Lambdas](/synapse/programming-languages/java/robust-oop/nested-and-anonymous-classes-and-lambdas).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- An **interface** is a contract: it lists what an object can do. Code that depends on an interface works with any class that implements it, including a fake one used in tests.
- An **abstract class** holds the structure its subclasses share, and lets each subclass fill in the parts that differ.
- `static` fields and calls to `static` methods are dependencies fixed in the code: easy to write, but hard to replace or test.

</div>

This builds on [Encapsulation, Inheritance & Polymorphism](/synapse/low-level-design/oop/encapsulation-access-modifiers-inheritance-polymorphism). Every output below was produced by running the code on Java 21 and Python 3.11.

**You'll be able to:** design a class that depends on an interface, and switch to a different implementation (including a test fake) without changing the class; choose between an interface and an abstract class; recognise when `static` state or a static call is a hidden dependency.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the design does to the code that uses it.
2. **A concrete bite** — a specific situation where the design choice pays off or hurts.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [Interfaces: program to a contract](#1-interfaces-program-to-a-contract)
2. [Abstract classes: shared steps, varying parts](#2-abstract-classes-shared-steps-varying-parts)
3. [Interface or abstract class?](#3-interface-or-abstract-class)
4. [`static` and nested classes in design](#4-static-and-nested-classes-in-design)
5. [Mental-model summary](#5-mental-model-summary)
6. [Gotcha checklist](#6-gotcha-checklist)
7. [Check yourself](#-check-yourself)
8. [Sources](#-sources)

---

## 1. Interfaces: program to a contract

Here the order service depends on a `Notifier` interface, and receives an object that implements it through its constructor:

```java run
import java.util.ArrayList;
import java.util.List;

// The contract: what the rest of the system relies on.
interface Notifier {
    void send(String to, String message);
}

class EmailNotifier implements Notifier {
    public void send(String to, String message) {
        System.out.println("EMAIL to " + to + ": " + message);
    }
}

class SmsNotifier implements Notifier {
    public void send(String to, String message) {
        System.out.println("SMS to " + to + ": " + message);
    }
}

// A fake for tests: records instead of sending.
class RecordingNotifier implements Notifier {
    final List<String> sent = new ArrayList<>();

    public void send(String to, String message) {
        sent.add(to + "|" + message);
    }
}

// Depends only on the contract, never on a concrete channel.
class OrderService {
    private final Notifier notifier;

    OrderService(Notifier notifier) {
        this.notifier = notifier;
    }

    void placeOrder(String customer, int orderId) {
        notifier.send(customer, "order #" + orderId + " confirmed");
    }
}

public class Main {
    public static void main(String[] args) {
        new OrderService(new EmailNotifier()).placeOrder("ada@example.com", 42);
        new OrderService(new SmsNotifier()).placeOrder("+44 7700 900123", 43);

        RecordingNotifier fake = new RecordingNotifier();
        new OrderService(fake).placeOrder("test-user", 44);
        System.out.println("test saw: " + fake.sent);
    }
}
```

```python run
from typing import Protocol


# The contract: what the rest of the system relies on.
class Notifier(Protocol):
    def send(self, to: str, message: str) -> None: ...


class EmailNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"EMAIL to {to}: {message}")


class SmsNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"SMS to {to}: {message}")


# A fake for tests: records instead of sending.
class RecordingNotifier:
    def __init__(self) -> None:
        self.sent: list[str] = []

    def send(self, to: str, message: str) -> None:
        self.sent.append(f"{to}|{message}")


# Depends only on the contract, never on a concrete channel.
class OrderService:
    def __init__(self, notifier: Notifier) -> None:
        self._notifier = notifier

    def place_order(self, customer: str, order_id: int) -> None:
        self._notifier.send(customer, f"order #{order_id} confirmed")


OrderService(EmailNotifier()).place_order("ada@example.com", 42)
OrderService(SmsNotifier()).place_order("+44 7700 900123", 43)

fake = RecordingNotifier()
OrderService(fake).place_order("test-user", 44)
print("test saw:", fake.sent)
```

**Output** *(Java; Python prints the list with quotes)*:
```
EMAIL to ada@example.com: order #42 confirmed
SMS to +44 7700 900123: order #43 confirmed
test saw: [test-user|order #44 confirmed]
```

**Analysis.** The same `OrderService`, unchanged, sent an email, then an SMS, and the third time sent nothing at all. The `RecordingNotifier` only stored the message, so a test can check exactly what would have been sent, without needing a mail server. In Python, a `Protocol` describes the contract, and any class with a matching `send` method satisfies it, without having to inherit from it <abbr title="Python 3 documentation, typing.Protocol">[4]</abbr>.

**Intuition.**
*Mechanism.* `OrderService` mentions only the interface. Which class actually sends the message is decided by the code that creates the service. That is called **dependency injection**, and it is covered in [Dependency Injection & Error Handling](/synapse/low-level-design/best-practices/dependency-injection-and-error-handling). It is also the D of [SOLID](/synapse/low-level-design/solid-principles/solid-principles): depend on abstractions, not on concrete classes. "Program to an interface, not an implementation" is one of the oldest rules of object-oriented design <abbr title="Gamma, Helm, Johnson and Vlissides, Design Patterns, 1994, ch. 1">[1]</abbr>.

*Concrete bite.* If `placeOrder` contained `new EmailNotifier()`, every test of placing an order would send a real email, or would need a mocking library to intercept it. Adding SMS would mean editing `OrderService`, a class whose job is orders, not messaging.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** When a class uses something that may change, or that is slow, external or awkward to use in tests (payment gateways, message senders, clocks, storage), make the class depend on an interface, and pass in the implementation from outside.

The cost is one more type and one more constructor parameter. Don't add an interface for a class that has only one implementation and no reason to be replaced. Create the interface when a second implementation, or the first test, needs it.

</div>

### Your Turn — Practice: Interfaces

One `PaymentGateway` contract, two implementations. The driver processes each payment through the interface type without caring which concrete class it is — that's the point of programming to an interface.

````problem
Design an interface `PaymentGateway` with a single method, and two classes that implement it differently.

**Interface `PaymentGateway`**

- `processPayment(double amount)`.

**Implementations**

- `CreditCardPayment` — prints `Processing credit card payment of <amount>`.
- `UPIPayment` — prints `Processing UPI payment of <amount>`.

Print each amount to **two decimal places**.

**Input format.** Two lines on standard input: a comma-separated list of methods (`credit` or `upi`), and a comma-separated list of amounts (positionally matched). The provided `Main` picks the right implementation per method and calls `processPayment`, with a blank line between payments.

**Example 1** — methods `credit, upi` · amounts `284.5, 27476.2`

```text
Processing credit card payment of 284.50

Processing UPI payment of 27476.20
```
````

```java run
import java.util.*;

interface PaymentGateway {
    void processPayment(double amount);
}

class CreditCardPayment implements PaymentGateway {
    @Override
    public void processPayment(double amount) {
        // TODO: print "Processing credit card payment of <amount>" (2 decimals)
    }
}

class UPIPayment implements PaymentGateway {
    @Override
    public void processPayment(double amount) {
        // TODO: print "Processing UPI payment of <amount>" (2 decimals)
    }
}

// The driver parses stdin and dispatches by method — implement the two classes above.
class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String[] methods = sc.nextLine().split(",");
        String[] amounts = sc.nextLine().split(",");

        boolean first = true;
        for (int i = 0; i < methods.length; i++) {
            String m = methods[i].trim();
            PaymentGateway gateway;
            if (m.equals("credit")) gateway = new CreditCardPayment();
            else if (m.equals("upi")) gateway = new UPIPayment();
            else continue;
            if (!first) System.out.println();
            first = false;
            gateway.processPayment(Double.parseDouble(amounts[i].trim()));
        }
    }
}
```

```testcases
{
  "args": [
    { "id": "methods", "label": "Methods (comma-separated)", "type": "string" },
    { "id": "amounts", "label": "Amounts (comma-separated)", "type": "string" }
  ],
  "cases": [
    { "args": { "methods": "credit,upi", "amounts": "284.5,27476.2" }, "expected": "Processing credit card payment of 284.50\n\nProcessing UPI payment of 27476.20" },
    { "args": { "methods": "upi,credit", "amounts": "100,50" }, "expected": "Processing UPI payment of 100.00\n\nProcessing credit card payment of 50.00" }
  ]
}
```

````editorial
`PaymentGateway` is a pure contract — a method signature and nothing else. `CreditCardPayment` and `UPIPayment` each `implement` it their own way, and the driver holds every payment as a `PaymentGateway`, so adding a third method (say `WalletPayment`) later would need zero changes to the loop. `Locale.US` keeps the decimal separator a dot regardless of the machine's locale.

```java solution
import java.util.*;

interface PaymentGateway {
    void processPayment(double amount);
}

class CreditCardPayment implements PaymentGateway {
    @Override
    public void processPayment(double amount) {
        System.out.printf(Locale.US, "Processing credit card payment of %.2f\n", amount);
    }
}

class UPIPayment implements PaymentGateway {
    @Override
    public void processPayment(double amount) {
        System.out.printf(Locale.US, "Processing UPI payment of %.2f\n", amount);
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String[] methods = sc.nextLine().split(",");
        String[] amounts = sc.nextLine().split(",");

        boolean first = true;
        for (int i = 0; i < methods.length; i++) {
            String m = methods[i].trim();
            PaymentGateway gateway;
            if (m.equals("credit")) gateway = new CreditCardPayment();
            else if (m.equals("upi")) gateway = new UPIPayment();
            else continue;
            if (!first) System.out.println();
            first = false;
            gateway.processPayment(Double.parseDouble(amounts[i].trim()));
        }
    }
}
```
````

---

## 2. Abstract classes: shared steps, varying parts

Sometimes several classes follow the same fixed procedure and differ only in a few steps. An **abstract class** can hold the shared procedure, and declare the differing steps `abstract`, for each subclass to fill in:

```java run
// An abstract class fixes the steps; subclasses fill in one of them.
abstract class Report {
    // The template: every report has the same frame.
    final String render() {
        return "== " + title() + " ==\n" + body() + "\n-- generated by ReportService --";
    }

    abstract String title();
    abstract String body();
}

class SalesReport extends Report {
    String title() { return "Sales, March"; }
    String body() { return "orders: 1,204  revenue: 38,900"; }
}

class InventoryReport extends Report {
    String title() { return "Inventory"; }
    String body() { return "SKUs low on stock: 7"; }
}

public class Main {
    public static void main(String[] args) {
        System.out.println(new SalesReport().render());
        System.out.println(new InventoryReport().render());
    }
}
```

```python run
from abc import ABC, abstractmethod


# An abstract class fixes the steps; subclasses fill in one of them.
class Report(ABC):
    # The template: every report has the same frame.
    def render(self) -> str:
        return f"== {self.title()} ==\n{self.body()}\n-- generated by ReportService --"

    @abstractmethod
    def title(self) -> str: ...

    @abstractmethod
    def body(self) -> str: ...


class SalesReport(Report):
    def title(self) -> str:
        return "Sales, March"

    def body(self) -> str:
        return "orders: 1,204  revenue: 38,900"


class InventoryReport(Report):
    def title(self) -> str:
        return "Inventory"

    def body(self) -> str:
        return "SKUs low on stock: 7"


print(SalesReport().render())
print(InventoryReport().render())
```

**Output:**
```
== Sales, March ==
orders: 1,204  revenue: 38,900
-- generated by ReportService --
== Inventory ==
SKUs low on stock: 7
-- generated by ReportService --
```

**Analysis.** Both reports have the same header and footer, and neither subclass repeats that code. `render()` is the fixed procedure (Java's `final` keyword stops subclasses from changing it), and `title()` and `body()` are the steps that differ. This shape is the **Template Method** pattern, covered with the other [behavioural patterns](/synapse/low-level-design/design-patterns/behavioural-design-patterns).

**Intuition.**
*Mechanism.* An abstract class can have fields, constructors and fully written methods; an interface cannot have instance fields or constructors. You cannot create an object of an abstract class directly, and a class can extend only one class <abbr title="The Java Language Specification, Java SE 21, §8.1.1.1 abstract Classes">[2]</abbr>.

*Concrete bite.* That one-parent limit is the cost. A `SalesReport` that extends `Report` cannot also extend any other class. Interfaces have no such limit: a class can implement as many as it needs.

### Your Turn — Practice: Abstraction

Define an abstract `Animal` with an abstract `makeSound()`, then let `Dog` and `Cat` supply their own — runtime polymorphism through an abstract base.

````problem
Design an abstract class `Animal` and two concrete subclasses that override its abstract method.

**Abstract class `Animal`**

- Attribute: `name` (`String`).
- Abstract method: `makeSound()`.

**Subclasses**

- `Dog extends Animal` — `makeSound()` prints `The dog <name> says : Woof!`.
- `Cat extends Animal` — `makeSound()` prints `The cat <name> says : Meow!`.

**Input format.** Two lines on standard input: the dog's name, then the cat's name. The provided `Main` builds a `Dog` and a `Cat` (held as `Animal` references) and calls `makeSound()` on each, with a blank line between.

**Example 1** — Input: `Buddy`, `Whiskers`

```text
The dog Buddy says : Woof!

The cat Whiskers says : Meow!
```
````

```java run
import java.util.*;

abstract class Animal {
    protected String name;

    Animal(String name) {
        this.name = name;
    }

    // Abstract: no body here — each subclass MUST provide one.
    abstract void makeSound();
}

class Dog extends Animal {
    Dog(String name) {
        super(name);
    }

    @Override
    void makeSound() {
        // TODO: print "The dog <name> says : Woof!"
    }
}

class Cat extends Animal {
    Cat(String name) {
        super(name);
    }

    @Override
    void makeSound() {
        // TODO: print "The cat <name> says : Meow!"
    }
}

// The driver is complete — implement makeSound() in Dog and Cat above.
class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String dName = sc.nextLine().trim();
        String cName = sc.nextLine().trim();

        Animal dog = new Dog(dName);
        dog.makeSound();

        System.out.println();

        Animal cat = new Cat(cName);
        cat.makeSound();
    }
}
```

```testcases
{
  "args": [
    { "id": "dogName", "label": "Dog name", "type": "string" },
    { "id": "catName", "label": "Cat name", "type": "string" }
  ],
  "cases": [
    { "args": { "dogName": "Buddy", "catName": "Whiskers" }, "expected": "The dog Buddy says : Woof!\n\nThe cat Whiskers says : Meow!" },
    { "args": { "dogName": "Rex", "catName": "Felix" }, "expected": "The dog Rex says : Woof!\n\nThe cat Felix says : Meow!" }
  ]
}
```

````editorial
`Animal` can't be instantiated — it declares `makeSound()` with no body, so it exists only to be extended. Each subclass supplies its own `makeSound()`, and because `Main` holds the objects through `Animal` references, the JVM picks the right override at runtime from each object's actual type (`Dog` or `Cat`). That late binding is **runtime polymorphism**; the abstract method is the contract guaranteeing every animal has a sound.

```java solution
import java.util.*;

abstract class Animal {
    protected String name;

    Animal(String name) {
        this.name = name;
    }

    abstract void makeSound();
}

class Dog extends Animal {
    Dog(String name) {
        super(name);
    }

    @Override
    void makeSound() {
        System.out.println("The dog " + name + " says : Woof!");
    }
}

class Cat extends Animal {
    Cat(String name) {
        super(name);
    }

    @Override
    void makeSound() {
        System.out.println("The cat " + name + " says : Meow!");
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String dName = sc.nextLine().trim();
        String cName = sc.nextLine().trim();

        Animal dog = new Dog(dName);
        dog.makeSound();

        System.out.println();

        Animal cat = new Cat(cName);
        cat.makeSound();
    }
}
```
````

---

## 3. Interface or abstract class?

| Question | Interface | Abstract class |
|---|---|---|
| What does it describe? | an ability or role: *can send*, *can be priced* | a family of classes with a shared structure: *is a report* |
| Instance fields and constructors | no | yes |
| Shared method code | `default` methods, which can't use fields | yes, and it can use the class's fields |
| How many a class can have | many | one |
| Swapping in a test fake | easy: implement the interface | harder: must extend the class |

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use an interface by default for anything another class depends on. If several implementations share real code or fields, add an abstract class *behind* the interface, so that other code still depends only on the interface.

The cost of using both is two types where one might be enough. In return, other code depends on the flexible contract, while the implementations still share code.

</div>

---

## 4. `static` and nested classes in design

`static` members belong to the class, not to any one object: there is a single copy, and any code can reach it. The Java guide's [static vs Instance](/synapse/programming-languages/java/classes-and-objects/static-vs-instance) covers the rules. In design, `static` has two very different uses:

- **Static methods that use no stored state** are fine: `Math.max`, a `Money.parse(String)` that only reads its argument, or a **static factory method** such as `List.of(...)`, whose name says how the object is made.
- **Static fields that change**, and **static calls to things that can change**, are hidden dependencies. A `static Config current` field, or a call to a static `PaymentGateway.charge(...)` inside a method, cannot be replaced with a test fake. It is shared by every test and every thread. And it doesn't appear in any constructor, so someone reading the class can't see that the class depends on it.

The usual fix is the one from §1: turn the static dependency into an interface, and pass an implementation in. A clock is the classic example. Code that calls `LocalDate.now()` directly can't be tested as if it were a leap day; code that is given a `java.time.Clock` can <abbr title="Java SE 21 API, java.time.Clock">[3]</abbr>.

**Nested classes** are classes declared inside another class. In design they have one purpose: keeping a helper class next to the only class that uses it. A `static` nested class (such as a `Builder` inside the class it builds, or a `Node` inside a linked list) doesn't need an object of the outer class. An inner (non-static) class keeps a hidden reference to an outer object. Prefer `static` nested classes, unless the helper really needs the outer object's fields. The kinds and their rules are in the Java guide's [Nested & Anonymous Classes; Lambdas](/synapse/programming-languages/java/robust-oop/nested-and-anonymous-classes-and-lambdas).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use `static` only for constants, methods that don't use stored state, and factory methods. Anything that holds changing state, or reaches the outside world (the time, random numbers, the network, storage), should be an object that is passed in.

The cost is a few more constructor parameters. The benefit is code whose dependencies are visible, and can be replaced.

</div>

---

## 5. Mental-model summary

| Principle | Consequence |
|---|---|
| An interface is a contract; other code depends only on it | Implementations, including test fakes, can be switched without changing that code |
| Pass implementations in from outside (dependency injection) | The class that uses another object doesn't choose which implementation it gets |
| An abstract class holds shared steps and fields | Subclasses fill in the parts that differ (Template Method); a class has only one parent |
| Use interfaces for dependencies by default | Add an abstract class behind the interface to share code |
| Changing static fields and static calls are hidden dependencies | Hard to test and shared by everything; pass an object in instead |
| Static nested classes keep helper classes close to their user | Prefer them over inner classes, which hold a reference to the outer object |

## 6. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

| Symptom | Likely cause | Fix |
|---|---|---|
| Tests send real emails or hit real services | the class creates its collaborators with `new` | depend on an interface; inject the implementation |
| Adding a new channel means editing the service | the service names a concrete class | program to an interface |
| Tests pass alone and fail together | shared `static` mutable state | make it an instance field of an injected object |
| Date-dependent code can't be tested | direct calls to `now()` | inject a `Clock` |
| A class needs two abstract parents | abstract classes allow only one | make the roles interfaces; share code by composition |
| An interface with one implementation and no tests needing a fake | an abstraction added "just in case" | inline it until a second implementation exists |

</div>

---

## ✅ Check yourself

One check per objective. Answer before you open anything.

```quiz
{"prompt": "OrderService receives a Notifier in its constructor. How do you test placeOrder without sending a message?", "options": ["Pass a fake Notifier that records what it was asked to send", "Edit OrderService to skip sending in tests", "Disconnect the network during tests"], "answer": "Pass a fake Notifier that records what it was asked to send"}
```

```quiz
{"prompt": "Several report types share a fixed header and footer, kept in fields, and differ only in the body. Which fits best?", "options": ["An abstract class with a final render() and an abstract body()", "An interface with no default methods", "Copying the header and footer code into each report"], "answer": "An abstract class with a final render() and an abstract body()"}
```

```quiz
{"prompt": "A method calls LocalDate.now() to decide whether a coupon has expired. What is the design problem?", "options": ["The current date is a hidden dependency that tests cannot control", "LocalDate.now() is not thread-safe", "There is no problem"], "answer": "The current date is a hidden dependency that tests cannot control"}
```

<details>
<summary>A <code>CheckoutService</code> calls <code>StripeClient.charge(...)</code>, a static method, directly. How would you change the design so you can add a second payment provider and test checkout without charging cards?</summary>

Define a `PaymentGateway` interface with a `charge` method. Write a `StripeGateway implements PaymentGateway` class whose `charge` makes the static call, and a second implementation for the other provider. Give `CheckoutService` a `PaymentGateway` in its constructor. Tests pass a fake gateway that records charges and can be told to fail, so both the success and failure paths can be tested.

</details>

---

## 📚 Sources

1. Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software* (Addison-Wesley, 1994), ch. 1.
2. *The Java Language Specification, Java SE 21*, §8.1.1.1 "`abstract` Classes" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.1.1.1>
3. `java.time.Clock`, Java SE 21 API — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/Clock.html>
4. Python 3 documentation, `typing.Protocol` and `abc` — <https://docs.python.org/3/library/typing.html#typing.Protocol>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.**

1. In §1, write a `PushNotifier` and pass it to `OrderService`. Predict which lines of `OrderService` you had to change.
2. In §2, try to override `render()` in `SalesReport`. Predict what Java says.
3. In §2's Python version, delete `body()` from `InventoryReport`. Predict what happens when it is created.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
