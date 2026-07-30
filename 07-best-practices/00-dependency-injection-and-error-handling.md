---
title: "Dependency Injection & Error Handling"
summary: "Decouple components with DI, then keep systems running with sound exception handling and resilience patterns."
essential: true
---

# Dependency Injection & Error Handling

In today's world of software development, building scalable and maintainable systems is key to ensuring long-term success. One of the essential concepts that play a significant role in achieving this goal is Dependency Injection. This technique allows developers to manage the relationships between various components of a system in a more flexible and efficient manner. By decoupling components from their dependencies, Dependency Injection promotes cleaner, more modular code that is easier to test and maintain.

To gain a better understanding of Dependency Injection, let's begin by examining the problem it aims to solve.

## The Problem

Imagine we are building an OrderService and we write the following code:

```java
// ⚠️ ANTI-PATTERN — this is the version we are about to fix. Do not copy it.
class InventoryService {
    void blockItems(Order order) {
        System.out.println("InventoryService: blocked items for order " + order.id);
    }
}

interface PaymentService {
    void process(Order order);
}

class RazorpayPayment implements PaymentService {
    @Override
    public void process(Order order) {
        System.out.println("RazorpayPayment: charged order " + order.id);
    }
}

class NotificationService {
    void sendConfirmation(Order order) {
        System.out.println("NotificationService: confirmation sent for order " + order.id);
    }
}

class Order {
    String id;
    Order(String id) { this.id = id; }
}

class OrderService {
    private InventoryService inventory = new InventoryService();
    private PaymentService payment = new RazorpayPayment();
    private NotificationService notification = new NotificationService();

    public void checkout(Order order) {
        inventory.blockItems(order);
        payment.process(order);
        notification.sendConfirmation(order);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        OrderService orderService = new OrderService();
        orderService.checkout(new Order("o-1"));
        // OrderService hardcodes RazorpayPayment inside itself — swapping to Stripe,
        // or unit-testing checkout() with a mock PaymentService, means editing this class.
        System.out.println("Violation: OrderService is hardwired to concrete InventoryService, RazorpayPayment, and NotificationService — it cannot be tested or extended without modifying this class.");
    }
}
```

While this code looks simple and functional at first, there are several issues that arise when we try to scale it or make changes:

### Hardcoded Logic

The OrderService is tightly coupled with specific implementations of the InventoryService, PaymentService, and NotificationService. This makes the code rigid. For example, if we want to switch from Razorpay to Stripe, we would need to manually change the code everywhere the RazorpayPayment class is used.

### Difficult to Test

Since the dependencies (InventoryService, PaymentService, and NotificationService) are hardcoded within the OrderService class, it becomes extremely difficult to test the logic of OrderService in isolation.

For example, if we want to test the checkout method, we would need to hit real payment APIs, which is not ideal for unit testing.

### Scalability Issues

As the application grows, we may want to introduce more payment providers, different inventory systems, or notification services. Each time we add a new dependency, we need to modify the OrderService class, which creates scalability issues in larger systems.

Let's now understand how Dependency Injection can help solve these issues and provide a cleaner, more maintainable design.

## Understanding

### What are Dependencies?

In software design, a dependency refers to any object that a class needs in order to function properly. For example, in our earlier OrderService, the dependencies are InventoryService, PaymentService, and NotificationService. These services are needed for the OrderService to carry out its checkout operation.

### Definition

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** Dependency Injection (DI) is a design pattern in which an object receives its dependencies from an external source rather than creating them itself.

</div>

In simple terms, instead of creating objects directly inside a class, you "inject" them from outside.

### Real-life Analogy

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Imagine you are a chef in a restaurant. You need several ingredients (e.g., tomatoes, onions, spices) to cook a dish. Now, instead of growing these ingredients in your garden (creating them yourself), you could simply ask the supplier to deliver them to your kitchen (injecting the dependencies). This way, you don't need to worry about the sourcing of ingredients yourself, making your job simpler and more flexible.

</div>

Similarly, in software development, Dependency Injection allows you to focus on what your class does (like cooking a dish), while an external entity (like a supplier) takes care of providing the necessary dependencies.

### Why Dependency Injection?

- **Flexibility:** It allows you to easily swap out dependencies without changing the core logic of the class.
- **Loose Coupling:** By injecting dependencies, your classes become decoupled from the specific implementations, making your system easier to maintain and extend.
- **Testability:** Since dependencies are injected, it's easier to replace them with mock objects or stubs for unit testing.

## Implementing Dependency Injection

In the previous section, we discussed the issues in the OrderService class. Now, let's see how we can fix these issues using Dependency Injection (DI).

Here is the refactored code using Dependency Injection:

```java
import java.util.*;

class InventoryService {
    void blockItems(Order order) {
        System.out.println("InventoryService: blocked items for order " + order.id);
    }
}

interface PaymentService {
    void process(Order order);
}

class RazorpayPayment implements PaymentService {
    @Override
    public void process(Order order) {
        System.out.println("RazorpayPayment: charged order " + order.id);
    }
}

class NotificationService {
    void sendConfirmation(Order order) {
        System.out.println("NotificationService: confirmation sent for order " + order.id);
    }
}

class Order {
    String id;
    Order(String id) { this.id = id; }
}

class OrderService2 {
    private InventoryService inventory;
    private PaymentService payment;
    private NotificationService notification;

    // Constructor Injection - Dependencies are injected through the constructor
    public OrderService2(InventoryService inventory,
                         PaymentService payment,
                         NotificationService notification) {
        this.inventory = inventory;
        this.payment = payment;
        this.notification = notification;
    }

    public void checkout(Order order) {
        inventory.blockItems(order);
        payment.process(order);
        notification.sendConfirmation(order);
    }
}

// Client-side code
class Main {
    public static void main(String[] args) {
        // Injecting dependencies manually (Constructor Injection)
        OrderService2 orderService2 = new OrderService2(
            new InventoryService(),
            new RazorpayPayment(),
            new NotificationService()
        );

        // Now, we can use the orderService2 to perform operations
        Order order = new Order("o-2");
        orderService2.checkout(order);
    }
}
```

Let's understand how the above code fixes the earlier discussed issues.

### Loose Coupling

In the refactored code, the OrderService2 class no longer creates its dependencies internally. Instead, it receives the required services (InventoryService, PaymentService, and NotificationService) via its constructor. This decouples the class from specific implementations, which makes it more flexible.

### Testability

Since the dependencies are injected, we can now easily provide mock implementations of these services for testing. For example, while testing, we could pass mock services instead of real ones, avoiding the need to hit actual payment gateways or databases.

### Scalability

If we want to switch from Razorpay to Stripe (or any other payment provider), we only need to inject the new PaymentService implementation without touching the OrderService2 class. This makes the system easier to extend and maintain.

### Client-side Dependency Injection

In the client-side code (e.g., in the Main class), we create an instance of OrderService2 and inject its dependencies through the constructor. By doing this, we gain the flexibility to choose which implementations of the dependencies to use.

For example, we can easily swap RazorpayPayment with another payment service, depending on the requirements.

## Advantages of Dependency Injection (DI)

Dependency Injection brings several advantages to software design. Here are the key benefits of using DI:

### Swappable Components

Since the dependencies are injected rather than hardcoded, you can easily replace one component with another.

For instance, switching from one payment service to another (e.g., from Razorpay to Stripe) becomes straightforward without changing the core logic of the OrderService.

### Testable with Mocks

