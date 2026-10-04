---
title: "SOLID Principles"
summary: "The five SOLID principles — SRP, OCP, LSP, ISP, and DIP — for writing clean, extensible, maintainable object-oriented code, with real-life analogies and before/after examples."
essential: true
---

# SOLID Principles

As systems grow, they tend to become fragile, rigid, and hard to understand. The SOLID principles are a set of five design guidelines introduced by Robert C. Martin to combat these symptoms of rotting software.

They are not strict laws, but rather structural heuristics for writing clean, scalable, maintainable object-oriented code. When applied correctly, they decouple the parts of a system so that a change in one place does not cause cascading breakages elsewhere.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.** Code is read and modified far more often than it is written. Designing for change means separating concerns, relying on abstractions rather than concrete details, and ensuring that new behavior can be added without editing existing, stable code.

</div>

**You'll be able to:**
- Identify when a class has too many responsibilities (SRP).
- Add new features without modifying existing code (OCP).
- Safely substitute subclasses for their parents (LSP).
- Keep interfaces small and client-specific (ISP).
- Decouple high-level logic from low-level details (DIP).

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** As you read, look for the *Mechanism* and *Concrete bite* under each code block. They map the code you just saw to the mental model you need to build.

</div>

1. [Single Responsibility Principle (SRP)](#1-single-responsibility-principle-srp)
2. [Open/Closed Principle (OCP)](#2-openclosed-principle-ocp)
3. [Liskov Substitution Principle (LSP)](#3-liskov-substitution-principle-lsp)
4. [Interface Segregation Principle (ISP)](#4-interface-segregation-principle-isp)
5. [Dependency Inversion Principle (DIP)](#5-dependency-inversion-principle-dip)

## 1. Single Responsibility Principle (SRP)

A class should have only one reason to change. In other words, a class should only have one job, one responsibility, and one purpose. If a class takes more than one responsibility, it becomes coupled. If one responsibility changes, the other responsibilities may also be affected.

Consider an online compiler. A single `OnlineCompiler` class that generates driver code, checks syntax, runs tests, and saves to a database violates SRP. We can split it into focused collaborators.

```java run
import java.util.*;

class DriverCodeGenerator {
    public String generate(String code) {
        return "// driver\n" + code + "\n// end driver";
    }
}

class SyntaxChecker {
    public boolean check(String code) {
        return !code.trim().isEmpty();
    }
}

class TestRunner {
    public List<String> run(String code, List<String> testCases) {
        List<String> results = new ArrayList<>();
        for (String t : testCases) {
            results.add("input=" + t + " -> ok");
        }
        return results;
    }
}

class DatabaseManager {
    public void save(List<String> output) {
        // pretend persistence
    }
}

class UserOutputHandler {
    public String present(List<String> output) {
        return String.join("\n", output);
    }
}

class Coordinator {
    private DriverCodeGenerator driver = new DriverCodeGenerator();
    private SyntaxChecker checker = new SyntaxChecker();
    private TestRunner runner = new TestRunner();
    private DatabaseManager db = new DatabaseManager();
    private UserOutputHandler output = new UserOutputHandler();

    public String compileAndRun(String code, List<String> testCases) {
        String wrapped = driver.generate(code);
        if (!checker.check(wrapped)) return "Syntax error";
        
        List<String> results = runner.run(wrapped, testCases);
        db.save(results);
        return output.present(results);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Coordinator coordinator = new Coordinator();
        String result = coordinator.compileAndRun("print('hello')", Arrays.asList("case1", "case2"));
        System.out.println(result);
    }
}
```
```python run
class DriverCodeGenerator:
    def generate(self, code: str) -> str:
        return f"// driver\n{code}\n// end driver"


class SyntaxChecker:
    def check(self, code: str) -> bool:
        return code.strip() != ""


class TestRunner:
    def run(self, code: str, test_cases: list) -> list:
        return [f"input={t!r} -> ok" for t in test_cases]


class DatabaseManager:
    def save(self, output: list) -> None:
        pass  # pretend persistence


class UserOutputHandler:
    def present(self, output: list) -> str:
        return "\n".join(output)


class Coordinator:
    def __init__(self) -> None:
        self._driver = DriverCodeGenerator()
        self._checker = SyntaxChecker()
        self._runner = TestRunner()
        self._db = DatabaseManager()
        self._output = UserOutputHandler()

    def compile_and_run(self, code: str, test_cases: list) -> str:
        wrapped = self._driver.generate(code)
        if not self._checker.check(wrapped):
            return "Syntax error"
        results = self._runner.run(wrapped, test_cases)
        self._db.save(results)
        return self._output.present(results)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    coordinator = Coordinator()
    result = coordinator.compile_and_run("print('hello')", ["case1", "case2"])
    print(result)
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `Coordinator` class orchestrates the process, but the actual work is delegated to five single-purpose collaborators. If the database schema changes, only `DatabaseManager` is edited. If the syntax checking logic improves, only `SyntaxChecker` changes.

**Intuition.**
- **Mechanism.** SRP separates concerns. You build many small, focused classes instead of a few large ones.
- **Concrete bite.** Imagine a chef who cooks, cleans, serves food, and orders groceries. If they are busy cleaning, they can't focus on cooking. Assigning one job per person (chef, cleaner, waiter, manager) leads to better results. 

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Keep classes small and focused on a single responsibility. This improves maintainability, readability, and testability.

</div>

## 2. Open/Closed Principle (OCP)

Software entities (classes, modules, functions) should be open for extension, but closed for modification. This means that the behaviour of a module can be extended without modifying its source code. 

Consider an invoicing system that calculates tax based on the region. A bad design uses an `if/else` chain for each region. A good design relies on an abstraction.

```java run
// Tax strategy Interface
interface TaxCalculator {
    double calculateTax(double amount);
}

// Implementing Region-Specific Tax Calculators
class IndiaTaxCalculator implements TaxCalculator {
    public double calculateTax(double amount) {
        return amount * 0.18; // GST
    }
}

class USTaxCalculator implements TaxCalculator {
    public double calculateTax(double amount) {
        return amount * 0.08; // Sales Tax
    }
}

class Invoice {
    private double amount;
    private TaxCalculator taxCalculator;

    public Invoice(double amount, TaxCalculator taxCalculator) {
        this.amount = amount;
        this.taxCalculator = taxCalculator;
    }

    public double getTotalAmount() {
        return amount + taxCalculator.calculateTax(amount);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        double amount = 1000.0;

        Invoice indiaInvoice = new Invoice(amount, new IndiaTaxCalculator());
        System.out.println("Total (India): " + indiaInvoice.getTotalAmount());

        Invoice usInvoice = new Invoice(amount, new USTaxCalculator());
        System.out.println("Total (US): " + usInvoice.getTotalAmount());
    }
}
```
```python run
from abc import ABC, abstractmethod


class TaxCalculator(ABC):  
    @abstractmethod          
    def calculate_tax(self, amount: float) -> float:
        ...


class IndiaTaxCalculator(TaxCalculator):
    def calculate_tax(self, amount: float) -> float:
        return amount * 0.18  # GST


class USTaxCalculator(TaxCalculator):
    def calculate_tax(self, amount: float) -> float:
        return amount * 0.08  # Sales Tax


class Invoice:
    def __init__(self, amount: float, tax_calculator: TaxCalculator) -> None:
        self._amount = amount
        self._tax_calculator = tax_calculator

    @property
    def total_amount(self) -> float:
        return self._amount + self._tax_calculator.calculate_tax(self._amount)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    amount = 1000.0

    india_invoice = Invoice(amount, IndiaTaxCalculator())
    print(f"Total (India): {india_invoice.total_amount}")

    us_invoice = Invoice(amount, USTaxCalculator())
    print(f"Total (US): {us_invoice.total_amount}")
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `Invoice` class depends only on the `TaxCalculator` interface. To support a new region (e.g. Germany), you simply write a new `GermanyTaxCalculator` class that implements the interface. The `Invoice` class never has to change. It is open for extension (new regions) but closed for modification.

**Intuition.**
- **Mechanism.** OCP relies heavily on polymorphism. The core logic operates on interfaces, and new behaviour is plugged in by passing new implementations.
- **Concrete bite.** When you travel to the UK, your Indian charger doesn't fit the wall socket. Instead of modifying the charger, you use a travel adapter. The adapter extends the charger's usability without altering its internals.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Code should be written so that adding new features does not require altering existing, stable code. Use interfaces and polymorphism to allow extensions.

</div>

## 3. Liskov Substitution Principle (LSP)

If `S` is a subtype of `T`, then objects of type `T` may be replaced with objects of type `S` without altering the correctness of the program. This means that any subclass should be substitutable for its parent class without breaking the functionality.

The classic violation of LSP is making a `Square` inherit from a `Rectangle`.

```java run
// ⚠️ ANTI-PATTERN — do not copy it.
class Rectangle {
    int width, height;

    void setWidth(int w) { width = w; }
    void setHeight(int h) { height = h; }
    int getArea() { return width * height; }
}

class Square extends Rectangle {
    @Override
    void setWidth(int w) {
        width = w;
        height = w; // forces square constraint
    }

    @Override
    void setHeight(int h) {
        height = h;
        width = h; // forces square constraint
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String args[]) {
        Rectangle r = new Square();
        r.setWidth(5);
        r.setHeight(10);
        
        System.out.println("Expected Area: 50");
        System.out.println("Actual Area: " + r.getArea());
    }
}
```
```python run
# ⚠️ ANTI-PATTERN — do not copy it.
class Rectangle:
    def __init__(self) -> None:
        self.width = 0
        self.height = 0

    def set_width(self, w: int) -> None:
        self.width = w

    def set_height(self, h: int) -> None:
        self.height = h

    def get_area(self) -> int:
        return self.width * self.height


class Square(Rectangle):
    def set_width(self, w: int) -> None:
        self.width = w
        self.height = w  # forces square constraint

    def set_height(self, h: int) -> None:
        self.height = h
        self.width = h  # forces square constraint


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    r: Rectangle = Square()
    r.set_width(5)
    r.set_height(10)

    print("Expected Area: 50")
    print(f"Actual Area: {r.get_area()}")
```

**Output:**
```text
@@OUT@@
```

**Analysis.** Calling `setWidth` and `setHeight` on what the caller believes is a `Rectangle` yields an unexpected area of 100 instead of 50. The `Square` broke the unwritten contract of the `Rectangle` (that setting width does not magically alter height).

**Intuition.**
- **Mechanism.** Subclasses must honour the contract (the preconditions and postconditions) of the parent class. They must not introduce unexpected side effects.
- **Concrete bite.** If a pet hotel accepts "pets" (expecting they can be fed, walked, and groomed), accepting a dog is fine. Accepting a snake breaks the system because you cannot walk it. The snake violates the expected behaviour of a "pet".

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** A subclass must behave like its parent in all scenarios expected by the caller. If it cannot, it shouldn't inherit from that parent.

</div>

## 4. Interface Segregation Principle (ISP)

Don't force a class to depend on methods it does not use. Large, "fat" interfaces should be split into smaller, more specific ones so that clients only need to implement the methods that are relevant to them.

Consider a ride-sharing app where riders and drivers share a single `UberUser` interface.

```java run
interface RiderInterface {
    void bookRide();
    void rateDriver();
}

interface DriverInterface {
    void acceptRide();
    void trackEarnings();
    void ratePassenger();
}

class Rider implements RiderInterface {
    public void bookRide() { System.out.println("Booking a ride..."); }
    public void rateDriver() { System.out.println("Rating the driver..."); }
}

class Driver implements DriverInterface {
    public void acceptRide() { System.out.println("Accepting the ride..."); }
    public void trackEarnings() { System.out.println("Tracking earnings..."); }
    public void ratePassenger() { System.out.println("Rating the passenger..."); }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Rider rider = new Rider();
        rider.bookRide();
        
        Driver driver = new Driver();
        driver.acceptRide();
        
        System.out.println("Each class implements only the interface it needs.");
    }
}
```
```python run
from abc import ABC, abstractmethod

class RiderInterface(ABC):
    @abstractmethod
    def book_ride(self) -> None:
        ...

    @abstractmethod
    def rate_driver(self) -> None:
        ...


class DriverInterface(ABC):
    @abstractmethod
    def accept_ride(self) -> None:
        ...

    @abstractmethod
    def track_earnings(self) -> None:
        ...


class Rider(RiderInterface):
    def book_ride(self) -> None:
        print("Booking a ride...")

    def rate_driver(self) -> None:
        print("Rating the driver...")


class Driver(DriverInterface):
    def accept_ride(self) -> None:
        print("Accepting the ride...")

    def track_earnings(self) -> None:
        print("Tracking earnings...")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    rider = Rider()
    rider.book_ride()

    driver = Driver()
    driver.accept_ride()

    print("Each class implements only the interface it needs.")
```

**Output:**
```text
@@OUT@@
```

**Analysis.** By splitting a massive `UberUser` interface into `RiderInterface` and `DriverInterface`, the `Rider` class is not forced to provide empty dummy implementations for `trackEarnings()` or `acceptRide()`.

**Intuition.**
- **Mechanism.** Interfaces define contracts. When an interface covers multiple distinct roles, it forces implementers to carry dead weight. Keep interfaces slim and role-specific.
- **Concrete bite.** When you order an Uber, you see a rider interface. The driver sees a completely different app interface. Software interfaces should be similarly partitioned.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Fat interfaces are bad. Slim, purpose-specific interfaces are good. Clients should not be forced to implement methods they don't use.

</div>

## 5. Dependency Inversion Principle (DIP)

High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details. Details should depend on abstractions.

Rather than high-level classes controlling and depending on the details of lower-level ones, both should rely on interfaces. This makes your code flexible, testable, and easier to maintain.

```java run
interface RecommendationStrategy {
    void getRecommendations();
}

class RecentlyAdded implements RecommendationStrategy {
    public void getRecommendations() {
        System.out.println("Showing recently added content...");
    }
}

class GenreBased implements RecommendationStrategy {
    public void getRecommendations() {
        System.out.println("Showing content based on your favorite genres...");
    }
}

// High-level module depends on the interface, not the concrete classes
class RecommendationEngine {
    private RecommendationStrategy strategy;

    public RecommendationEngine(RecommendationStrategy strategy) {
        this.strategy = strategy;
    }

    public void recommend() {
        strategy.getRecommendations();
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        RecommendationStrategy strategy = new GenreBased(); 
        RecommendationEngine engine = new RecommendationEngine(strategy);
        engine.recommend();
    }
}
```
```python run
from abc import ABC, abstractmethod


class RecommendationStrategy(ABC):
    @abstractmethod
    def get_recommendations(self) -> None:
        ...


class RecentlyAdded(RecommendationStrategy):
    def get_recommendations(self) -> None:
        print("Showing recently added content...")


class GenreBased(RecommendationStrategy):
    def get_recommendations(self) -> None:
        print("Showing content based on your favorite genres...")


class RecommendationEngine:  # high-level module
    def __init__(self, strategy: RecommendationStrategy) -> None:
        self._strategy = strategy

    def recommend(self) -> None:
        self._strategy.get_recommendations()


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    strategy: RecommendationStrategy = GenreBased()  
    engine = RecommendationEngine(strategy)
    engine.recommend()
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `RecommendationEngine` does not hardcode its dependency on `RecentlyAdded`. It accepts any `RecommendationStrategy` passed to it (this is called *dependency injection*). The dependency direction has been inverted: instead of the high-level engine depending on the low-level logic, both depend on the `RecommendationStrategy` interface.

**Intuition.**
- **Mechanism.** Extract the interactions between high-level policy and low-level details into an interface. 
- **Concrete bite.** When you want pizza, you use a food delivery app. You don't care which chef cooks it or who drives the car. The app (abstraction) sits between you (high-level) and the restaurant (low-level). 

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Rely on abstractions (interfaces) rather than concrete implementations. This decouples the components of your system.

</div>

## Summary

| Principle | Meaning | What it prevents |
|---|---|---|
| **SRP** (Single Responsibility) | A class should have one reason to change. | God classes, ripple-effect changes. |
| **OCP** (Open/Closed) | Extend behaviour without editing source code. | Breaking stable code when adding features. |
| **LSP** (Liskov Substitution) | Subclasses must be drop-in replacements. | Unexpected crashes or side-effects when using polymorphism. |
| **ISP** (Interface Segregation) | Don't force clients to implement unused methods. | Fat, unmanageable interfaces. |
| **DIP** (Dependency Inversion) | Depend on abstractions, not concretions. | Tightly coupled, untestable spaghetti code. |

## 🚨 Gotcha Checklist
| Symptom | Likely cause | Fix |
|---|---|---|
| Changing a DB query forces an update to business logic. | **SRP Violation.** The business logic and data access are tangled. | Move DB code into a separate repository or DAO class. |
| Every new requirement adds another `else if` to a massive method. | **OCP Violation.** The method is not closed for modification. | Extract the conditional branches into classes that implement a common interface. |
| A subclass throws `UnsupportedOperationException` for a parent method. | **LSP Violation.** The subclass cannot fulfill the parent's contract. | Rethink the inheritance hierarchy. Use composition instead if the "is-a" relationship is flawed. |
| You are implementing an interface but leaving most methods blank. | **ISP Violation.** The interface is too broad. | Split the interface into smaller, cohesive pieces. |
| You cannot unit test a class without starting the database. | **DIP Violation.** The class directly instantiates the DB connection instead of receiving it via an interface. | Inject an interface (e.g. `UserRepository`) into the class constructor. |

## ✅ Check yourself

```quiz
{
  "prompt": "If you add a new payment gateway to your app and have to modify the `CheckoutProcessor` class to support it, which principle are you violating?",
  "options": [
    "SRP",
    "OCP",
    "LSP",
    "ISP"
  ],
  "answer": "OCP"
}
```

```quiz
{
  "prompt": "Which principle is primarily achieved by injecting interfaces into constructors (Dependency Injection)?",
  "options": [
    "SRP",
    "OCP",
    "LSP",
    "DIP"
  ],
  "answer": "DIP"
}
```

<details>
<summary>How do OCP and DIP work together?</summary>

They are two sides of the same coin. DIP tells you to code against an interface (abstraction) rather than a concrete class. Once your system relies on that interface, OCP allows you to introduce new behaviours simply by providing a new concrete class that implements the interface. DIP provides the structure; OCP is the resulting flexibility.
</details>

## 📚 Sources
- Martin, R. C. (2002). *Agile Software Development, Principles, Patterns, and Practices*. Pearson. (The origin of the SOLID acronym).

<div style="border-left:4px solid #8e155c;background:rgba(142,21,92,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** 
If a `Bird` class has a `fly()` method, and an `Ostrich` class inherits from `Bird` but overrides `fly()` to throw an exception (since ostriches can't fly), which principle is violated?

LSP. Any code that accepts a `Bird` and calls `fly()` will crash when given an `Ostrich`. The subclass fails to substitute for the parent safely. To fix it, you might introduce a `FlyingBird` subclass, or compose behaviour using interfaces like `Flyable`.

</div>

## Your Turn

Look at a recent project you wrote. Pick a class that feels "messy" or hard to test. Apply the SOLID lens: Does it do too much (SRP)? Does it use `new` to hardcode its dependencies (DIP)? How many interfaces could you extract from it to decouple the rest of your system?
