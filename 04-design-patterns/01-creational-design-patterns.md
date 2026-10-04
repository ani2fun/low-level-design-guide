---
title: "Creational Design Patterns"
summary: "Singleton, Factory, Abstract Factory, Builder, and Prototype — the patterns that control how objects get created."
essential: true
---

# Creational Design Patterns

In object-oriented design, the way you create objects can heavily impact the flexibility and maintainability of your system. If your codebase is littered with `new` keywords hardcoded to specific classes, it becomes difficult to change those classes later without breaking everything.

Creational design patterns abstract the instantiation process. They help make a system independent of how its objects are created, composed, and represented, providing mechanisms that control when and how objects are instantiated.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.** Hardcoding `new SpecificClass()` tightly couples your code to that exact implementation. Creational patterns hide the creation logic behind an interface or method, allowing you to swap implementations flexibly.

</div>

**You'll be able to:**
- Guarantee that only one instance of a class exists (Singleton).
- Delegate object creation to subclasses (Factory).
- Create families of related objects (Abstract Factory).
- Construct complex objects step-by-step (Builder).
- Clone existing objects without depending on their classes (Prototype).

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** As you read, look for the *Mechanism* and *Concrete bite* under each code block. They map the code you just saw to the mental model you need to build.

</div>

1. [Singleton Pattern](#1-singleton-pattern)
2. [Factory Pattern](#2-factory-pattern)
3. [Builder Pattern](#3-builder-pattern)
4. [Abstract Factory Pattern](#4-abstract-factory-pattern)
5. [Prototype Pattern](#5-prototype-pattern)

## 1. Singleton Pattern

The Singleton Pattern ensures that a class has only one instance and provides a global point of access to that instance.

In a typical application, creating multiple objects of a class might not be problematic. However, for resources like logging, configuration handling, or managing a database connection, you want exactly one instance to avoid redundancy, excessive memory use, or inconsistent behaviour.

```java run
class Configuration {
    // Volatile ensures changes made by one thread are immediately visible to others
    private static volatile Configuration instance;
    private String dbUrl;

    // Private constructor prevents instantiation from outside
    private Configuration() {
        this.dbUrl = "jdbc:postgresql://localhost:5432/mydb";
    }

    // Double-checked locking for thread safety
    public static Configuration getInstance() {
        if (instance == null) {
            synchronized (Configuration.class) {
                if (instance == null) {
                    instance = new Configuration();
                }
            }
        }
        return instance;
    }

    public String getDbUrl() {
        return dbUrl;
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Configuration config1 = Configuration.getInstance();
        Configuration config2 = Configuration.getInstance();
        
        System.out.println("config1 URL: " + config1.getDbUrl());
        System.out.println("Same instance? " + (config1 == config2));
    }
}
```
```python run
import threading


class Configuration:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "Configuration":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super().__new__(cls)
                    # Initialize only once
                    cls._instance.db_url = "jdbc:postgresql://localhost:5432/mydb"
        return cls._instance


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    config1 = Configuration()
    config2 = Configuration()

    print(f"config1 URL: {config1.db_url}")
    print(f"Same instance? {config1 is config2}")
```

**Output (Java):**
```
config1 URL: jdbc:postgresql://localhost:5432/mydb
Same instance? true
```

**Output (Python):**
```
config1 URL: jdbc:postgresql://localhost:5432/mydb
Same instance? True
```

**Analysis.** Both `config1` and `config2` point to the exact same object in memory. In Java, this is achieved by making the constructor private and controlling access through a static `getInstance()` method. In Python, overriding `__new__` achieves the same effect. Both use double-checked locking to remain thread-safe without sacrificing performance.

**Intuition.**
- **Mechanism.** Hide the constructor and provide a static method that creates the object once and returns the cached instance on subsequent calls.
- **Concrete bite.** Imagine a building's fire extinguisher. You don't buy a new extinguisher every time someone asks where it is; you just point them to the same, single extinguisher on the wall.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a Singleton when a class must have exactly one instance available to clients (e.g. a shared configuration). The cost is tight coupling and potential difficulty in unit testing because of global state.

</div>

## 2. Factory Pattern

The Factory Pattern provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created.

When client code needs to work with multiple types of related objects and the decision of which to instantiate is made at runtime, the Factory pattern encapsulates that decision.

```java run
interface Logistics {
    void send();
}

class Road implements Logistics {
    public void send() {
        System.out.println("Sending by road logic...");
    }
}

class Air implements Logistics {
    public void send() {
        System.out.println("Sending by air logic...");
    }
}

class LogisticsFactory {
    public static Logistics getLogistics(String mode) {
        if (mode.equalsIgnoreCase("Air")) {
            return new Air();
        } else if (mode.equalsIgnoreCase("Road")) {
            return new Road();
        }
        throw new IllegalArgumentException("Unknown logistics mode: " + mode);
    }
}

class LogisticsService {
    public void executeDelivery(String mode) {
        Logistics logistics = LogisticsFactory.getLogistics(mode);
        logistics.send();
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        LogisticsService service = new LogisticsService();
        service.executeDelivery("Air");
        service.executeDelivery("Road");
    }
}
```
```python run
from abc import ABC, abstractmethod


class Logistics(ABC):
    @abstractmethod
    def send(self) -> None:
        ...


class Road(Logistics):
    def send(self) -> None:
        print("Sending by road logic...")


class Air(Logistics):
    def send(self) -> None:
        print("Sending by air logic...")


class LogisticsFactory:
    @staticmethod
    def get_logistics(mode: str) -> Logistics:
        mode = mode.lower()
        if mode == "air":
            return Air()
        elif mode == "road":
            return Road()
        raise ValueError(f"Unknown logistics mode: {mode}")


class LogisticsService:
    def execute_delivery(self, mode: str) -> None:
        logistics = LogisticsFactory.get_logistics(mode)
        logistics.send()


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    service = LogisticsService()
    service.execute_delivery("Air")
    service.execute_delivery("Road")
```

**Output:**
```
Sending by air logic...
Sending by road logic...
```

**Analysis.** The `LogisticsService` class does not know about the concrete `Road` or `Air` classes. It asks `LogisticsFactory` for an object that implements the `Logistics` interface. If we add a new `Ship` class, we only modify the factory, leaving `LogisticsService` untouched (adhering to the Open/Closed Principle).

**Intuition.**
- **Mechanism.** Replace direct object construction calls (`new`) with calls to a special factory method.
- **Concrete bite.** When you order a pizza, you don't go to the kitchen to bake it. You ask the cashier (the factory) for a "Margherita", and they hand you the finished product. You only interact with the interface ("Pizza").

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Move object creation logic out of business logic and into a dedicated factory. The cost is an increase in the number of small classes.

</div>

## 4. Abstract Factory Pattern

The Abstract Factory Pattern provides an interface for creating families of related or dependent objects without specifying their concrete classes. 

You use it when your code needs to work with various families of related products (e.g. Mac UI components vs Windows UI components), but you don't want it to depend on the concrete classes of those products.

```java run
// 1. The abstract products
interface PaymentGateway { void processPayment(double amount); }
interface Invoice { void generateInvoice(); }

// 2. Concrete products for India
class RazorpayGateway implements PaymentGateway {
    public void processPayment(double amount) { System.out.println("INR payment via Razorpay: " + amount); }
}
class GSTInvoice implements Invoice {
    public void generateInvoice() { System.out.println("GST Invoice for India."); }
}

// 3. Concrete products for US
class StripeGateway implements PaymentGateway {
    public void processPayment(double amount) { System.out.println("USD payment via Stripe: " + amount); }
}
class USInvoice implements Invoice {
    public void generateInvoice() { System.out.println("Invoice for US norms."); }
}

// 4. The Abstract Factory
interface RegionFactory {
    PaymentGateway createPaymentGateway();
    Invoice createInvoice();
}

// 5. Concrete Factories
class IndiaFactory implements RegionFactory {
    public PaymentGateway createPaymentGateway() { return new RazorpayGateway(); }
    public Invoice createInvoice() { return new GSTInvoice(); }
}
class USFactory implements RegionFactory {
    public PaymentGateway createPaymentGateway() { return new StripeGateway(); }
    public Invoice createInvoice() { return new USInvoice(); }
}

// Client
class CheckoutService {
    private PaymentGateway paymentGateway;
    private Invoice invoice;

    public CheckoutService(RegionFactory factory) {
        this.paymentGateway = factory.createPaymentGateway();
        this.invoice = factory.createInvoice();
    }

    public void completeOrder(double amount) {
        paymentGateway.processPayment(amount);
        invoice.generateInvoice();
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        CheckoutService indiaCheckout = new CheckoutService(new IndiaFactory());
        indiaCheckout.completeOrder(1500.00);

        CheckoutService usCheckout = new CheckoutService(new USFactory());
        usCheckout.completeOrder(49.99);
    }
}
```
```python run
from abc import ABC, abstractmethod


# 1. The abstract products
class PaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> None: ...

class Invoice(ABC):
    @abstractmethod
    def generate_invoice(self) -> None: ...


# 2. Concrete products for India
class RazorpayGateway(PaymentGateway):
    def process_payment(self, amount: float) -> None:
        print(f"INR payment via Razorpay: {amount}")

class GSTInvoice(Invoice):
    def generate_invoice(self) -> None:
        print("GST Invoice for India.")


# 3. Concrete products for US
class StripeGateway(PaymentGateway):
    def process_payment(self, amount: float) -> None:
        print(f"USD payment via Stripe: {amount}")

class USInvoice(Invoice):
    def generate_invoice(self) -> None:
        print("Invoice for US norms.")


# 4. The Abstract Factory
class RegionFactory(ABC):
    @abstractmethod
    def create_payment_gateway(self) -> PaymentGateway: ...
    
    @abstractmethod
    def create_invoice(self) -> Invoice: ...


# 5. Concrete Factories
class IndiaFactory(RegionFactory):
    def create_payment_gateway(self) -> PaymentGateway:
        return RazorpayGateway()

    def create_invoice(self) -> Invoice:
        return GSTInvoice()


class USFactory(RegionFactory):
    def create_payment_gateway(self) -> PaymentGateway:
        return StripeGateway()

    def create_invoice(self) -> Invoice:
        return USInvoice()


# Client
class CheckoutService:
    def __init__(self, factory: RegionFactory) -> None:
        self.payment_gateway = factory.create_payment_gateway()
        self.invoice = factory.create_invoice()

    def complete_order(self, amount: float) -> None:
        self.payment_gateway.process_payment(amount)
        self.invoice.generate_invoice()


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    india_checkout = CheckoutService(IndiaFactory())
    india_checkout.complete_order(1500.00)

    us_checkout = CheckoutService(USFactory())
    us_checkout.complete_order(49.99)
```

**Output:**
```
INR payment via Razorpay: 1500.0
GST Invoice for India.
USD payment via Stripe: 49.99
Invoice for US norms.
```

**Analysis.** The `CheckoutService` doesn't care whether it is running in India or the US. It just asks the `RegionFactory` for a `PaymentGateway` and an `Invoice`. The concrete factories (`IndiaFactory`, `USFactory`) guarantee that the products created belong to the same region and are compatible.

**Intuition.**
- **Mechanism.** Group a set of related factory methods into one interface.
- **Concrete bite.** When buying furniture, you don't pick a random Victorian chair, a Modernist table, and an Art Deco sofa. You go to the "Victorian Furniture" factory to get a matching set of chairs, tables, and sofas.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use the Abstract Factory when your code needs to work with various families of related products, and you want to ensure that it only ever uses products from one family at a time.

</div>

## 5. Prototype Pattern

The Prototype Pattern lets you copy existing objects without making your code dependent on their classes.

When you need an exact copy of an object, instead of writing code to instantiate a new object and painstakingly copying every field (which might be private and inaccessible), you delegate the cloning process to the object itself.

```java run
abstract class Document implements Cloneable {
    private String title;
    
    public Document(String title) {
        this.title = title;
    }
    
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    
    public abstract Document clone();
}

class InvoiceDoc extends Document {
    private double amount;
    
    public InvoiceDoc(String title, double amount) {
        super(title);
        this.amount = amount;
    }
    
    @Override
    public InvoiceDoc clone() {
        // Here we simulate deep/shallow copy based on business needs
        return new InvoiceDoc(this.getTitle(), this.amount);
    }
    
    @Override
    public String toString() {
        return "Invoice[" + getTitle() + ", $" + amount + "]";
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        InvoiceDoc original = new InvoiceDoc("Monthly Server", 250.0);
        InvoiceDoc copy = original.clone();
        
        copy.setTitle("Monthly Server - Copy");
        
        System.out.println("Original: " + original);
        System.out.println("Copy: " + copy);
        System.out.println("Are they the same object? " + (original == copy));
    }
}
```
```python run
import copy


class Document:
    def __init__(self, title: str) -> None:
        self.title = title

    def clone(self) -> "Document":
        # Python's `copy.deepcopy` is often used to implement Prototype natively
        return copy.deepcopy(self)


class InvoiceDoc(Document):
    def __init__(self, title: str, amount: float) -> None:
        super().__init__(title)
        self.amount = amount

    def __str__(self) -> str:
        return f"Invoice[{self.title}, ${self.amount}]"


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    original = InvoiceDoc("Monthly Server", 250.0)
    copied = original.clone()

    copied.title = "Monthly Server - Copy"

    print(f"Original: {original}")
    print(f"Copy: {copied}")
    print(f"Are they the same object? {original is copied}")
```

**Output (Java):**
```
Original: Invoice[Monthly Server, $250.0]
Copy: Invoice[Monthly Server - Copy, $250.0]
Are they the same object? false
```

**Output (Python):**
```
Original: Invoice[Monthly Server, $250.0]
Copy: Invoice[Monthly Server - Copy, $250.0]
Are they the same object? False
```

**Analysis.** The `InvoiceDoc` provides a `clone()` method. The caller does not need to know the exact class of the `Document` it is holding, nor does it need to know how to construct it from scratch. It just asks the object to clone itself. Note that in Java, for a deeper dive on cloning, review the Object Model lesson: `/synapse/programming-languages/java/classes-and-objects/references-equality-and-the-object-model`.

**Intuition.**
- **Mechanism.** Declare a `clone` method in the base class or interface. Implement it in concrete classes by creating a new instance and copying state.
- **Concrete bite.** When dividing cells, a cell doesn't ask an external factory to assemble a new cell from proteins. It simply splits and replicates its own DNA.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Delegate the cloning process to the actual objects that are being cloned. The cost is handling circular references during deep copies.

</div>

## Summary

| Pattern | Purpose |
|---|---|
| **Singleton** | Ensures only one instance of a class exists globally. |
| **Factory Method** | Defines an interface for creating a single object, but lets subclasses decide which class to instantiate. |
| **Abstract Factory** | Creates families of related objects without specifying their concrete classes. |
| **Builder** | Constructs complex objects step-by-step, allowing different representations. |
| **Prototype** | Creates new objects by copying an existing object (the prototype). |

## 🚨 Gotcha Checklist
| Symptom | Likely cause | Fix |
|---|---|---|
| A `getInstance()` call returns different objects on different threads. | **Thread-safety violation.** The Singleton was lazily initialized without locks. | Add double-checked locking, or use a static nested class. |
| You have a constructor with 10 parameters, and 8 of them are `null`. | **Telescoping constructor.** You are trying to handle optionality in the constructor. | Extract the logic into a Builder. |
| Passing an abstract factory around results in a mismatch (e.g. Mac buttons on a Windows window). | **Leaky abstraction.** You accidentally bypassed the factory for some objects. | Ensure *all* family objects are created strictly via the Abstract Factory. |

## ✅ Check yourself

```quiz
{
  "prompt": "Which pattern is the best fit when you need to construct a complex `House` object that might optionally have a pool, a garage, or a garden?",
  "options": [
    "Singleton",
    "Factory Method",
    "Builder",
    "Prototype"
  ],
  "answer": "Builder"
}
```

```quiz
{
  "prompt": "Which pattern guarantees that all objects created by it belong to the same family?",
  "options": [
    "Factory Method",
    "Abstract Factory",
    "Singleton",
    "Builder"
  ],
  "answer": "Abstract Factory"
}
```

<details>
<summary>What is the difference between Factory Method and Abstract Factory?</summary>

The Factory Method creates one single product. You override the method in subclasses to change the product created. The Abstract Factory creates a *family* of products (e.g. Chair, Table, Sofa). An Abstract Factory usually has multiple methods (one for each product type), and it is often implemented using Factory Methods internally.
</details>

## 📚 Sources
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

<div style="border-left:4px solid #8e155c;background:rgba(142,21,92,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** 
If a singleton class implements `Cloneable` and allows callers to call `clone()`, what happens?

It breaks the Singleton guarantee. The caller can create a second instance of the Singleton. To fix this, a strict Singleton must override `clone()` to either throw an exception or just return `this`.

</div>

## Your Turn

Look through your system for a class that has the word `Factory` or `Builder` in it. Does it actually hide the instantiation logic, or does the caller still end up calling `new` somewhere? Try refactoring a sprawling constructor in your own code into a Builder.