With DI, you can inject mock implementations of your services when running tests. This makes unit testing easier because you don't need to call external services (e.g., payment APIs or database operations). You can replace them with mock objects that simulate their behavior.

### Follows Dependency Inversion Principle (D in SOLID)

Dependency Injection adheres to the Dependency Inversion Principle (DIP), one of the key principles of SOLID design. DIP states that high-level modules should not depend on low-level modules; both should depend on abstractions. DI enables this by allowing classes to depend on abstractions (interfaces) instead of concrete implementations.

### Open to Extension, Closed to Modification

This is part of the Open/Closed Principle (O in SOLID), which DI supports. By injecting dependencies, your code is open to extension (e.g., adding new payment types, notification systems, etc.) without modifying existing classes. You can extend the system by simply adding new implementations, without touching the core code.

## Types of Dependency Injection (DI)

There are three main types of Dependency Injection. Let's dive deep into each type.

### Constructor Injection

Constructor Injection is the most commonly used form of Dependency Injection. In this approach, dependencies are passed to the class via the constructor. This ensures that the class is always instantiated with its required dependencies, which makes it easier to manage and test.

#### Key Points

- **Immutable Dependencies:** Once the dependencies are injected through the constructor, they cannot be changed. This makes the object immutable, which ensures better reliability and predictability.
- **Test-Friendly:** Constructor injection makes testing easier since you can inject mock dependencies during unit testing, isolating the class under test.
- **Ensures Required Dependencies:** Since all required dependencies must be provided when the object is created, you are guaranteed that the class will always have everything it needs to function properly.

#### Example Code

```java
// Using Constructor Injection
interface PaymentService {
    void process(Order order);
}

class Order {
    String id;
    Order(String id) { this.id = id; }
}

class OrderService {
    private final PaymentService payment;

    // Constructor
    public OrderService(PaymentService payment) {
        this.payment = payment;
    }

    public void checkout(Order order) {
        payment.process(order);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        PaymentService payment = order -> System.out.println("Charged order " + order.id);
        OrderService orderService = new OrderService(payment);
        orderService.checkout(new Order("o-3"));
    }
}
```

### Setter Injection

In Setter Injection, dependencies are passed to the class via setter methods after the object has been created. This allows for mutable dependencies, meaning you can change the dependencies of the class at runtime.

#### Key Points

- **Mutable Dependencies:** In Setter Injection, dependencies can be set or changed at any time after the object is created, which gives more flexibility in some scenarios. This contrasts with Constructor Injection, where dependencies are only set at the time of object creation and cannot be changed later.
- **Less Strict:** Unlike constructor injection, where all dependencies are required, setter injection allows for optional dependencies.
- **Can Be Misused:** One drawback is that the dependencies may not be properly set if the setter method is not called. This can lead to situations where a class is not fully initialized.

#### Example Code

```java
// Using Setter Injection
interface PaymentService {
    void process(Order order);
}

class Order {
    String id;
    Order(String id) { this.id = id; }
}

class OrderService {
    private PaymentService payment;

    // Setter method to inject dependencies
    public void setPayment(PaymentService payment) {
        this.payment = payment;
    }

    public void checkout(Order order) {
        payment.process(order);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        OrderService orderService = new OrderService();
        orderService.setPayment(order -> System.out.println("Charged order " + order.id));
        orderService.checkout(new Order("o-4"));
    }
}
```

### Interface Injection

In Interface Injection, the dependency provides an injector method that will inject the dependency into the class. This type is rarely used in practice and is typically only suitable for very specific cases.

#### Key Points

- **Rarely Used:** This type of DI is not as commonly used as constructor or setter injection. It requires changes to the interfaces themselves and may not always be suitable for all applications.
- **Requires Interface Changes:** Since the class must implement an interface that provides the injection method, it can require significant changes to existing interfaces.
- **Unnecessary Method Implementation:** A drawback of Interface Injection is that every class implementing the interface is required to implement the injectPayment method, even if the class does not need a payment service. This can lead to unnecessary method definitions and potential code bloat in some cases.

#### Example Code

```java
// Interface to inject PaymentService dependency
interface PaymentInjectable {
    // Method to inject PaymentService
    void injectPayment(PaymentService payment);
}

interface PaymentService {
    void process(Order order);
}

class Order {
    String id;
    Order(String id) { this.id = id; }
}

// Using Interface Injection
class OrderService implements PaymentInjectable {
    private PaymentService payment;

    // Inject PaymentService through the method
    @Override
    public void injectPayment(PaymentService payment) {
        this.payment = payment; // Set the injected payment service
    }


    public void checkout(Order order) {
        payment.process(order);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        OrderService orderService = new OrderService();
        orderService.injectPayment(order -> System.out.println("Charged order " + order.id));
        orderService.checkout(new Order("o-5"));
    }
}
```

## Best Practices for Implementing Dependency Injection in Java

The below code contains the best practices for implementing Dependency Injection in Java.

```java
// ── Contract: defines what the client needs, not how it is done
interface NotificationService {
    void send(String message);
}

// ── Concrete implementation of the contract
class EmailNotificationService implements NotificationService {
    @Override
    public void send(String message) {
        System.out.println("Email sent: " + message);
    }
}

// ── Client that depends on the abstraction, not the implementation
class UserService {
    // Dependency held as an interface, promoting loose coupling
    private final NotificationService notificationService;

    // Constructor Injection: forces the caller to supply the dependency up-front
    public UserService(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    // Business logic uses the injected service
    public void register(String user) {
        System.out.println("User registered: " + user);
        notificationService.send("Welcome " + user);
    }
}

// ── Composition Root: the only place where “new” keywords appear
class Main {
    public static void main(String[] args) {
        // Create the concrete dependency
        NotificationService service = new EmailNotificationService();

        // Inject it into the client
        UserService userService = new UserService(service);

        // Execute business operation
        userService.register("alex");
    }
}
```

**The same idea in Python**

```python
from abc import ABC, abstractmethod


# Contract: defines what the client needs, not how it is done.
# Java's `interface` has no direct Python analogue — abc.ABC + @abstractmethod
# makes the contract explicit and fails fast (a subclass missing `send`
# cannot even be instantiated), instead of relying on duck typing alone.
class NotificationService(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        ...


# Concrete implementation of the contract
class EmailNotificationService(NotificationService):
    def send(self, message: str) -> None:
        print(f"Email sent: {message}")


# Client that depends on the abstraction, not the implementation
class UserService:
    def __init__(self, notification_service: NotificationService) -> None:
        # Constructor Injection: forces the caller to supply the dependency up-front
        self._notification_service = notification_service

    def register(self, user: str) -> None:
        print(f"User registered: {user}")
        self._notification_service.send(f"Welcome {user}")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    # Composition Root: the only place a concrete class gets instantiated
    service = EmailNotificationService()
    user_service = UserService(service)
    user_service.register("alex")
```

### Why this approach is considered best-practice

| Reason | How the code achieves it |
| --- | --- |
| Depends on abstractions | UserService holds a NotificationService interface, not a concrete class. |
| Constructor Injection ensures completeness | Objects can’t be created without their required dependencies, preventing partially-initialized states. |
| Immutability & Thread-safety | Dependencies are final; once injected they can’t change, making the object safer to use across threads. |
| Single Responsibility | Only the composition root (Main) knows about concrete classes; the rest of the code focuses purely on business logic. |
| Easy swapping & testing | Swap EmailNotificationService with SmsNotificationService, or inject a mock in tests, without touching UserService. |
| Adheres to SOLID (DIP & OCP) | High-level modules depend on interfaces, and new notification channels can be added without modifying existing code. |

