---
title: "Routing & Messages"
summary: "Chain of Responsibility, Mediator, Visitor, and Memento — behavioral patterns for decoupling senders from receivers and managing complex interactions."
essential: true
---

# Routing & Messages

As systems grow, direct communication between objects leads to tight coupling. A button shouldn't need to know the memory address of the database service. These patterns focus on routing messages, decoupling senders from receivers, and managing complex networks of interacting objects.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.** You can place intermediary objects between senders and receivers. This allows you to chain handlers, centralize communication, execute operations without changing class structures, or capture snapshots of state.

</div>

**You'll be able to:**
- Pass a request along a chain of handlers until one handles it (Chain of Responsibility).
- Centralize complex communication between objects to prevent a chaotic web of references (Mediator).
- Add new operations to a class hierarchy without modifying the classes themselves (Visitor).
- Capture and restore an object's internal state without violating encapsulation (Memento).

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** As you read, look for the *Mechanism* and *Concrete bite* under each code block. They map the code you just saw to the mental model you need to build.

</div>

1. [Chain of Responsibility Pattern](#1-chain-of-responsibility-pattern)
2. [Mediator Pattern](#2-mediator-pattern)
3. [Visitor Pattern](#3-visitor-pattern)
4. [Memento Pattern](#4-memento-pattern)

## 1. Chain of Responsibility Pattern

The Chain of Responsibility passes a request along a chain of handlers. Upon receiving a request, each handler decides either to process it or to pass it to the next handler in the chain.

Instead of writing a massive block of authentication, logging, and caching checks inside a web controller, you split them into separate middlewares.

```java run
abstract class Logger {
    public static int INFO = 1;
    public static int DEBUG = 2;
    public static int ERROR = 3;

    protected int level;
    protected Logger nextLogger;

    public void setNextLogger(Logger nextLogger) {
        this.nextLogger = nextLogger;
    }

    public void logMessage(int level, String message) {
        if (this.level <= level) {
            write(message);
        }
        if (nextLogger != null) {
            nextLogger.logMessage(level, message);
        }
    }

    abstract protected void write(String message);
}

class ConsoleLogger extends Logger {
    public ConsoleLogger(int level) { this.level = level; }
    protected void write(String message) { System.out.println("Standard Console::Logger: " + message); }
}

class ErrorLogger extends Logger {
    public ErrorLogger(int level) { this.level = level; }
    protected void write(String message) { System.out.println("Error Console::Logger: " + message); }
}

class FileLogger extends Logger {
    public FileLogger(int level) { this.level = level; }
    protected void write(String message) { System.out.println("File::Logger: " + message); }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    private static Logger getChainOfLoggers() {
        Logger errorLogger = new ErrorLogger(Logger.ERROR);
        Logger fileLogger = new FileLogger(Logger.DEBUG);
        Logger consoleLogger = new ConsoleLogger(Logger.INFO);

        errorLogger.setNextLogger(fileLogger);
        fileLogger.setNextLogger(consoleLogger);
        return errorLogger;
    }

    public static void main(String[] args) {
        Logger loggerChain = getChainOfLoggers();

        System.out.println("--- Logging INFO ---");
        loggerChain.logMessage(Logger.INFO, "This is an information.");

        System.out.println("\n--- Logging DEBUG ---");
        loggerChain.logMessage(Logger.DEBUG, "This is a debug level information.");

        System.out.println("\n--- Logging ERROR ---");
        loggerChain.logMessage(Logger.ERROR, "This is an error information.");
    }
}
```
```python run
from abc import ABC, abstractmethod


class Logger(ABC):
    INFO = 1
    DEBUG = 2
    ERROR = 3

    def __init__(self, level: int) -> None:
        self._level = level
        self._next_logger: Logger | None = None

    def set_next_logger(self, next_logger: "Logger") -> None:
        self._next_logger = next_logger

    def log_message(self, level: int, message: str) -> None:
        if self._level <= level:
            self._write(message)
        if self._next_logger:
            self._next_logger.log_message(level, message)

    @abstractmethod
    def _write(self, message: str) -> None: ...


class ConsoleLogger(Logger):
    def _write(self, message: str) -> None:
        print(f"Standard Console::Logger: {message}")


class ErrorLogger(Logger):
    def _write(self, message: str) -> None:
        print(f"Error Console::Logger: {message}")


class FileLogger(Logger):
    def _write(self, message: str) -> None:
        print(f"File::Logger: {message}")


# ── Driver ──────────────────────────────────────────────
def get_chain_of_loggers() -> Logger:
    error_logger = ErrorLogger(Logger.ERROR)
    file_logger = FileLogger(Logger.DEBUG)
    console_logger = ConsoleLogger(Logger.INFO)

    error_logger.set_next_logger(file_logger)
    file_logger.set_next_logger(console_logger)
    return error_logger

if __name__ == "__main__":
    logger_chain = get_chain_of_loggers()

    print("--- Logging INFO ---")
    logger_chain.log_message(Logger.INFO, "This is an information.")

    print("\n--- Logging DEBUG ---")
    logger_chain.log_message(Logger.DEBUG, "This is a debug level information.")

    print("\n--- Logging ERROR ---")
    logger_chain.log_message(Logger.ERROR, "This is an error information.")
```

**Output:**
```text
@@OUT@@
```

**Analysis.** An ERROR message enters the chain. `ErrorLogger` processes it and passes it on. `FileLogger` sees that ERROR > DEBUG, processes it, and passes it on. `ConsoleLogger` sees that ERROR > INFO, processes it, and the chain ends. (Note: standard HTTP middleware usually *stops* the chain when a handler fully resolves a request, rather than propagating it to every handler).

**Intuition.**
- **Mechanism.** Each handler contains a reference to the next handler. It either processes the request or forwards it.
- **Concrete bite.** Tech support. You call the level 1 agent. If they can't help, they pass you to level 2. If level 2 can't help, you go to level 3.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Chain of Responsibility to decouple a request's sender from its receiver, allowing multiple objects a chance to handle it. The cost is that a request might reach the end of the chain unhandled.

</div>

## 2. Mediator Pattern

The Mediator Pattern centralizes complex communications and control logic between objects in a system.

Instead of aircraft communicating directly with each other to avoid collisions (which requires every plane to know the location of every other plane), they all communicate with a central Air Traffic Control tower.

```java run
import java.util.*;

// Mediator interface
interface ChatMediator {
    void sendMessage(String message, User user);
    void addUser(User user);
}

// Concrete Mediator
class ChatRoom implements ChatMediator {
    private List<User> users = new ArrayList<>();

    public void addUser(User user) { users.add(user); }

    public void sendMessage(String message, User sender) {
        for (User user : users) {
            if (user != sender) { // Don't send the message to the sender
                user.receive(message);
            }
        }
    }
}

// Colleague
abstract class User {
    protected ChatMediator mediator;
    protected String name;

    public User(ChatMediator mediator, String name) {
        this.mediator = mediator;
        this.name = name;
    }

    public abstract void send(String message);
    public abstract void receive(String message);
}

class ChatUser extends User {
    public ChatUser(ChatMediator mediator, String name) { super(mediator, name); }

    public void send(String message) {
        System.out.println(this.name + " sends: " + message);
        mediator.sendMessage(message, this);
    }

    public void receive(String message) {
        System.out.println(this.name + " receives: " + message);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        ChatMediator chatRoom = new ChatRoom();

        User user1 = new ChatUser(chatRoom, "Alice");
        User user2 = new ChatUser(chatRoom, "Bob");
        User user3 = new ChatUser(chatRoom, "Charlie");

        chatRoom.addUser(user1);
        chatRoom.addUser(user2);
        chatRoom.addUser(user3);

        user1.send("Hello everyone!");
    }
}
```
```python run
from abc import ABC, abstractmethod
from typing import List


class User(ABC):
    def __init__(self, mediator: "ChatMediator", name: str) -> None:
        self._mediator = mediator
        self._name = name

    @property
    def name(self) -> str: return self._name

    @abstractmethod
    def send(self, message: str) -> None: ...
    @abstractmethod
    def receive(self, message: str) -> None: ...


class ChatMediator(ABC):
    @abstractmethod
    def send_message(self, message: str, sender: User) -> None: ...
    @abstractmethod
    def add_user(self, user: User) -> None: ...


class ChatRoom(ChatMediator):
    def __init__(self) -> None:
        self._users: List[User] = []

    def add_user(self, user: User) -> None:
        self._users.append(user)

    def send_message(self, message: str, sender: User) -> None:
        for user in self._users:
            if user != sender:
                user.receive(message)


class ChatUser(User):
    def send(self, message: str) -> None:
        print(f"{self.name} sends: {message}")
        self._mediator.send_message(message, self)

    def receive(self, message: str) -> None:
        print(f"{self.name} receives: {message}")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    chat_room = ChatRoom()

    user1 = ChatUser(chat_room, "Alice")
    user2 = ChatUser(chat_room, "Bob")
    user3 = ChatUser(chat_room, "Charlie")

    chat_room.add_user(user1)
    chat_room.add_user(user2)
    chat_room.add_user(user3)

    user1.send("Hello everyone!")
```

**Output:**
```text
@@OUT@@
```

**Analysis.** Users don't hold references to other users. They only hold a reference to the `ChatMediator`. This eliminates the many-to-many relationship (where 10 users would require 90 direct references) and replaces it with a one-to-many relationship to the mediator.

**Intuition.**
- **Mechanism.** Extract all communication logic between multiple objects into a dedicated Mediator class. Components communicate only with the Mediator.
- **Concrete bite.** A smart home hub. The motion sensor doesn't talk to the lights directly. It tells the hub it detected motion, and the hub turns on the lights.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Mediator to reduce chaotic dependencies between interacting objects. The cost is that the Mediator can grow into a bloated "God Object" that knows too much about everything.

</div>

## 3. Visitor Pattern

The Visitor Pattern lets you add new operations to existing classes without changing them. 

If you have a complex hierarchy (like a Document with Paragraphs, Images, and Tables) and you want to export it to PDF, HTML, or Markdown, putting an `exportPDF()`, `exportHTML()`, and `exportMD()` method inside every node class breaks the Single Responsibility Principle.

```java run
interface Element {
    void accept(Visitor visitor);
}

class Book implements Element {
    private int price;
    public Book(int price) { this.price = price; }
    public int getPrice() { return price; }
    
    // Double dispatch: the book passes itself to the visitor
    public void accept(Visitor visitor) { visitor.visit(this); }
}

class Fruit implements Element {
    private int pricePerKg;
    private int weight;
    public Fruit(int pricePerKg, int weight) { this.pricePerKg = pricePerKg; this.weight = weight; }
    public int getPrice() { return pricePerKg * weight; }
    
    public void accept(Visitor visitor) { visitor.visit(this); }
}

interface Visitor {
    void visit(Book book);
    void visit(Fruit fruit);
}

class TaxCalculatorVisitor implements Visitor {
    public void visit(Book book) {
        // Books have no tax
        System.out.println("Book tax: 0 (Total: " + book.getPrice() + ")");
    }
    
    public void visit(Fruit fruit) {
        // Fruits have 10% tax
        double tax = fruit.getPrice() * 0.10;
        System.out.println("Fruit tax: " + tax + " (Total: " + (fruit.getPrice() + tax) + ")");
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Element[] items = new Element[]{
            new Book(500), 
            new Fruit(100, 2)
        };
        
        Visitor taxCalc = new TaxCalculatorVisitor();
        
        for (Element item : items) {
            item.accept(taxCalc);
        }
    }
}
```
```python run
from abc import ABC, abstractmethod
from typing import List


class Visitor(ABC):
    @abstractmethod
    def visit_book(self, book: "Book") -> None: ...
    @abstractmethod
    def visit_fruit(self, fruit: "Fruit") -> None: ...


class Element(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None: ...


class Book(Element):
    def __init__(self, price: int) -> None:
        self._price = price

    @property
    def price(self) -> int: return self._price

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_book(self)


class Fruit(Element):
    def __init__(self, price_per_kg: int, weight: int) -> None:
        self._price_per_kg = price_per_kg
        self._weight = weight

    @property
    def price(self) -> int: return self._price_per_kg * self._weight

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_fruit(self)


class TaxCalculatorVisitor(Visitor):
    def visit_book(self, book: Book) -> None:
        print(f"Book tax: 0 (Total: {book.price})")

    def visit_fruit(self, fruit: Fruit) -> None:
        tax = fruit.price * 0.10
        print(f"Fruit tax: {tax:.1f} (Total: {fruit.price + tax:.1f})")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    items: List[Element] = [Book(500), Fruit(100, 2)]
    tax_calc = TaxCalculatorVisitor()

    for item in items:
        item.accept(tax_calc)
```

**Output:**
```text
@@OUT@@
```

**Analysis.** This uses a technique called **Double Dispatch**. The client calls `item.accept(visitor)`. The item (e.g., `Book`) then calls `visitor.visit(this)`. Because Java and Python resolve the `this` (or `self`) reference at runtime, the visitor knows exactly which concrete `visit(Book)` or `visit_book` method to execute.

**Intuition.**
- **Mechanism.** Implement an `accept(Visitor)` method on elements. Implement overloaded `visit(Element)` methods on the Visitor.
- **Concrete bite.** An insurance agent (Visitor) visiting different types of buildings (Elements). The agent evaluates a house differently than a factory. The buildings just open the door (`accept`), and the agent executes the correct evaluation logic based on the building type.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Visitor to perform operations on a stable hierarchy of classes without polluting their code. The cost is that adding a new *Element* to the hierarchy forces you to update every existing Visitor.

</div>

## 4. Memento Pattern

The Memento Pattern captures and externalizes an object's internal state so it can be restored later, all without violating encapsulation.

```java run
import java.util.*;

// Memento: stores the snapshot. Immutable.
class Memento {
    private final String state;
    public Memento(String state) { this.state = state; }
    public String getState() { return state; }
}

// Originator: creates and restores mementos.
class Editor {
    private String content = "";
    
    public void type(String words) { content += words; }
    public String getContent() { return content; }
    
    public Memento save() { return new Memento(content); }
    public void restore(Memento memento) { this.content = memento.getState(); }
}

// Caretaker: manages the mementos (history)
class History {
    private Stack<Memento> mementos = new Stack<>();
    
    public void push(Memento m) { mementos.push(m); }
    public Memento pop() { return mementos.pop(); }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Editor editor = new Editor();
        History history = new History();

        editor.type("This is the first sentence. ");
        history.push(editor.save());

        editor.type("This is the second. ");
        System.out.println("Current: " + editor.getContent());

        editor.restore(history.pop());
        System.out.println("Restored: " + editor.getContent());
    }
}
```
```python run
from typing import List


class Memento:
    def __init__(self, state: str) -> None:
        self._state = state

    @property
    def state(self) -> str:
        return self._state


class Editor:
    def __init__(self) -> None:
        self._content = ""

    def type(self, words: str) -> None:
        self._content += words

    @property
    def content(self) -> str:
        return self._content

    def save(self) -> Memento:
        return Memento(self._content)

    def restore(self, memento: Memento) -> None:
        self._content = memento.state


class History:
    def __init__(self) -> None:
        self._mementos: List[Memento] = []

    def push(self, m: Memento) -> None:
        self._mementos.append(m)

    def pop(self) -> Memento:
        return self._mementos.pop()


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    editor = Editor()
    history = History()

    editor.type("This is the first sentence. ")
    history.push(editor.save())

    editor.type("This is the second. ")
    print(f"Current: {editor.content}")

    editor.restore(history.pop())
    print(f"Restored: {editor.content}")
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `History` (Caretaker) holds the `Memento` objects but never inspects or modifies their contents. The `Editor` (Originator) is the only class that extracts state from the Memento. This protects the Editor's encapsulation.

**Intuition.**
- **Mechanism.** The Originator creates an immutable Memento containing its state. A Caretaker stores the Memento and can pass it back to the Originator later to restore the state.
- **Concrete bite.** Video game save files. You (the Caretaker) tell the game (the Originator) to save. It hands you a file (the Memento). You can't edit the file, but you can pass it back to the game later to resume playing.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Memento when you need to produce snapshots of an object's state to be able to restore a previous state. The cost is high RAM usage if the state is massive and snapshots are frequent.

</div>

## Summary

| Pattern | Purpose |
|---|---|
| **Chain of Responsibility** | Passes a request along a chain of potential handlers. |
| **Mediator** | Centralizes communication between objects to prevent a tangled web of dependencies. |
| **Visitor** | Adds operations to a stable hierarchy of objects without modifying their classes. |
| **Memento** | Captures and restores an object's state without violating encapsulation. |

## 🚨 Gotcha Checklist
| Symptom | Likely cause | Fix |
|---|---|---|
| You try to add a new `Video` class to an element hierarchy, and suddenly you have to edit 14 different `Visitor` classes. | **Unstable hierarchy.** Visitor is only meant for object hierarchies that rarely change. | If the hierarchy changes often, don't use Visitor. Put the operations directly inside the classes instead. |
| Two objects communicate with each other, then one triggers the Mediator, which triggers the other, creating an infinite loop. | **Mediator circular dependency.** Complex event handling in a Mediator can easily loop back on itself. | Use flags or careful event tracing to ensure events only propagate one way. |

## ✅ Check yourself

```quiz
{
  "prompt": "Which pattern relies on 'Double Dispatch' (calling `accept(visitor)` on an element, which in turn calls `visit(element)` on the visitor)?",
  "options": [
    "Visitor",
    "Mediator",
    "Command",
    "Chain of Responsibility"
  ],
  "answer": "Visitor"
}
```

```quiz
{
  "prompt": "If you have an application with dozens of UI components that all trigger complex interactions with each other, which pattern helps decouple them by moving the interaction logic to a central hub?",
  "options": [
    "Mediator",
    "Observer",
    "Chain of Responsibility",
    "Strategy"
  ],
  "answer": "Mediator"
}
```

<details>
<summary>Why shouldn't the Caretaker just read the fields directly from the Editor and store them?</summary>

Because that breaks encapsulation. The `Editor` would have to make its internal fields `public`, allowing *any* class to modify them. By using a Memento, the `Editor` packages its state securely, and the Caretaker holds it blindly.
</details>

## 📚 Sources
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

<div style="border-left:4px solid #8e155c;background:rgba(142,21,92,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** 
In the Chain of Responsibility, does the invoker know which handler will eventually process the request?

No. The invoker simply hands the request to the *first* handler in the chain. It is up to the handlers to decide who processes it, which decouples the sender from the receiver.

</div>

## Your Turn

Think of an Express.js or Spring Boot application. The request passes through authentication, rate limiting, and body parsing before reaching your controller. This is the **Chain of Responsibility**. Write a dummy chain of three handlers that checks if a user is logged in, then checks if they have admin rights, then prints "Success".
