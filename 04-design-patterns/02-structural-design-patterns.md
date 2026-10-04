---
title: "Structural Design Patterns"
summary: "Adapter, Decorator, Facade, Composite, Proxy, Bridge, and Flyweight — how objects and classes compose into larger, flexible structures."
essential: true
---

# Structural Design Patterns

Structural design patterns are concerned with the composition of classes and objects. They focus on how to assemble classes and objects into larger structures while keeping these structures flexible and efficient. 

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.** While creational patterns help you create objects, structural patterns help you plug those objects together to form larger, more complex structures without coupling them so tightly that they break when changed.

</div>

**You'll be able to:**
- Make incompatible interfaces work together (Adapter).
- Attach new behaviors to objects dynamically (Decorator).
- Provide a simplified interface to a complex subsystem (Facade).
- Treat individual objects and compositions of objects uniformly (Composite).
- Provide a surrogate to control access to an object (Proxy).
- Decouple an abstraction from its implementation (Bridge).
- Share memory efficiently across a huge number of fine-grained objects (Flyweight).

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** As you read, look for the *Mechanism* and *Concrete bite* under each code block. They map the code you just saw to the mental model you need to build.

</div>

1. [Adapter Pattern](#1-adapter-pattern)
2. [Decorator Pattern](#2-decorator-pattern)
3. [Facade Pattern](#3-facade-pattern)
4. [Composite Pattern](#4-composite-pattern)
5. [Proxy Pattern](#5-proxy-pattern)
6. [Bridge Pattern](#6-bridge-pattern)
7. [Flyweight Pattern](#7-flyweight-pattern)

## 1. Adapter Pattern

The Adapter Pattern allows incompatible interfaces to work together. It acts as a bridge between a Target interface (expected by the client) and an Adaptee (an existing class with a different interface).

Imagine you are implementing a payment system and want to integrate both PayU and Razorpay. PayU might already conform to your `PaymentGateway` interface, but Razorpay has its own distinct API.

```java run
// Target Interface expected by the client
interface PaymentGateway {
    void pay(String orderId, double amount);
}

// Adaptee: An existing class with an incompatible interface
class RazorpayAPI {
    public void makePayment(String invoiceId, double amountInRupees) {
        System.out.println("Paid Rs. " + amountInRupees + " using Razorpay for invoice: " + invoiceId);
    }
}

// Adapter: Translates the expected interface to the Adaptee
class RazorpayAdapter implements PaymentGateway {
    private RazorpayAPI razorpayAPI;

    public RazorpayAdapter(RazorpayAPI razorpayAPI) {
        this.razorpayAPI = razorpayAPI;
    }

    @Override
    public void pay(String orderId, double amount) {
        razorpayAPI.makePayment(orderId, amount);
    }
}

// Client
class CheckoutService {
    private PaymentGateway paymentGateway;

    public CheckoutService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }

    public void checkout(String orderId, double amount) {
        paymentGateway.pay(orderId, amount);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        RazorpayAPI api = new RazorpayAPI();
        CheckoutService checkout = new CheckoutService(new RazorpayAdapter(api));
        checkout.checkout("123", 1500.0);
    }
}
```
```python run
from abc import ABC, abstractmethod


class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, order_id: str, amount: float) -> None:
        ...


class RazorpayAPI:
    def make_payment(self, invoice_id: str, amount_in_rupees: float) -> None:
        print(f"Paid Rs. {amount_in_rupees} using Razorpay for invoice: {invoice_id}")


class RazorpayAdapter(PaymentGateway):
    def __init__(self, razorpay_api: RazorpayAPI) -> None:
        self._razorpay_api = razorpay_api

    def pay(self, order_id: str, amount: float) -> None:
        self._razorpay_api.make_payment(order_id, amount)


class CheckoutService:
    def __init__(self, payment_gateway: PaymentGateway) -> None:
        self._payment_gateway = payment_gateway

    def checkout(self, order_id: str, amount: float) -> None:
        self._payment_gateway.pay(order_id, amount)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    api = RazorpayAPI()
    checkout = CheckoutService(RazorpayAdapter(api))
    checkout.checkout("123", 1500.0)
```

**Output:**
```
Paid Rs. 1500.0 using Razorpay for invoice: 123
```

**Analysis.** The `CheckoutService` expects a `pay()` method. The `RazorpayAPI` only has `makePayment()`. The `RazorpayAdapter` bridges this gap by implementing `PaymentGateway` and translating `pay()` calls into `makePayment()` calls on the wrapped `RazorpayAPI`.

**Intuition.**
- **Mechanism.** Create a wrapper class that implements the expected interface and translates calls to the wrapped object.
- **Concrete bite.** When traveling from India to Europe, your mobile charger's pins don't fit the wall socket. You use a plug adapter that accepts Indian pins and has European pins on the other side.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use an Adapter when you want to use an existing class, but its interface doesn't match the one you need. The cost is the addition of a new class, slightly increasing the overall complexity.

</div>

## 2. Decorator Pattern

The Decorator Pattern allows behavior to be added to individual objects, dynamically at runtime, without affecting the behavior of other objects from the same class.

Instead of relying on a rigid class hierarchy where you subclass every possible combination of features (e.g. `CheesePizza`, `OlivePizza`, `CheeseOlivePizza`), you wrap objects in decorators.

```java run
interface Pizza {
    String getDescription();
    double getCost();
}

class MargheritaPizza implements Pizza {
    public String getDescription() { return "Margherita Pizza"; }
    public double getCost() { return 200.00; }
}

abstract class PizzaDecorator implements Pizza {
    protected Pizza pizza;
    public PizzaDecorator(Pizza pizza) { this.pizza = pizza; }
}

class ExtraCheese extends PizzaDecorator {
    public ExtraCheese(Pizza pizza) { super(pizza); }
    public String getDescription() { return pizza.getDescription() + ", Extra Cheese"; }
    public double getCost() { return pizza.getCost() + 40.0; }
}

class Olives extends PizzaDecorator {
    public Olives(Pizza pizza) { super(pizza); }
    public String getDescription() { return pizza.getDescription() + ", Olives"; }
    public double getCost() { return pizza.getCost() + 30.0; }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Pizza myPizza = new MargheritaPizza();
        myPizza = new ExtraCheese(myPizza);
        myPizza = new Olives(myPizza);

        System.out.println(myPizza.getDescription() + " = ₹" + myPizza.getCost());
    }
}
```
```python run
from abc import ABC, abstractmethod


class Pizza(ABC):
    @abstractmethod
    def get_description(self) -> str: ...
    @abstractmethod
    def get_cost(self) -> float: ...


class MargheritaPizza(Pizza):
    def get_description(self) -> str: return "Margherita Pizza"
    def get_cost(self) -> float: return 200.00


class PizzaDecorator(Pizza, ABC):
    def __init__(self, pizza: Pizza) -> None:
        self._pizza = pizza


class ExtraCheese(PizzaDecorator):
    def get_description(self) -> str: return self._pizza.get_description() + ", Extra Cheese"
    def get_cost(self) -> float: return self._pizza.get_cost() + 40.0


class Olives(PizzaDecorator):
    def get_description(self) -> str: return self._pizza.get_description() + ", Olives"
    def get_cost(self) -> float: return self._pizza.get_cost() + 30.0


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    my_pizza: Pizza = MargheritaPizza()
    my_pizza = ExtraCheese(my_pizza)
    my_pizza = Olives(my_pizza)

    print(f"{my_pizza.get_description()} = ₹{my_pizza.get_cost()}")
```

**Output:**
```
Margherita Pizza, Extra Cheese, Olives = ₹270.0
```

**Analysis.** Each decorator implements the `Pizza` interface and holds a reference to a wrapped `Pizza`. When `getCost()` is called, the decorator delegates the call to the wrapped object and adds its own cost. This allows infinite stacking of toppings without creating new base classes. Note that Python's function decorators (`@decorator`) wrap functions or methods, whereas the Gang of Four Decorator Pattern wraps objects.

**Intuition.**
- **Mechanism.** Implement the component interface and wrap an instance of it, delegating calls and modifying results.
- **Concrete bite.** When buying coffee, you don't buy an entirely new drink for every addition. You order a base coffee, then "decorate" it with milk, then sugar.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Decorator when you need to assign extra behaviors to objects at runtime without breaking the code that uses these objects. The cost is a proliferation of small wrapper classes and a deeper call stack.

</div>

## 3. Facade Pattern

The Facade Pattern provides a simplified, unified interface to a complex subsystem or group of classes.

Instead of making the client interact directly with multiple components (like `PaymentService`, `SeatReservationService`, `TicketService`), you provide a single Facade class that orchestrates these interactions.

```java run
class PaymentService {
    public void pay(double amount) { System.out.println("Payment of ₹" + amount + " successful"); }
}
class SeatReservationService {
    public void reserve(String seat) { System.out.println("Seat " + seat + " reserved"); }
}
class TicketService {
    public void generate() { System.out.println("Ticket generated"); }
}

class MovieBookingFacade {
    private PaymentService payment = new PaymentService();
    private SeatReservationService seatRes = new SeatReservationService();
    private TicketService ticket = new TicketService();

    public void bookTicket(String seat, double amount) {
        payment.pay(amount);
        seatRes.reserve(seat);
        ticket.generate();
        System.out.println("Booking complete!");
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        MovieBookingFacade facade = new MovieBookingFacade();
        facade.bookTicket("A10", 500);
    }
}
```
```python run
class PaymentService:
    def pay(self, amount: float) -> None:
        print(f"Payment of ₹{amount} successful")

class SeatReservationService:
    def reserve(self, seat: str) -> None:
        print(f"Seat {seat} reserved")

class TicketService:
    def generate(self) -> None:
        print("Ticket generated")

class MovieBookingFacade:
    def __init__(self) -> None:
        self._payment = PaymentService()
        self._seat_res = SeatReservationService()
        self._ticket = TicketService()

    def book_ticket(self, seat: str, amount: float) -> None:
        self._payment.pay(amount)
        self._seat_res.reserve(seat)
        self._ticket.generate()
        print("Booking complete!")

# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    facade = MovieBookingFacade()
    facade.book_ticket("A10", 500)
```

**Output (Java):**
```
Payment of ₹500.0 successful
Seat A10 reserved
Ticket generated
Booking complete!
```

**Output (Python):**
```
Payment of ₹500 successful
Seat A10 reserved
Ticket generated
Booking complete!
```

**Analysis.** The client only calls `bookTicket()` on the `MovieBookingFacade`. The underlying complexity of paying, reserving a seat, and generating a ticket is completely hidden. If the booking workflow changes, only the Facade needs updating, protecting the client from ripple effects.

**Intuition.**
- **Mechanism.** Create a single class that encapsulates the interaction with multiple classes in a subsystem.
- **Concrete bite.** When you drive an automatic car, you interact with a simplified interface ("Drive", "Reverse", "Park"). The car's internal facade handles the complex orchestration of the clutch, gears, and engine RPM.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a Facade when you need to provide a simple or unified interface to a complex subsystem. The cost is that the Facade can become a "god object" tied to all classes of an app if it orchestrates too much.

</div>

## 4. Composite Pattern

The Composite Pattern allows you to compose objects into tree structures to represent part-whole hierarchies. It lets clients treat individual objects (leaves) and compositions of objects (composites) uniformly.

```java run
import java.util.*;

interface CartItem {
    double getPrice();
    void display(String indent);
}

class Product implements CartItem {
    private String name;
    private double price;

    public Product(String name, double price) {
        this.name = name;
        this.price = price;
    }

    public double getPrice() { return price; }
    public void display(String indent) { System.out.println(indent + name + " - ₹" + price); }
}

class ProductBundle implements CartItem {
    private String name;
    private List<CartItem> items = new ArrayList<>();

    public ProductBundle(String name) { this.name = name; }
    public void addItem(CartItem item) { items.add(item); }

    public double getPrice() {
        double total = 0;
        for (CartItem item : items) total += item.getPrice();
        return total;
    }

    public void display(String indent) {
        System.out.println(indent + "Bundle: " + name);
        for (CartItem item : items) item.display(indent + "  ");
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        CartItem phone = new Product("iPhone", 70000);
        CartItem charger = new Product("Charger", 2000);
        
        ProductBundle techCombo = new ProductBundle("Tech Combo");
        techCombo.addItem(phone);
        techCombo.addItem(charger);
        
        ProductBundle megaCart = new ProductBundle("Mega Cart");
        megaCart.addItem(techCombo);
        megaCart.addItem(new Product("Book", 500));
        
        megaCart.display("");
        System.out.println("Total: ₹" + megaCart.getPrice());
    }
}
```
```python run
from abc import ABC, abstractmethod
from typing import List


class CartItem(ABC):
    @abstractmethod
    def get_price(self) -> float: ...
    @abstractmethod
    def display(self, indent: str) -> None: ...


class Product(CartItem):
    def __init__(self, name: str, price: float) -> None:
        self._name = name
        self._price = price

    def get_price(self) -> float: return self._price
    def display(self, indent: str) -> None: print(f"{indent}{self._name} - ₹{self._price}")


class ProductBundle(CartItem):
    def __init__(self, name: str) -> None:
        self._name = name
        self._items: List[CartItem] = []

    def add_item(self, item: CartItem) -> None:
        self._items.append(item)

    def get_price(self) -> float:
        return sum(item.get_price() for item in self._items)

    def display(self, indent: str) -> None:
        print(f"{indent}Bundle: {self._name}")
        for item in self._items:
            item.display(indent + "  ")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    phone = Product("iPhone", 70000)
    charger = Product("Charger", 2000)

    tech_combo = ProductBundle("Tech Combo")
    tech_combo.add_item(phone)
    tech_combo.add_item(charger)

    mega_cart = ProductBundle("Mega Cart")
    mega_cart.add_item(tech_combo)
    mega_cart.add_item(Product("Book", 500))

    mega_cart.display("")
    print(f"Total: ₹{mega_cart.get_price()}")
```

**Output (Java):**
```
Bundle: Mega Cart
  Bundle: Tech Combo
    iPhone - ₹70000.0
    Charger - ₹2000.0
  Book - ₹500.0
Total: ₹72500.0
```

**Output (Python):**
```
Bundle: Mega Cart
  Bundle: Tech Combo
    iPhone - ₹70000
    Charger - ₹2000
  Book - ₹500
Total: ₹72500
```

**Analysis.** Because both `Product` and `ProductBundle` implement `CartItem`, the client can iterate over a list of `CartItem`s without using `instanceof` to check whether an item is a single product or a nested bundle. Calling `getPrice()` recursively computes the sum.

**Intuition.**
- **Mechanism.** Implement a common interface for both leaf nodes and composite nodes, where composite nodes iterate over their children and delegate the work.
- **Concrete bite.** A folder on your computer can contain files (leaves) and other folders (composites). When you ask the OS for the size of a folder, it asks for the size of everything inside, treating files and nested folders identically.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use the Composite pattern when you have to implement a tree-like object structure and want clients to treat individual objects and compositions uniformly. The cost is that the unified interface may include operations that don't make sense for leaf nodes.

</div>

## 5. Proxy Pattern

The Proxy Pattern provides a surrogate or placeholder for another object to control access to it. It intercepts requests to the real object.

```java run
import java.util.*;

interface VideoDownloader {
    String downloadVideo(String videoUrl);
}

class RealVideoDownloader implements VideoDownloader {
    public String downloadVideo(String videoUrl) {
        System.out.println("Downloading from network: " + videoUrl);
        return "Video content";
    }
}

class CachedVideoDownloader implements VideoDownloader {
    private RealVideoDownloader realDownloader = new RealVideoDownloader();
    private Map<String, String> cache = new HashMap<>();

    public String downloadVideo(String videoUrl) {
        if (cache.containsKey(videoUrl)) {
            System.out.println("Returning cached video for: " + videoUrl);
            return cache.get(videoUrl);
        }
        String video = realDownloader.downloadVideo(videoUrl);
        cache.put(videoUrl, video);
        return video;
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        VideoDownloader proxy = new CachedVideoDownloader();
        proxy.downloadVideo("https://example.com/video1");
        proxy.downloadVideo("https://example.com/video1");
    }
}
```
```python run
from abc import ABC, abstractmethod
from typing import Dict


class VideoDownloader(ABC):
    @abstractmethod
    def download_video(self, video_url: str) -> str: ...


class RealVideoDownloader(VideoDownloader):
    def download_video(self, video_url: str) -> str:
        print(f"Downloading from network: {video_url}")
        return "Video content"


class CachedVideoDownloader(VideoDownloader):
    def __init__(self) -> None:
        self._real_downloader = RealVideoDownloader()
        self._cache: Dict[str, str] = {}

    def download_video(self, video_url: str) -> str:
        if video_url in self._cache:
            print(f"Returning cached video for: {video_url}")
            return self._cache[video_url]
        
        video = self._real_downloader.download_video(video_url)
        self._cache[video_url] = video
        return video


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    proxy = CachedVideoDownloader()
    proxy.download_video("https://example.com/video1")
    proxy.download_video("https://example.com/video1")
```

**Output:**
```
Downloading from network: https://example.com/video1
Returning cached video for: https://example.com/video1
```

**Analysis.** The `CachedVideoDownloader` intercepts the `downloadVideo` call. If the result is already in the cache, it returns it directly, avoiding an expensive call to `RealVideoDownloader`. This is the core of lazy initialization and caching. 

**Intuition.**
- **Mechanism.** Implement the same interface as the real object, intercept calls, apply logic (like caching or access control), and pass the call to the real object if necessary.
- **Concrete bite.** A corporate firewall acts as a proxy. You ask it for a webpage; if it's allowed and cached, it hands it back instantly. If it's malicious, it denies access before your browser ever connects to the remote server.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a Proxy when you need lazy initialization, access control, logging, or caching for a resource-heavy object. The cost is a delayed response and a new layer of abstraction.

</div>

## 6. Bridge Pattern

The Bridge Pattern is a structural design pattern that is used to decouple an abstraction from its implementation so that the two can vary independently.

When you have multiple dimensions of variability, such as different types of platforms (Web, Mobile) and multiple features (SD, HD, 4K video quality), you end up with a combinatorial explosion of subclasses (`WebHDPlayer`, `MobileHDPlayer`, `Web4KPlayer`) if you try to use inheritance to handle all combinations.

```java run
interface VideoQuality {
    void load(String title);
}

class HDQuality implements VideoQuality {
    public void load(String title) { System.out.println("Streaming " + title + " in HD Quality"); }
}
class UltraHDQuality implements VideoQuality {
    public void load(String title) { System.out.println("Streaming " + title + " in 4K Ultra HD Quality"); }
}

abstract class VideoPlayer {
    protected VideoQuality quality;
    public VideoPlayer(VideoQuality quality) { this.quality = quality; }
    public abstract void play(String title);
}

class WebPlayer extends VideoPlayer {
    public WebPlayer(VideoQuality quality) { super(quality); }
    public void play(String title) {
        System.out.println("Web Platform:");
        quality.load(title);
    }
}

class MobilePlayer extends VideoPlayer {
    public MobilePlayer(VideoQuality quality) { super(quality); }
    public void play(String title) {
        System.out.println("Mobile Platform:");
        quality.load(title);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        VideoPlayer player1 = new WebPlayer(new HDQuality());
        player1.play("Interstellar");

        VideoPlayer player2 = new MobilePlayer(new UltraHDQuality());
        player2.play("Inception");
    }
}
```
```python run
from abc import ABC, abstractmethod


class VideoQuality(ABC):
    @abstractmethod
    def load(self, title: str) -> None: ...


class HDQuality(VideoQuality):
    def load(self, title: str) -> None: print(f"Streaming {title} in HD Quality")


class UltraHDQuality(VideoQuality):
    def load(self, title: str) -> None: print(f"Streaming {title} in 4K Ultra HD Quality")


class VideoPlayer(ABC):
    def __init__(self, quality: VideoQuality) -> None:
        self._quality = quality
    @abstractmethod
    def play(self, title: str) -> None: ...


class WebPlayer(VideoPlayer):
    def play(self, title: str) -> None:
        print("Web Platform:")
        self._quality.load(title)


class MobilePlayer(VideoPlayer):
    def play(self, title: str) -> None:
        print("Mobile Platform:")
        self._quality.load(title)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    player1 = WebPlayer(HDQuality())
    player1.play("Interstellar")

    player2 = MobilePlayer(UltraHDQuality())
    player2.play("Inception")
```

**Output:**
```
Web Platform:
Streaming Interstellar in HD Quality
Mobile Platform:
Streaming Inception in 4K Ultra HD Quality
```

**Analysis.** The abstraction (`VideoPlayer`) does not implement video streaming itself; it delegates it to the implementor (`VideoQuality`). Adding a new platform like `SmartTV` just adds one class extending `VideoPlayer`, and it automatically supports all existing video qualities.

**Intuition.**
- **Mechanism.** Use composition instead of inheritance. Make one of the dimensions (quality) a separate class hierarchy, and pass an instance of it to the other hierarchy (player).
- **Concrete bite.** A TV remote (abstraction) and a TV (implementation). You can buy a more advanced remote, or you can buy a newer TV. Because the communication protocol between them is standardized, any remote can talk to any TV.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Bridge when you want to divide and organize a monolithic class that has multiple variants of some functionality (e.g., cross-platform apps or multiple hardware integrations). The cost is added indirection.

</div>

## 7. Flyweight Pattern

The Flyweight Pattern is used to minimize memory usage by sharing as much data as possible with similar objects.

It separates the intrinsic (shared) state from the extrinsic (unique) state, so that shared parts of objects are stored only once and reused wherever needed.

```java run
import java.util.*;

// Intrinsic state: shared across all trees of the same type
class TreeType {
    private String name, color, texture;
    public TreeType(String name, String color, String texture) {
        this.name = name; this.color = color; this.texture = texture;
    }
    public void draw(int x, int y) {
        System.out.println("Drawing " + name + " tree at (" + x + ", " + y + ")");
    }
}

// Extrinsic state: unique coordinates + reference to shared intrinsic state
class Tree {
    private int x, y;
    private TreeType treeType;
    public Tree(int x, int y, TreeType treeType) {
        this.x = x; this.y = y; this.treeType = treeType;
    }
    public void draw() { treeType.draw(x, y); }
}

// Factory caches and reuses the intrinsic state
class TreeFactory {
    static Map<String, TreeType> treeTypeMap = new HashMap<>();
    public static TreeType getTreeType(String name, String color, String texture) {
        String key = name + "-" + color + "-" + texture;
        if (!treeTypeMap.containsKey(key)) {
            treeTypeMap.put(key, new TreeType(name, color, texture));
        }
        return treeTypeMap.get(key);
    }
}

class Forest {
    private List<Tree> trees = new ArrayList<>();
    public void plantTree(int x, int y, String name, String color, String texture) {
        Tree tree = new Tree(x, y, TreeFactory.getTreeType(name, color, texture));
        trees.add(tree);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Forest forest = new Forest();
        for (int i = 0; i < 10000; i++) {
            forest.plantTree(i, i, "Oak", "Green", "Rough");
        }
        System.out.println("Planted 10000 trees.");
        System.out.println("Distinct TreeType objects: " + TreeFactory.treeTypeMap.size());
    }
}
```
```python run
from typing import Dict, List


class TreeType:
    def __init__(self, name: str, color: str, texture: str) -> None:
        self._name = name
        self._color = color
        self._texture = texture

    def draw(self, x: int, y: int) -> None:
        print(f"Drawing {self._name} tree at ({x}, {y})")


class Tree:
    def __init__(self, x: int, y: int, tree_type: TreeType) -> None:
        self._x = x
        self._y = y
        self._tree_type = tree_type

    def draw(self) -> None:
        self._tree_type.draw(self._x, self._y)


class TreeFactory:
    _tree_types: Dict[str, TreeType] = {}

    @classmethod
    def get_tree_type(cls, name: str, color: str, texture: str) -> TreeType:
        key = f"{name}-{color}-{texture}"
        if key not in cls._tree_types:
            cls._tree_types[key] = TreeType(name, color, texture)
        return cls._tree_types[key]


class Forest:
    def __init__(self) -> None:
        self._trees: List[Tree] = []

    def plant_tree(self, x: int, y: int, name: str, color: str, texture: str) -> None:
        tree = Tree(x, y, TreeFactory.get_tree_type(name, color, texture))
        self._trees.append(tree)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    forest = Forest()
    for i in range(10000):
        forest.plant_tree(i, i, "Oak", "Green", "Rough")

    print("Planted 10000 trees.")
    print(f"Distinct TreeType objects: {len(TreeFactory._tree_types)}")
```

**Output:**
```
Planted 10000 trees.
Distinct TreeType objects: 1
```

**Analysis.** Even though we created 10,000 `Tree` objects, we only instantiated 1 `TreeType` object. The memory overhead for storing the string `"Oak"`, `"Green"`, and `"Rough"` occurs exactly once. This is the same principle Python uses internally to cache small integers (like `256`) and short strings, avoiding duplicate memory allocation for identical constants.

**Intuition.**
- **Mechanism.** Divide an object's state into intrinsic (immutable, shareable) and extrinsic (mutable, unique per instance). Move intrinsic state to a shared "flyweight" object returned by a factory.
- **Concrete bite.** When rendering this webpage, the browser doesn't load a separate image into RAM for every single letter 'e' on the screen. It loads the shape of 'e' once (intrinsic), and draws it at different coordinates (extrinsic).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use the Flyweight pattern when a huge number of identical objects consumes too much RAM. The cost is slightly higher CPU overhead to compute or pass the extrinsic state on every method call.

</div>

## Summary

| Pattern | Purpose |
|---|---|
| **Adapter** | Wraps an incompatible object to make it conform to a target interface. |
| **Decorator** | Wraps an object to dynamically add or alter behavior without modifying the base class. |
| **Facade** | Wraps a complex subsystem and provides a simple, single point of entry. |
| **Composite** | Wraps objects into tree structures, allowing uniform treatment of leaves and branches. |
| **Proxy** | Wraps an object to control or defer access to it (e.g. lazy loading, caching). |
| **Bridge** | Separates an abstraction from its implementation so they can vary independently. |
| **Flyweight** | Extracts shared state from millions of objects into a single shared object to save memory. |

## 🚨 Gotcha Checklist
| Symptom | Likely cause | Fix |
|---|---|---|
| You find yourself writing `instanceof` checks when looping over a mix of simple objects and collections of those objects. | **Missing Composite.** The client has to distinguish between leaves and branches manually. | Make both the leaf and branch implement the same component interface. |
| Your inheritance tree is exploding because you have `Shape`, `RedShape`, `BlueShape`, `Circle`, `RedCircle`, etc. | **Combinatorial explosion.** You are using inheritance to mix two independent dimensions (shape and color). | Use the Bridge pattern to separate `Shape` and `Color`. |
| Wrapping an object in a Decorator breaks existing code that uses `instanceof` checks on that object. | **Decorator changes identity.** A decorated object is a wrapper, not the original object. | Don't use decorators if your client code relies on strict object identity or concrete class checking. Depend on interfaces instead. |

## ✅ Check yourself

```quiz
{
  "prompt": "Which pattern is the best fit when you want to delay loading a heavy image from disk until it actually needs to be rendered on the screen?",
  "options": [
    "Adapter",
    "Proxy",
    "Facade",
    "Composite"
  ],
  "answer": "Proxy"
}
```

```quiz
{
  "prompt": "If you are integrating a third-party analytics library whose method signatures do not match what your application expects, which pattern should you use?",
  "options": [
    "Bridge",
    "Decorator",
    "Adapter",
    "Flyweight"
  ],
  "answer": "Adapter"
}
```

<details>
<summary>What is the difference between Adapter, Decorator, and Proxy? They all wrap an object.</summary>

While their structure is similar (all wrap an object), their intent is different:
- **Adapter:** Changes the interface of the wrapped object so it becomes compatible with a client.
- **Decorator:** Keeps the same interface, but adds new behaviors or responsibilities to the wrapped object.
- **Proxy:** Keeps the same interface, but controls access to the wrapped object (e.g. caching, lazy loading, security).
</details>

## 📚 Sources
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

<div style="border-left:4px solid #8e155c;background:rgba(142,21,92,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** 
If a `CachedVideoDownloader` (Proxy) is instantiated, does the `RealVideoDownloader` get instantiated immediately?

Yes, in the example above, the constructor instantiates `RealVideoDownloader`. If `RealVideoDownloader` takes a long time to create, the Proxy should use **lazy initialization**, creating `RealVideoDownloader` only when `downloadVideo()` is called for the first time.

</div>

## Your Turn

Look at how your favorite framework handles HTTP requests or database calls. Do they expose every single internal component, or do they offer a unified `Client` or `Context` object? That's a Facade! Think of a subsystem in your own codebase that requires calling 3 or 4 different classes in a specific order. Wrap it in a Facade.