## When Dependency Injection is Not Needed

While Dependency Injection (DI) is a powerful design pattern, it is not always necessary. Here are some situations where DI may not be needed:

### Tiny Classes with zero dependencies

If a class is small and doesn't rely on any other services or components, there is no need to introduce DI. The simplicity of such classes doesn't justify the added complexity of dependency injection.

### Static utility classes

Static classes that provide utility functions (like string manipulation or date handling) don't require DI because they don't have any instance dependencies. Their behavior remains the same across all calls and does not change based on external factors.

### One-off scripts or tools

For small, isolated scripts or tools used just once, the overhead of introducing DI might not be necessary. In such cases, simplicity and direct implementation may be more efficient than using a design pattern like DI.

## When to Use Dependency Injection

It is best suggested to use Dependency Injection when you see the following symptoms:

### Classes use new for internal collaborators

If classes are directly creating instances of their dependencies (using new), this tight coupling makes them hard to test and maintain. DI helps in breaking this coupling by injecting dependencies externally.

### Cannot mock services in tests

When your classes create their dependencies internally, it becomes difficult to replace them with mock objects during testing. DI allows you to inject mock dependencies, making unit testing much easier.

### Adding feature branches old code

If adding new features causes existing code to break or requires you to modify many parts of the system, it could be a sign of poor separation of concerns. DI helps by making dependencies more modular, reducing the impact of changes.

### Too many if statements to switch service type

If your code is full of if or switch statements to handle different types of services or behaviors, DI can help by injecting the correct service implementation dynamically, based on the configuration or environment.

### Table for Symptoms and DI Solutions

| Symptom | Fix with DI |
| --- | --- |
| Classes use new for internal collaborators | Constructor Injection |
| Cannot mock services in tests | Inject dependency via interface |
| Adding feature breaks old code | Use abstraction and inject |
| Too many if / switch for service type | Inject strategy implementation |

## Framework Dependency Injection (DI) with Spring

Till now, we have seen how to manually implement Dependency Injection via the three methods discussed earlier. However, there is another more efficient way to implement DI, which is through frameworks like Spring.

With Framework DI, the DI process is handled automatically by the framework itself. In Spring, dependencies are injected using annotations like @Autowired or @Inject. This eliminates the need for manually wiring objects, making the code cleaner, more scalable, and easier to maintain. The framework takes care of creating and managing dependencies, reducing boilerplate code and improving application structure.

## Exception Handling

In software development, errors are inevitable. Whether it's a simple typo or a complex issue in your code, errors can disrupt the normal flow of a program. To ensure that a program continues running smoothly despite these unexpected challenges, developers use strategies to handle errors effectively. Exception handling is one such approach that helps programmers manage errors in a controlled way, allowing the program to recover or provide useful feedback to the user.

Throughout this article, we will explore how exception handling works, why it’s essential for robust software development, and how it can be implemented in various programming languages. By understanding these concepts, you will be better equipped to write resilient and user-friendly applications.

### Problem Statement: Payment Gateway in Amazon

Imagine you're building a payment gateway for Amazon. As a developer, you always focus on designing the "happy path", which refers to the expected sequence of events that occurs during a successful checkout. Here's how it works:

- **Add items to the cart** – The user selects items they want to purchase.
- **Cart accumulation** – The cart accumulates the selected items and calculates the total price.
- **Add delivery address** – The user provides their shipping information.
- **Checkout** – The user proceeds to payment and enters an OTP (One-Time Password) for security.

This flow typically works smoothly when everything goes as expected. However, problems arise when things don’t go according to plan.

### The Problem

In our case, let's consider what happens when, after the user enters the OTP on the checkout page, the OTP is not delivered. The user is now stuck at the page with an error message such as, "Something went wrong", without any clear direction on how to proceed.

This situation highlights the need for effective exception handling, as users encounter errors that prevent them from completing the checkout process. We'll see how exception handling can help manage such situations in the next section.

### Impact of Poor Exception Handling

Poor exception handling can lead to several negative outcomes, both for the user and the business:

#### Failed Transactions

A payment failure, for example, can leave customers frustrated and may result in lost sales. If not handled properly, the customer may abandon the transaction altogether.

#### Angry Customers

Users who encounter errors without clear information or a way to resolve the issue will likely become upset. This negative experience can drive them away from your platform, affecting customer loyalty.

#### Cart Abandonment

In e-commerce platforms like Amazon, users who experience issues at checkout, such as OTP failures, may abandon their shopping cart altogether. This leads to missed revenue opportunities.

#### Bad Public Relations (PR)

If customers experience repeated issues, especially without a clear way to resolve them, they may share their frustrations on social media or review sites. This can harm the company’s public image and reputation, impacting future business.

### Good Exception Handling Practices

When handling errors, it is crucial to ensure that the system responds to exceptions in a way that minimizes the negative impact on both the user experience and the business. A good exception handling strategy involves several key actions:

#### Show a Proper Error Message

The user should always be informed of the issue in a clear and friendly manner. A vague error message like "Something went wrong" doesn’t help. Instead, users should be provided with a specific message about what went wrong and possible next steps.

#### Log the Root Cause

It's essential to track and log the underlying cause of the problem. This helps the development team diagnose and resolve the issue quickly, ensuring that it doesn’t happen again.

#### Trigger Alerts

Alerts, such as Slack notifications or PagerDuty alerts, should be triggered when critical issues occur. This ensures that the right team is immediately aware of the problem and can begin addressing it right away.

#### Retry in Safe Flows

In some cases, a transient issue might resolve itself, so it’s important to implement retry logic in safe flows. For example, if the OTP isn't delivered, the system could automatically retry the process after a brief delay, or prompt the user to try again.

#### Fail Gracefully

If an error cannot be avoided or fixed immediately, the system should fail gracefully. This means maintaining the integrity of the rest of the application and providing the user with an option to continue without feeling completely blocked by the error.

### Approaches to Handle Errors

In the context of exception handling and system design, the terms fail-fast and fail-safe refer to two different approaches to handling errors and unexpected situations in software. Let's dive deeper into each of these approaches, explore their differences, and look at real-world examples to help clarify the concepts.

#### Fail-Fast

A fail-fast system detects errors early and stops further execution to prevent invalid states. This approach ensures problems are caught quickly, making it easier to debug.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Imagine a car with a safety system that immediately alerts you or stops the engine if it detects a problem (like low tire pressure), preventing further damage.

</div>

```java
class Product {
    String id;
    String name;
    Product(String id, String name) { this.id = id; this.name = name; }
}

class ProductRepo {
    Product find(String productId) {
        return new Product(productId, "Wireless Mouse");
    }
}

class ProductServiceFailFirst {
    private final ProductRepo productRepo = new ProductRepo();

    public Product getProduct(String productId) {
        if (productId == null) throw new IllegalArgumentException("Product ID cannot be null");
        // fail-fast for invalid input
        return productRepo.find(productId);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        ProductServiceFailFirst service = new ProductServiceFailFirst();
        Product product = service.getProduct("p-1");
        System.out.println("Fetched: " + product.name);

        try {
            service.getProduct(null);
        } catch (IllegalArgumentException e) {
            System.out.println("Fail-fast rejected the call: " + e.getMessage());
        }
    }
}
```

**The same idea in Python**

