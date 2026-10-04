---
title: "Introduction to Design Patterns"
summary: "What design patterns are, where they came from, and the three GoF categories that organize them."
essential: true
---

# Introduction to Design Patterns

Design patterns are standard, time-tested solutions to common software design problems. They are not code templates that you can copy and paste directly into your program, but rather abstract descriptions or blueprints that help developers solve recurring issues in code architecture and system design. 

Formalized by the "Gang of Four" (GoF) — Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides — in their seminal 1994 book, these 23 patterns form the shared vocabulary of object-oriented software engineering.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.** You are not the first person to face a particular structural problem in code. Instead of reinventing the wheel, use a proven blueprint (a design pattern) that has already been battle-tested by the industry.

</div>

**You'll be able to:**
- Explain the purpose of a design pattern.
- Identify the three main Gang of Four (GoF) categories.
- Distinguish between creational, structural, and behavioral problems.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** As you read, look for the *Mechanism* and *Concrete bite* under each code block. They map the code you just saw to the mental model you need to build.

</div>

1. [Creational Patterns](#1-creational-patterns)
2. [Structural Patterns](#2-structural-patterns)
3. [Behavioral Patterns](#3-behavioral-patterns)

```mermaid
flowchart TD
    GoF["Design Patterns<br/>(Gang of Four — 23 patterns)"]
    GoF --> C["Creational<br/><i>object creation</i>"]
    GoF --> S["Structural<br/><i>object composition</i>"]
    GoF --> B["Behavioral<br/><i>object interaction</i>"]
    C --> Cx["Singleton · Factory Method<br/>Abstract Factory · Builder · Prototype"]
    S --> Sx["Adapter · Bridge · Composite · Decorator<br/>Facade · Flyweight · Proxy"]
    B --> Bx["Observer · Strategy · Command · State · Iterator<br/>Mediator · Chain of Responsibility · Template Method<br/>Visitor · Memento · Interpreter"]
    classDef root fill:#f3f4f6,stroke:#6b7280,color:#111827;
    classDef creational fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef structural fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef behavioral fill:#f3e8ff,stroke:#9333ea,color:#581c87;
    class GoF root;
    class C,Cx creational;
    class S,Sx structural;
    class B,Bx behavioral;
```

## 1. Creational Patterns

Creational patterns focus on object creation mechanisms. They abstract the instantiation process, making the system independent of how its objects are created, composed, and represented.

Rather than scattering `new` keywords throughout your business logic, creational patterns centralise and encapsulate creation.

```java run
interface Drink {
    void consume();
}

class OrangeJuice implements Drink {
    public void consume() { System.out.println("Drinking Orange Juice."); }
}

// The Factory (Creational Pattern)
class VendingMachine {
    public Drink dispense(String type) {
        if ("orange".equalsIgnoreCase(type)) {
            return new OrangeJuice();
        }
        throw new IllegalArgumentException("Unknown drink");
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        VendingMachine machine = new VendingMachine();
        Drink drink = machine.dispense("orange");
        drink.consume();
    }
}
```
```python run
from abc import ABC, abstractmethod


class Drink(ABC):
    @abstractmethod
    def consume(self) -> None:
        ...


class OrangeJuice(Drink):
    def consume(self) -> None:
        print("Drinking Orange Juice.")


# The Factory (Creational Pattern)
class VendingMachine:
    def dispense(self, drink_type: str) -> Drink:
        if drink_type.lower() == "orange":
            return OrangeJuice()
        raise ValueError("Unknown drink")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    machine = VendingMachine()
    drink = machine.dispense("orange")
    drink.consume()
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The caller doesn't use the `new` keyword to create `OrangeJuice`. The `VendingMachine` handles the creation logic, freeing the caller from dependency on the concrete class.

**Intuition.**
- **Mechanism.** Wrap object creation inside a dedicated method or class.
- **Concrete bite.** When you order at a vending machine, you press a button ("Orange Juice"). The machine internally figures out how to prepare it — you don't care how it's made, you just get your drink.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Hide the complexity of object creation from the client code.

</div>

## 2. Structural Patterns

Structural patterns deal with object composition — how classes and objects can be combined to form larger structures while keeping the system flexible and efficient. They help incompatible interfaces work together.

```java run
// An old interface we cannot change
interface MicroUsb {
    void chargeWithMicroUsb();
}

class OldPhone implements MicroUsb {
    public void chargeWithMicroUsb() {
        System.out.println("Charging via Micro USB.");
    }
}

// A new interface our system uses
interface UsbC {
    void chargeWithUsbC();
}

// The Adapter (Structural Pattern)
class MicroUsbToUsbCAdapter implements UsbC {
    private MicroUsb device;
    
    public MicroUsbToUsbCAdapter(MicroUsb device) {
        this.device = device;
    }
    
    public void chargeWithUsbC() {
        // delegates the call
        device.chargeWithMicroUsb();
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        MicroUsb oldPhone = new OldPhone();
        UsbC adapter = new MicroUsbToUsbCAdapter(oldPhone);
        
        System.out.println("Using USB-C charger:");
        adapter.chargeWithUsbC();
    }
}
```
```python run
from abc import ABC, abstractmethod


# An old interface we cannot change
class MicroUsb(ABC):
    @abstractmethod
    def charge_with_micro_usb(self) -> None:
        ...


class OldPhone(MicroUsb):
    def charge_with_micro_usb(self) -> None:
        print("Charging via Micro USB.")


# A new interface our system uses
class UsbC(ABC):
    @abstractmethod
    def charge_with_usb_c(self) -> None:
        ...


# The Adapter (Structural Pattern)
class MicroUsbToUsbCAdapter(UsbC):
    def __init__(self, device: MicroUsb) -> None:
        self._device = device

    def charge_with_usb_c(self) -> None:
        # delegates the call
        self._device.charge_with_micro_usb()


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    old_phone = OldPhone()
    adapter = MicroUsbToUsbCAdapter(old_phone)

    print("Using USB-C charger:")
    adapter.charge_with_usb_c()
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `OldPhone` and the `UsbC` standard are incompatible. The `MicroUsbToUsbCAdapter` acts as a structural bridge, combining them so they work together without modifying `OldPhone`'s source code.

**Intuition.**
- **Mechanism.** Use composition or inheritance to wrap an object, translating its interface into what the client expects.
- **Concrete bite.** You have a modern smartphone with a USB-C charger, but your old phone uses micro-USB. Instead of rewriting the old phone's hardware, you use a physical adapter.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Combine objects using wrappers and interfaces to build larger, flexible structures out of incompatible parts.

</div>

## 3. Behavioral Patterns

Behavioral patterns are concerned with object interaction and responsibility — how objects communicate, assign responsibilities, and coordinate tasks while ensuring loose coupling.

```java run
import java.util.*;

// The Mediator (Behavioral Pattern)
class Waiter {
    public void routeOrder(String order) {
        System.out.println("Waiter taking order: " + order + " -> passing to Kitchen.");
        // Kitchen logic would go here
    }
}

class Customer {
    private Waiter waiter;
    
    public Customer(Waiter waiter) {
        this.waiter = waiter;
    }
    
    public void orderFood(String food) {
        waiter.routeOrder(food);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Waiter waiter = new Waiter();
        Customer customer = new Customer(waiter);
        
        customer.orderFood("Pizza");
    }
}
```
```python run
# The Mediator (Behavioral Pattern)
class Waiter:
    def route_order(self, order: str) -> None:
        print(f"Waiter taking order: {order} -> passing to Kitchen.")
        # Kitchen logic would go here


class Customer:
    def __init__(self, waiter: Waiter) -> None:
        self._waiter = waiter

    def order_food(self, food: str) -> None:
        self._waiter.route_order(food)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    waiter = Waiter()
    customer = Customer(waiter)

    customer.order_food("Pizza")
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `Customer` doesn't need a reference to the kitchen, the chef, or the inventory. They only talk to the `Waiter` (a mediator), which coordinates the complex interactions behind the scenes.

**Intuition.**
- **Mechanism.** Define objects that encapsulate the rules of communication, preventing objects from explicitly referring to each other.
- **Concrete bite.** In a restaurant, you don't shout your order directly at the chef. The waiter acts as a mediator between you and the kitchen, reducing chaos and decoupling you from the cooking process.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Organise the flow of control and communication between objects to prevent a tangled, tightly-coupled web of dependencies.

</div>

## Summary

| Category | What it handles | Typical phrase | Example patterns |
|---|---|---|---|
| **Creational** | Object creation | "Who creates this?" | Factory, Singleton, Builder |
| **Structural** | Object composition | "How do we fit these together?" | Adapter, Decorator, Facade |
| **Behavioral** | Object communication | "Who does what and when?" | Observer, Strategy, Mediator |

## 🚨 Gotcha Checklist
| Symptom | Likely cause | Fix |
|---|---|---|
| You try to use a pattern for everything. | **Pattern fever.** Forcing a pattern where simple code suffices. | Remember patterns add complexity. Only use them when the problem explicitly calls for them. |
| You memorize the code instead of the intent. | **Implementation focus.** Patterns look different across languages. | Learn *why* a pattern exists, not just how to type it. |

## ✅ Check yourself

```quiz
{
  "prompt": "If you are trying to make an old logging library work with a new analytics dashboard that expects a different interface, which category of pattern do you need?",
  "options": [
    "Creational",
    "Structural",
    "Behavioral"
  ],
  "answer": "Structural"
}
```

```quiz
{
  "prompt": "Which category of patterns is concerned with algorithms and the assignment of responsibilities between objects?",
  "options": [
    "Creational",
    "Structural",
    "Behavioral"
  ],
  "answer": "Behavioral"
}
```

<details>
<summary>Why shouldn't I use design patterns everywhere?</summary>

Every design pattern adds a layer of abstraction. Abstraction means more classes, more interfaces, and more indirection. If a simple function or a basic class solves your problem without causing maintenance headaches, using a pattern is over-engineering. Patterns are cures for specific architectural pains; don't take the medicine if you aren't sick.
</details>

## 📚 Sources
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

<div style="border-left:4px solid #8e155c;background:rgba(142,21,92,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** 
If you need to ensure that only one connection to your database is ever created, which category of pattern would you look into?

Creational. The Singleton pattern, which ensures a class has only one instance, falls under the creational category because it explicitly controls object instantiation.

</div>

## Your Turn

Think of the codebase you work in most frequently. Can you spot one place where object creation is mixed with business logic? Can you spot one place where two incompatible classes are duct-taped together? These are the breeding grounds for Creational and Structural patterns.