```python
from typing import Optional


class Product:
    def __init__(self, id_: str, name: str) -> None:
        self.id = id_
        self.name = name


class ProductRepo:
    def find(self, product_id: str) -> Product:
        return Product(product_id, "Wireless Mouse")


class ProductServiceFailFirst:
    def __init__(self) -> None:
        self._product_repo = ProductRepo()

    def get_product(self, product_id: Optional[str]) -> Product:
        if product_id is None:
            raise ValueError("Product ID cannot be null")  # fail-fast for invalid input
        return self._product_repo.find(product_id)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    service = ProductServiceFailFirst()
    product = service.get_product("p-1")
    print(f"Fetched: {product.name}")

    try:
        service.get_product(None)
    except ValueError as e:
        print(f"Fail-fast rejected the call: {e}")
```

In this example:

- The method checks if the productId is null right away.
- If it is, it throws an IllegalArgumentException and stops further execution.
- This ensures that the function doesn’t proceed with invalid input, preventing errors later in the process.

The system fails immediately when invalid input is detected, ensuring that no inconsistent or incorrect data is processed.

**Advantages**

- Early error detection
- Easier debugging
- Improved system reliability

**Disadvantages**

- May disrupt user experience
- Needs thorough testing

#### Fail-Safe

A fail-safe system continues running despite errors, using fallback mechanisms to minimize disruption. It ensures the system remains operational even when a failure occurs.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** In aviation, if one engine fails, the secondary engine kicks in to ensure the plane continues flying safely.

</div>

```java
// Search Product in any of the websites..
class Product {
    String id;
    String name;
    Product(String id, String name) { this.id = id; this.name = name; }
}

class ProductRepo {
    Product find(String productId) {
        throw new RuntimeException("catalog service unavailable");
    }
}

class ProductServiceFailSafe {
    private final ProductRepo productRepo = new ProductRepo();

    public Product getProduct(String productId) {
        try {
            return productRepo.find(productId);
        } catch (Exception e) {
            // fail-safe: return default
            return new Product("default", "Fallback Product");
        }
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        ProductServiceFailSafe service = new ProductServiceFailSafe();
        Product product = service.getProduct("p-1");
        System.out.println("Fetched: " + product.name);
    }
}
```

**The same idea in Python**

```python
class Product:
    def __init__(self, id_: str, name: str) -> None:
        self.id = id_
        self.name = name


class ProductRepo:
    def find(self, product_id: str) -> Product:
        raise RuntimeError("catalog service unavailable")


class ProductServiceFailSafe:
    def __init__(self) -> None:
        self._product_repo = ProductRepo()

    def get_product(self, product_id: str) -> Product:
        try:
            return self._product_repo.find(product_id)
        except Exception:
            # fail-safe: return default
            return Product("default", "Fallback Product")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    service = ProductServiceFailSafe()
    product = service.get_product("p-1")
    print(f"Fetched: {product.name}")
```

In this example:

- If productRepo.find(productId) fails, the catch block kicks in.
- Rather than crashing the system or throwing an error, the system returns a default product.
- This ensures the system continues to function and offers a smoother experience to the end user.

This is a classic fail-safe behavior, so we keep the system running by degrading gracefully.

**Advantages**

- Ensures system continuity
- Reduced risk of complete failure
- Better user experience

**Disadvantages**

- Potential for hidden issues
- More complex to implement

#### Comparison between Fail-fast and Fail-safe

| Aspect | Fail-fast | Fail-safe |
| --- | --- | --- |
| Error Detection | Immediately | At the point of critical failure |
| Impact on System | Halts execution | Continues with fallback mechanisms |
| User Experience | May disrupt the user | Minimizes disruption |
| When to Use | Use when ensuring data integrity is crucial, such as in payment processing or financial transactions. | Use when the system must continue functioning even during a failure, such as in healthcare or transportation systems. |

### Checked Exceptions

A Checked Exception is a type of exception in programming that is explicitly checked by the compiler during the compilation process. These exceptions are typically errors that a program might encounter during its normal operation, and the compiler forces the programmer to handle these exceptions explicitly in the code.

#### Formal Definition

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** In languages like Java, Checked Exceptions are exceptions that must be either caught (handled) using a try-catch block or declared in the method signature using the throws keyword.

</div>

The compiler checks whether the programmer has handled or declared these exceptions, ensuring that the program doesn't ignore potential errors that could occur during runtime.

Checked exceptions typically represent recoverable conditions, such as file I/O errors, database connection issues, or network timeouts. These exceptions must be handled properly to prevent the program from terminating unexpectedly.

#### Key Points

- **Compiler Enforced Handling:** The compiler requires that the programmer either catch the exception with a try-catch block or declare it in the method signature using the throws keyword.
- **Recoverable Errors:** These exceptions generally occur in conditions that can be recovered from, such as trying to open a file that doesn't exist, or failing to connect to a database. The programmer is expected to handle these scenarios gracefully.
- **Examples in Java:**
  - **IOException:** Happens during file I/O operations, such as reading or writing a file that may not be accessible.
  - **SQLException:** Thrown when there’s a problem with the database connection or query execution.

#### Example Code

Here is a simple example that demonstrates a Checked Exception (IOException):

```java
import java.io.*;

class Main {
    public void readFile(String filePath) throws IOException {
        FileReader reader = new FileReader(filePath);  // This may throw an IOException
        BufferedReader bufferedReader = new BufferedReader(reader);
        String line = bufferedReader.readLine();
        System.out.println(line);
        bufferedReader.close();
    }

    public static void main(String[] args) {
        Main example = new Main();
        try {
            example.readFile("somefile.txt"); // Must handle the IOException
        } catch (IOException e) {
            System.out.println("An error occurred while reading the file: " + e.getMessage());
        }
    }
}
```

In this example:

- The readFile method declares that it may throw an IOException using the throws keyword.
- The calling code (in the main method) must either handle the exception using a try-catch block or propagate it further.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **No Python translation here.** Python has no checked exceptions — there is no `throws` clause, so
the compiler never forces a caller to handle anything. Every Python exception behaves like Java's
unchecked ones: `try/except` and `finally` are how you *choose* to handle one, and a `with` block
(context manager) is the idiomatic replacement for Java's try-with-resources, but nothing enforces
that you do either. An approximate "checked exception" block would misrepresent that difference, so
none is given.

</div>

#### Advantages of Checked Exceptions

- **Prevents Unhandled Errors:** By requiring explicit handling, checked exceptions reduce the likelihood of uncaught exceptions causing the program to crash unexpectedly.
- **Encourages Robust Code:** Programmers are forced to consider error handling, which results in more resilient and fault-tolerant software.

#### Disadvantages of Checked Exceptions

- **Increased Boilerplate Code:** Checked exceptions force developers to write additional try-catch blocks or throws declarations, leading to more code and potential complexity.
- **Overuse Can Lead to Clutter:** Excessive handling of checked exceptions in code can lead to overly verbose or cluttered code, making it harder to maintain and read.

#### When to Use Checked Exceptions

- **External Resources:** When the program interacts with external resources like files, databases, or networks, where errors are expected and can be handled.
- **Recoverable Conditions:** When the program can recover from the exception by retrying the operation, alerting the user, or attempting alternative methods.
- **Client-Provided Input:** When the client (user or system) provides input, such as file paths, database credentials, or network settings. If invalid input is provided, exceptions can occur, and the program must handle these cases, often by prompting the user for corrections or fallback actions.

### Unchecked Exceptions

Unchecked Exceptions are exceptions that the compiler does not require to be explicitly handled or declared in the method signature. These exceptions typically represent programming bugs, such as logic errors or incorrect API usage, and they often cannot be easily recovered from at runtime.

#### Formal Definition

In languages like Java, Unchecked Exceptions are exceptions that do not need to be declared in the throws clause, nor do they require handling using try-catch blocks. They are subclasses of RuntimeException and are usually thrown due to issues in the code that should be fixed by the developer.

Unchecked exceptions are typically used for errors that are beyond the control of the program's flow, such as null pointer references, array index out-of-bounds errors, or invalid type casts. These exceptions often signal that there is a bug in the code that needs to be fixed, rather than something that should be handled by error-handling mechanisms.

#### Key Points

- **No Compiler Requirement to Handle:** The compiler does not require the programmer to handle unchecked exceptions, so they do not need to be caught or declared in method signatures.
- **Represents Programming Bugs:** These exceptions usually indicate errors in the code, such as logic mistakes or invalid assumptions, that should be fixed rather than handled at runtime.
- **Examples in Java:**
  - **NullPointerException:** Thrown when trying to use a reference that points to null.
  - **ArrayIndexOutOfBoundsException:** Thrown when an invalid index is accessed in an array.
  - **ClassCastException:** Thrown when trying to cast an object to a type it is not an instance of.

### Custom Exceptions

Custom Exceptions are user-defined exception classes tailored to your application's specific domain. Rather than relying on generic exceptions (like IOException or NullPointerException), custom exceptions allow you to define more meaningful, application-specific errors that align with your business logic.

#### Formal Definition

In programming, a Custom Exception is a class that extends an existing exception class (often Exception or RuntimeException) to represent a specific error scenario in your application. Custom exceptions allow you to handle domain-specific errors in a structured and meaningful way, making your error handling more expressive and easier to maintain.

Unlike standard exceptions, custom exceptions enable developers to create their own error types that are directly tied to their application’s needs. These exceptions are usually thrown to indicate situations that require special handling or user notification.

#### Why Use Custom Exceptions?

- **Expressive Code:** Custom exceptions allow developers to make their error-handling code more expressive and relevant to the application’s context. Instead of catching general exceptions, you catch exceptions that directly map to your business rules.
- **Maintainable Code:** Custom exceptions make it easier to maintain your code. For example, if a specific domain-related error occurs, you can handle it separately from other types of errors, keeping your error-handling logic clean and organized.
- **Debugging:** Custom exceptions provide meaningful names and messages that make it easier to debug issues related to specific business logic.

#### Example Code

Let’s assume we are building a service in an online learning platform that checks whether a user has access to a particular course. If a user doesn’t have the required subscription or access level, we want to throw a custom exception to indicate this clearly.

```java
// Custom Exception
class CustomerNotPlusException extends RuntimeException {
    public CustomerNotPlusException(String userId) {
        super("User " + userId + " is not a plus customer");
    }
}

class CourseService {
    public void accessCourse(String userId) {
        if (!hasAccess(userId)) {
            // Throwing the custom exception if the user doesn't have access
            throw new CustomerNotPlusException(userId);
        }
        // continue enrollment...
    }

    private boolean hasAccess(String userId) {
        // Logic to check if the user is a Plus customer from the database
        return false;  // For the sake of this example, assume the user doesn't have access
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        CourseService courseService = new CourseService();
        try {
            courseService.accessCourse("u-42");
        } catch (CustomerNotPlusException e) {
            System.out.println("Blocked: " + e.getMessage());
        }
    }
}
```

**The same idea in Python**

```python
class CustomerNotPlusException(Exception):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"User {user_id} is not a plus customer")


class CourseService:
    def access_course(self, user_id: str) -> None:
        if not self._has_access(user_id):
            # Raising the custom exception if the user doesn't have access
            raise CustomerNotPlusException(user_id)
        # continue enrollment...

    def _has_access(self, user_id: str) -> bool:
        # Logic to check if the user is a Plus customer from the database
        return False  # For the sake of this example, assume the user doesn't have access


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    course_service = CourseService()
    try:
        course_service.access_course("u-42")
    except CustomerNotPlusException as e:
        print(f"Blocked: {e}")
```

In this example:

- The accessCourse method checks if the user has access to the course using the hasAccess method.
- If the user doesn't have access, a CustomerNotPlusException (Custom Exception) is thrown, and the message includes the userId, indicating the specific user who attempted the access.

#### When to Use Custom Exceptions

- **To Represent Specific Domain Errors:** When a particular scenario in your application needs to be captured with a unique error message, such as UserNotFoundException or ProductOutOfStockException.
- **To Wrap Lower-Level Exceptions:** When you need to abstract lower-level errors, such as database connection issues, and present them in a more user-friendly way.
- **For Clear Separation of Concerns:** Custom exceptions allow you to separate different types of errors (validation errors, network errors, etc.), making your error handling clearer and more structured.
- **When Building APIs:** Custom exceptions are helpful when building APIs, as they allow you to define specific error codes and messages that clients can handle easily. For instance, an API might return InvalidRequestException when the input request is malformed.

### Conclusion

In conclusion, exception handling is a critical part of writing robust and reliable software. By understanding the different types of exceptions (checked, unchecked, and custom), you can design error-handling mechanisms that make your code more maintainable, expressive, and user-friendly. Whether it's ensuring the integrity of data, gracefully handling errors, or providing meaningful error messages, proper exception handling allows your application to function smoothly, even in the face of unexpected issues. As you continue to develop applications, mastering exception handling will significantly improve the stability and quality of your software.

## Building Resilient System

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** In today’s fast-paced, interconnected world, systems are increasingly required to perform flawlessly, even in the face of failure. Imagine a high-speed train making its way through a busy city. To ensure the train runs smoothly, there are numerous backup systems in place like backup power, maintenance teams, signaling systems, and fail-safe measures. Even if one component fails, the train continues running smoothly, thanks to these safety nets. This analogy of the high-speed train perfectly illustrates the essence of resilience in systems.

</div>

In the same way, modern software systems, networks, and infrastructures must be designed to withstand failures and continue functioning seamlessly. Whether it’s handling a sudden surge in traffic, recovering from unexpected outages, or ensuring data is always available, resilience plays a pivotal role in maintaining system reliability and user trust.

Understanding how to build resilient systems is essential for anyone involved in system architecture, software development, or infrastructure management. The goal is to design systems that not only deliver exceptional performance but also recover gracefully when failure strikes. In a world where system downtime can result in significant financial and reputational loss, building resilient systems has become a top priority.

Before we dive deeper into the specific techniques and strategies for building resilient systems, let’s first define a few key terminologies to ensure we’re all on the same page.

### Key Terminologies

#### Error Handling

Error handling is the process of anticipating, detecting, and resolving issues during system execution. It ensures that a system responds to failure gracefully without corrupting data or collapsing the user experience. Effective error handling includes mechanisms for capturing errors, logging them, and providing meaningful feedback to users or system administrators.

In resilient systems, error handling goes beyond merely catching exceptions; it’s about maintaining the system’s stability and performance even when something goes wrong.

#### Resilience

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** Resilience refers to the system’s ability to absorb failure and continue operating. Robust systems recover from failure, while brittle systems crash. Resilience is not about avoiding failure but about surviving it and ensuring minimal disruption to service. A resilient system is designed to handle unexpected events, recover quickly from failures, and maintain a consistent user experience.

</div>

Resilience is crucial in systems where uptime and continuous service are vital, such as in financial services or healthcare applications.

### Robust System vs. Brittle System

When building resilient systems, it's crucial to understand the difference between robust and brittle systems.

A robust system can gracefully degrade in performance or continue working with limited functionality even if part of the system fails. A brittle system, on the other hand, is prone to complete failure when faced with issues or when one component goes down.

Let's now understand the difference between the two systems:

| Characteristic | Robust System | Brittle System |
| --- | --- | --- |
| System Behavior | Continues on demand gracefully. | Crashes or freezes. |
| Error Handling | Shows cached content or provides degraded service. | Entire system halts on error. |
| Example | Netflix showing cached content when the service is down. | Amazon checkout page crashes if payment service is down. |
| User Experience | Minimizes disruption to the user experience. | User experience is severely disrupted. |
| Recovery from Failures | Can recover or continue with limited functionality. | Fails completely with no fallback. |
| Example Scenario | Amazon checkout page hides recommendation services when the checkout fails. | Amazon checkout fails when payment service is down. |

#### Explanation with Real-World Example

Imagine you're shopping on Amazon. When you try to purchase an item, the Amazon checkout page is a critical part of the transaction. If this page is part of a brittle system, and the payment service goes down, the entire checkout process may fail, causing the user to abandon the purchase and leading to a negative experience.

However, if Amazon's checkout page is designed as a robust system, even if the payment service fails, the system could still allow the user to complete the purchase by hiding the recommendation service or by offering the ability to retry. This ensures that the user can still proceed without facing a complete breakdown, demonstrating how a robust system maintains functionality under partial failure.

### Graceful Degradation Strategies

#### 1. Return Cached Data

When a live service or an external API fails, the system can fall back on cached data to provide a seamless experience to the user. This strategy ensures that even if the primary service is unavailable, the system continues functioning using stored, potentially outdated, data.

In the provided code snippet, we have a RecommendationService class that fetches user recommendations. Here's how it works:

```java
import java.util.*;

class RecommendationCache {
    List<String> getCachedRecommendations(String userId) {
        return List.of("cached-movie-1");
    }
}

class Logger {
    void warn(String message) {
        System.out.println("[WARN] " + message);
    }
}

// The live recommendation service — a separate collaborator, injected in.
class LiveRecommendationClient {
    private final boolean reachable;

    LiveRecommendationClient(boolean reachable) {
        this.reachable = reachable;
    }

    public List<String> fetchLiveRecommendations(String userId) {
        if (!reachable) {
            throw new IllegalStateException("live recommendation service unreachable");
        }
        return List.of("movie-1", "movie-2");  // Simulated live recommendation data
    }
}

class RecommendationService {
    private final LiveRecommendationClient recommendationService;
    private final RecommendationCache cacheService = new RecommendationCache();
    private final Logger log = new Logger();

    RecommendationService(LiveRecommendationClient recommendationService) {
        this.recommendationService = recommendationService;
    }

    public List<String> getRecommendedItems(String userId) {
        try {
            // Attempt to fetch live recommendations
            return recommendationService.fetchLiveRecommendations(userId);
        } catch (Exception ex) {
            // If the live service fails, log the error and fall back to cache
            log.warn("Live service failed, falling back to cache");
            return cacheService.getCachedRecommendations(userId);  // Fallback to cached data
        }
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        // Happy path — the live service answers.
        RecommendationService healthy =
                new RecommendationService(new LiveRecommendationClient(true));
        System.out.println("Live:     " + healthy.getRecommendedItems("u-1"));

        // Degraded path — the live service is down, so stale cache is served instead.
        RecommendationService degraded =
                new RecommendationService(new LiveRecommendationClient(false));
        System.out.println("Fallback: " + degraded.getRecommendedItems("u-1"));
    }
}
```

**The same idea in Python**

```python
from typing import List


class RecommendationCache:
    def get_cached_recommendations(self, user_id: str) -> List[str]:
        return ["cached-movie-1"]


# The live recommendation service — a separate collaborator, injected in.
class LiveRecommendationClient:
    def __init__(self, reachable: bool) -> None:
        self._reachable = reachable

    def fetch_live_recommendations(self, user_id: str) -> List[str]:
        if not self._reachable:
            raise RuntimeError("live recommendation service unreachable")
        return ["movie-1", "movie-2"]  # Simulated live recommendation data


class RecommendationService:
    def __init__(self, recommendation_service: LiveRecommendationClient) -> None:
        self._recommendation_service = recommendation_service
        self._cache_service = RecommendationCache()

    def get_recommended_items(self, user_id: str) -> List[str]:
        try:
            # Attempt to fetch live recommendations
            return self._recommendation_service.fetch_live_recommendations(user_id)
        except Exception:
            # If the live service fails, log the error and fall back to cache
            print("[WARN] Live service failed, falling back to cache")
            return self._cache_service.get_cached_recommendations(user_id)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    # Happy path — the live service answers.
    healthy = RecommendationService(LiveRecommendationClient(True))
    print(f"Live:     {healthy.get_recommended_items('u-1')}")

    # Degraded path — the live service is down, so stale cache is served instead.
    degraded = RecommendationService(LiveRecommendationClient(False))
    print(f"Fallback: {degraded.get_recommended_items('u-1')}")
```

In this example:

- The getRecommendedItems method first tries to get the data from the live service by calling fetchLiveRecommendations.
- If the live service fails (e.g., due to a network issue or server downtime), the system catches the exception and logs the failure.
- It then returns the cached recommendations using the cacheService.getCachedRecommendations method, ensuring that the user still gets some content, albeit potentially out-of-date.

This method of graceful degradation keeps the user experience intact by providing fallback data when the system is unable to perform as expected.

This strategy works best when the data doesn’t need to be real-time and can tolerate being stale for short periods, such as user recommendations, product details, or news articles that don't change frequently.

#### 2. Show Fallback UI

When a system or service becomes unavailable, it’s crucial to ensure that users still have a meaningful experience. One of the ways to handle this is by showing a fallback UI.

This could be a message, a static version of the content, or a default view that informs the user of the issue and provides a way forward (e.g., "try again later").

Here’s how the code for showing fallback UI works:

```java
class Menu {
    String content;
    Menu(String content) { this.content = content; }
}

class MenuService {
    Menu fetchMenu(String restaurantId) {
        throw new RuntimeException("menu service timed out");
    }
}

class Main {
    static MenuService menuService = new MenuService();

    // Show fallback UI
    public static Menu getMenu(String restaurantId) {
        try {
            // Attempt to fetch the live menu
            return menuService.fetchMenu(restaurantId);
        } catch (Exception e) {
            // If the live menu is unavailable, show a fallback message in the UI
            return new Menu("Menu currently unavailable. Please try again later.");
        }
    }

    public static void main(String[] args) {
        System.out.println(getMenu("r-1").content);
    }
}
```

In this example:

- The getMenu method tries to fetch the live menu from the menuService.fetchMenu method.
- If the service fails (e.g., the menu is unavailable due to a server issue), the system catches the exception and instead returns a fallback UI in the form of a Menu object with a message: "Menu currently unavailable. Please try again later."

This strategy ensures that users are not left staring at an empty screen or a broken interface. Instead, they are informed that the content they seek is temporarily unavailable, and they can try again later.

This approach is effective for user-facing applications where it’s essential to maintain a friendly and informative experience, even during downtime. Examples of fallback UI include error messages, loading spinners, or simplified versions of the content.

#### 3. Queue Requests

Another graceful degradation strategy is queuing requests. When a service is temporarily unavailable or experiences high traffic, it’s crucial to prevent the system from becoming overloaded or failing outright. By queuing requests, the system can defer the action until the service is ready to process it, ensuring that no requests are lost, and users are not impacted by service interruptions.

```java
class Order {
    String id;
    Order(String id) { this.id = id; }
}

class PaymentService {
    void charge(Order order) {
        throw new RuntimeException("payment gateway unreachable");
    }
}

class RetryQueue {
    void enqueue(Order order) {
        System.out.println("Queued order " + order.id + " for retry");
    }
}

class Logger {
    void warn(String message) {
        System.out.println("[WARN] " + message);
    }
}

class Main {
    static PaymentService paymentService = new PaymentService();
    static RetryQueue orderRetryQueue = new RetryQueue();
    static Logger log = new Logger();

    // Queue request's
    public static void placeOrder(Order order) {
        try {
            // Attempt to charge the payment
            paymentService.charge(order);
        } catch (Exception e) {
            // If payment fails, queue the order for retry
            orderRetryQueue.enqueue(order);
            log.warn("Payment failed. Queued for retry.");
        }
    }

    public static void main(String[] args) {
        placeOrder(new Order("o-6"));
    }
}
```

In this example:

- The placeOrder method attempts to charge the payment for an order.
- If the payment service fails (e.g., due to network issues), the exception is caught, and the order is placed in a retry queue (orderRetryQueue.enqueue(order)).
- A warning is logged to indicate that the payment has failed and the order has been queued for retry.

This ensures that, rather than rejecting the request immediately, the system can retry processing the payment later when the service is available again.

The queueing requests strategy is ideal for handling intermittent failures in high-demand systems. It allows for non-disruptive operations, ensuring that operations are completed when the system can handle them, without burdening the user with error messages or failed transactions.

### Retry Mechanisms

In systems with unreliable or intermittent services, retry mechanisms are essential for improving the user experience during temporary failures. Instead of failing immediately or frustrating users with error messages, a retry mechanism allows the system to attempt the same operation a few times, increasing the chances of success.

There are various retry strategies, each suited to different types of failures and service conditions. Let's explore two of the most common strategies:

#### 1. Naive Retry

The naive retry mechanism simply retries an operation a fixed number of times when it fails. It works well when the service is expected to recover quickly, but it can lead to excessive load on the system if not handled carefully.

Here's an example of the naive retry mechanism:

```java
class EtaService {
    String getETA() {
        throw new RuntimeException("ETA service unavailable");
    }
}

class Logger {
    void warn(String message) {
        System.out.println("[WARN] " + message);
    }
}

class Main {
    static EtaService etaService = new EtaService();
    static Logger log = new Logger();

    // Naive retry example
    public static String getETA() {
        int retries = 3;  // Maximum retry attempts
        while (retries-- > 0) {
            try {
                return etaService.getETA();  // Attempt to fetch ETA from service
            } catch (Exception e) {
                log.warn("Retrying ETA, attempts left: " + retries);
            }
        }
        return "ETA unavailable";  // Return message if all retries fail
    }

    public static void main(String[] args) {
        System.out.println(getETA());
    }
}
```

**The same idea in Python**

```python
class EtaService:
    def get_eta(self) -> str:
        raise RuntimeError("ETA service unavailable")


# Naive retry example
def get_eta() -> str:
    eta_service = EtaService()
    retries = 3  # Maximum retry attempts
    while retries > 0:
        retries -= 1
        try:
            return eta_service.get_eta()  # Attempt to fetch ETA from service
        except Exception:
            print(f"[WARN] Retrying ETA, attempts left: {retries}")
    return "ETA unavailable"  # Return message if all retries fail


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    print(get_eta())
```

In this example:

- The system tries to fetch the ETA from the etaService up to three times.
- If the service fails (due to an exception), the system retries the request until the number of retries is exhausted.
- If all attempts fail, it returns a fallback message "ETA unavailable".

The naive retry mechanism is simple to implement but doesn't account for the possibility of repeated failures, and it can overwhelm the system if retries are not well-managed.

#### 2. Backoff Strategy

A more sophisticated approach is the backoff strategy, which adds a delay between retries, helping to reduce the load on the system and give the service time to recover. A common variation is exponential backoff, where the delay increases after each retry attempt.

Here’s an example of the backoff strategy:

```java
class EtaService {
    String getETA() {
        throw new RuntimeException("ETA service unavailable");
    }
}

class Main {
    static EtaService etaService = new EtaService();

    // Backoff strategy
    public static String getETAWithBackoff() throws InterruptedException {
        int retries = 3;
        int delay = 50; // Shortened from 1000ms for the sandbox; same exponential shape
        while (retries-- > 0) {
            try {
                return etaService.getETA();  // Attempt to fetch ETA from service
            } catch (Exception e) {
                Thread.sleep(delay);  // Wait before retrying
                delay *= 2;  // Exponential backoff: double the delay each time
            }
        }
        return "ETA unavailable";  // Return message if all retries fail
    }

    public static void main(String[] args) throws InterruptedException {
        System.out.println(getETAWithBackoff());
    }
}
```

**The same idea in Python**

```python
import time


class EtaService:
    def get_eta(self) -> str:
        raise RuntimeError("ETA service unavailable")


# Backoff strategy
def get_eta_with_backoff() -> str:
    eta_service = EtaService()
    retries = 3
    delay_ms = 10.0  # shortened for the sandbox; same exponential shape
    while retries > 0:
        retries -= 1
        try:
            return eta_service.get_eta()  # Attempt to fetch ETA from service
        except Exception:
            time.sleep(delay_ms / 1000)  # Wait before retrying
            delay_ms *= 2  # Exponential backoff: double the delay each time
    return "ETA unavailable"  # Return message if all retries fail


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    print(get_eta_with_backoff())
```

In this example:

- After each failed attempt, the system waits for a progressively longer time before retrying.
- Initially, it waits for 1 second, then 2 seconds, then 4 seconds, and so on. This exponential backoff helps in reducing the strain on the system and avoids flooding it with too many requests.

This approach is useful in scenarios where the service is temporarily overwhelmed, giving it a chance to recover between retry attempts.

### Possibility of DDoS due to Retry Mechanisms

#### What is DDoS?

DDoS (Distributed Denial of Service) is a type of cyberattack where multiple systems, often compromised and controlled remotely, are used to flood a target server or network with traffic. The overwhelming volume of requests causes the target system to slow down or crash, denying service to legitimate users.

#### How Retry Mechanisms Can Lead to DDoS

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** While retry mechanisms are crucial for improving resilience, improper implementation can lead to a self-inflicted DDoS on your system.

</div>

Consider this scenario:

- If many users are retrying failed requests at the same time, especially with short or no backoff periods, it can cause a significant spike in requests, overwhelming the system.
- This sudden surge in retries can lead to resource exhaustion, slower response times, and potentially system crashes, much like a DDoS attack.

#### Possible Solutions

To avoid DDoS-like situations while using retry mechanisms:

- Implement exponential backoff (as shown in the backoff strategy) to progressively delay retries, preventing all users from retrying at once.
- Cap the number of retries and set a maximum delay to prevent endless attempts in case of service failure.
- Use circuit breakers to detect persistent failures and stop retrying temporarily, allowing the system to recover instead of continually hammering it with requests.
- Rate limit retries from clients to ensure that not too many retries happen in a short time frame.

By using these strategies, you can reduce the risk of unintentionally overwhelming your system and ensure the service remains available to all users.

### Circuit Breaker Pattern

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** The Circuit Breaker Pattern is a design pattern used to protect a system from repeatedly calling a failing service. Instead of constantly trying to invoke a failing service, the circuit breaker “opens” after a certain number of failures, blocking further attempts and allowing the system to continue operating. This prevents the system from overloading the failing service and gives it time to recover.

</div>

#### The Problem

What happens if a downstream service, such as a payment service, is constantly failing? If the system keeps calling the service, it can lead to wasted resources, further failure, and potentially impact the performance of other components. The Circuit Breaker Pattern addresses this by stopping the calls after a threshold is met, allowing the system to wait and retry later.

#### The Solution

The solution is to implement a circuit breaker that stops sending requests to the failing service after a threshold of failures. Once the service has had time to recover, the circuit breaker enters a "half-open" state to test the service's availability before fully restoring normal operations.

#### States of Circuit Breaker

- **Closed:** The service is working normally, and requests are being sent to the service.
- **Open:** The service is failing consistently, and the circuit breaker stops sending requests to the service.
- **Half-Open:** After a defined timeout, the system sends a limited number of test requests to see if the service has recovered. If these requests succeed, the circuit breaker returns to the "Closed" state.

#### Code Implementation

Here’s how the Circuit Breaker pattern can be implemented using Spring Boot with Resilience4j.

##### 1. Annotation-based Circuit Breaker Setup

The circuit breaker is applied using the @CircuitBreaker annotation, which wraps the method with the defined circuit breaker and fallback mechanism.

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Requires Resilience4j.** This example needs Spring Boot plus the Resilience4j library on the classpath — it won't run in the sandbox editor below.

</div>

```java
// requires: resilience4j — not runnable in the sandbox
@Service
class PaymentService {

    @CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
    public String charge(String userId, double amount) {
        // real payment logic
        return externalPaymentApi.charge(userId, amount);
    }

    // Fallback method in case of failure
    public String paymentFallback(String userId, double amount, Throwable t) {
        log.error("Payment Service Down. Fallback triggered.");
        return "PAYMENT_FAILED";
    }
}
```

- `@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")`: This annotation applies the circuit breaker to the charge method. If it fails, it will trigger the fallback method paymentFallback().
- `paymentFallback()`: This method is invoked if the charge method fails, providing a default value and logging the failure.

##### 2. Java Config Customization

You can also configure the circuit breaker programmatically by using a @Bean method:

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Requires Resilience4j.** This is a Spring `@Bean` configuration method — it needs the framework container to run and won't compile standalone.

</div>

```java
// requires: resilience4j — not runnable in the sandbox
@Bean
public Customizer<CircuitBreakerConfigCustomizer> paymentCircuitBreakerConfig() {
    return CircuitBreakerConfigCustomizer.of("paymentService", builder -> builder
        .slidingWindowSize(10)
        .failureRateThreshold(50)
        .waitDurationInOpenState(Duration.ofSeconds(10))
        .permittedNumberOfCallsInHalfOpenState(2)
        .automaticTransitionFromOpenToHalfOpenEnabled(true));
}
```

This allows you to configure the circuit breaker dynamically at runtime.

##### 3. Configuration via application.yml

You can configure the circuit breaker properties externally in the application.yml file as follows:

```yaml
resilience4j:
  circuitbreaker:
    instances:
      paymentService:
        registerHealthIndicator: true
        slidingWindowSize: 10
        slidingWindowType: COUNT_BASED
        minimumNumberOfCalls: 5
        failureRateThreshold: 50
        waitDurationInOpenState: 10s
        permittedNumberOfCallsInHalfOpenState: 2
        automaticTransitionFromOpenToHalfOpenEnabled: true
```

- `slidingWindowSize`: Defines the number of calls to consider when determining whether the circuit should open.
- `failureRateThreshold`: Defines the failure rate (in percentage) above which the circuit will open.
- `waitDurationInOpenState`: The duration the circuit breaker stays open before transitioning to a half-open state.
- `permittedNumberOfCallsInHalfOpenState`: Number of allowed requests in half-open state before deciding whether to close the circuit.

### Failover and Timeout Strategies

In a resilient system, it's not just about detecting failure, it's about how quickly and effectively the system recovers or reroutes around that failure. Two key techniques that play a major role in this are Timeouts and Failovers. These strategies help ensure that your system doesn't hang indefinitely and can automatically switch to backup options when necessary.

#### 1. Timeout Strategy

A timeout is a mechanism used to prevent long waits or hangs when a service becomes unresponsive. Instead of waiting indefinitely for a response, a timeout defines a maximum amount of time to wait before the request is aborted.

**Why it matters:**

- Prevents resource blockage and thread exhaustion.
- Ensures the calling service doesn't get stuck.
- Allows for fallback or retry logic to kick in promptly.

**Example use case:** Imagine your frontend service calls a backend API to fetch user details. If that backend service is hanging (maybe due to a DB lock), your frontend should timeout in 2 seconds rather than wait endlessly, ensuring your UI remains responsive or shows a graceful error.

#### 2. Failover Strategy

Failover is the process of switching to a standby or alternative service when the primary one is unavailable or down. This is a proactive resilience strategy that ensures high availability and continued service delivery even when components fail.

**Why it matters:**

- Enables seamless experience even during service failures.
- Minimizes downtime and disruption.
- Useful in both service-to-service calls and infrastructure (like DB or servers).

**Example use case:** If you have two payment gateways (say Razorpay and Stripe), and Razorpay is down, the system can automatically failover to Stripe to complete the transaction without the user even noticing.

By combining Timeouts (to avoid hanging) and Failovers (to reroute the request), systems can maintain a smooth and fault-tolerant user experience even in the face of partial or complete component failures.

### Summary: Engineering Checklist

To build a resilient and high-performing system, it's essential to apply various strategies that handle different types of failures, delays, and potential issues. Here’s a summary of key engineering strategies and solutions you can apply to ensure your system remains functional under different circumstances:

#### 1. Temporary Spike

- **Problem:** Sudden bursts in demand or traffic.
- **Solution:** Use retry with backoff to manage the load. This technique helps to handle spikes by spacing out retries with a growing delay, reducing the strain on the system and giving it time to recover.

#### 2. Persistent Failure

- **Problem:** A service or component that is consistently failing.
- **Solution:** Implement a Circuit Breaker to stop calling the failing service after a set threshold. This allows the system to stop wasting resources and enter a recovery mode.

#### 3. Third-party Delay

- **Problem:** Delays caused by external services (e.g., APIs, cloud services).
- **Solution:** Use Timeouts to avoid waiting too long for responses from third-party services. Setting an appropriate timeout ensures that your system doesn’t hang indefinitely and can proceed with a fallback.

#### 4. Degraded Experience

- **Problem:** System continues working, but with reduced functionality.
- **Solution:** Implement Fallback UI on Cache. When live data is unavailable, use cached data or show a degraded user interface to ensure users still have access to important information.

#### 5. Avoid Throttling

- **Problem:** Excessive load on the system or external services due to too many simultaneous requests.
- **Solution:** Use Own Rate Limiting to limit the number of requests your system can make to external services within a specific time frame, ensuring that it doesn't overwhelm any single service.

#### 6. Highly Critical Services

- **Problem:** Critical services must remain operational at all times.
- **Solution:** Implement Failover Setup to ensure that if one critical service goes down, another backup service takes over seamlessly, ensuring high availability and minimal disruption.

By following these strategies, you can ensure that your system is robust, resilient, and capable of handling various real-world challenges. Implementing these solutions will help protect your system from downtime, service failures, and poor user experiences, all while maintaining functionality even in the face of issues.
