---
title: "API & Database Design"
summary: "API design, versioning, lifecycle, and security patterns, plus database design and integration practices for LLD, using a payment-system case study."
essential: true
---

# API Design, Versioning, and Security

APIs (Application Programming Interfaces) are the backbone of modern software architecture, enabling seamless communication between services, platforms, and systems. As businesses grow and systems scale, careful attention to API design, versioning, and security becomes essential. This guide dives deep into best practices, patterns, and principles required to build enterprise-grade APIs that are robust, scalable, secure, and maintainable.

## 1. What Are APIs? Things to Keep in Mind While Designing Them

An API is a contract that allows two software components to interact. It defines what data can be exchanged, how it can be accessed, and under what constraints. API design influences developer experience, system flexibility, and security posture.

### Key Design Considerations:

- **Clarity:** Use intuitive and descriptive resource names (e.g., /users, /payments).
- **Consistency:** Follow a uniform naming convention, error format, and HTTP verbs (GET, POST, PUT, DELETE).
- **Predictability:** Avoid surprises. Ensure the same input always results in predictable output.
- **Minimalism:** Expose only necessary data, and avoid overloading clients with too many options.
- **Statelessness:** APIs should not rely on server-side sessions; each call should be independent.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Designing APIs is not just about endpoints — it’s about creating a consistent and reliable developer experience.

</div>

## 2. API Lifecycle Across Teams

APIs often span multiple teams — from backend developers and frontend consumers to DevOps, QA, and product managers. A well-defined API lifecycle ensures consistency, quality, and traceability throughout its evolution.

### Stages of API Lifecycle:

- **Design:** Define contracts using tools like OpenAPI (Swagger), including endpoints, methods, and response schemas.
- **Development:** Implement the API while adhering to the defined spec, following version control and code reviews.
- **Testing:** Perform integration and contract tests. Use mocks or stubs to decouple frontend/backend development.
- **Deployment:** Deploy APIs in CI/CD pipelines with canary releases, blue-green deployments, or feature toggles.
- **Monitoring:** Track metrics like latency, uptime, and error rate using tools like Prometheus, Grafana, or Postman Monitor.
- **Versioning/Maintenance:** Introduce changes carefully while maintaining backward compatibility.
- **Deprecation:** Gradually phase out old versions with client communication and support periods.

## 3. Advanced REST Principles & Sensitive Operations

REST (Representational State Transfer) APIs should follow principles that maximize scalability, flexibility, and security.

### Advanced REST Guidelines:

- **HATEOAS (Hypermedia as the Engine of Application State):** Include links within responses to guide client actions.
- **Idempotency:** Ensure methods like PUT and DELETE are idempotent — calling them multiple times has the same effect.
- **Partial Updates:** Use PATCH for modifying partial resources instead of overwriting full objects.
- **Validation:** Use schemas (like JSON Schema) to validate requests and responses.

### Handling Sensitive Operations:

- Use two-step confirmation or email verification for critical actions (e.g., password changes, fund transfers).
- Use HTTP 401/403 for unauthorized/forbidden access, not just 500 errors.

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** Encrypt sensitive query parameters and payloads — never expose secrets via URLs.

</div>

## 4. DTO Patterns – Designing Contracts

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** DTO (Data Transfer Object) patterns help define strict contracts between API consumers and producers.

</div>

DTOs are used to encapsulate data in both directions (requests and responses) and decouple internal models from external exposure.

### Best Practices for DTOs:

- **Validation:** Annotate DTOs with validation rules (e.g., required fields, formats).
- **Encapsulation:** Never expose internal entity structures or unnecessary metadata.
- **Separate Input and Output DTOs:** Avoid reusing the same object for requests and responses.
- **Immutable Contracts:** Treat DTOs as contracts. Changing them should be versioned and communicated.

## 5. Error Handling

Robust error handling ensures clients receive clear, actionable feedback. A consistent error structure helps in debugging and improves client integration.

### Recommended Error Response Structure:

```json
{
  "timestamp": "2025-07-29T10:23:00Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Missing required field: email",
  "path": "/api/users"
}
```

### HTTP Status Code Guidelines:

- 2xx – Success
- 4xx – Client errors (e.g., 400 Bad Request, 401 Unauthorized, 404 Not Found)
- 5xx – Server errors (e.g., 500 Internal Server Error, 503 Service Unavailable)

## 6. Versioning

API versioning is critical for evolving your product without breaking existing clients. It helps manage backward-incompatible changes.

### Common Versioning Strategies:

- **URI Versioning:** /api/v1/users (most explicit and commonly used)
- **Header Versioning:** Custom headers like X-API-Version: 1
- **Media Type Versioning:** Accept: application/vnd.company.v1+json

### Versioning Best Practices:

- Introduce breaking changes only in new versions.
- Deprecate but support old versions with clear timelines.
- Document changes and provide migration guides.

## 7. Filtering, Sorting, and Pagination

Large datasets should not be returned as single responses. Filtering, sorting, and pagination help control performance and usability.

### Example Query Parameters:

- ?page=2&limit=50 – Pagination
- ?sort=created_at&order=desc – Sorting
- ?status=active&type=premium – Filtering

### Paginated Response Format:

```json
{
  "data": [...],
  "page": 2,
  "limit": 50,
  "totalItems": 320,
  "totalPages": 7
}
```

## 8. API Security Considerations, Throttling, and Rate Limiting

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** APIs must be secure by default. A compromised API can lead to data leaks, financial losses, or service downtime.

</div>

### Security Best Practices:

- **Authentication:** Use OAuth2, API keys, or JWTs for authenticating clients.
- **Authorization:** Use role-based or permission-based access control.
- **Input Validation:** Sanitize all inputs to prevent SQL injection or XSS.
- **HTTPS Everywhere:** All traffic should be encrypted using TLS.

### Throttling & Rate Limiting:

- **Rate Limits:** Limit clients to a set number of requests per second/minute.
- **Throttling:** Temporarily slow down or block clients exceeding thresholds.
- **Quota Enforcement:** Monthly API usage caps for users, teams, or apps.

### Response Example for Rate Limiting:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
{
  "error": "Too many requests. Please retry after 60 seconds."
}
```

## Conclusion

Thoughtfully designed APIs act as stable foundations for digital products, enabling scalable innovation and collaboration. By focusing on consistent design, proper versioning, and strong security measures, organizations can provide developers with tools that are intuitive, safe, and future-proof.

As teams adopt these principles, they enhance not just the quality of their APIs — but also the trust and efficiency of their entire development lifecycle.

## Database Design and Integration in LLD

**Use-Case:** Razorpay Payment System

Designing robust, scalable, and maintainable systems requires a deep understanding of how to structure and integrate databases effectively. In Low-Level Design (LLD), this involves bridging the gap between abstract requirements and real-world implementation. This article covers the core topics you must know to implement sound database design and integration practices using Razorpay's payment system as a use case.

### 1. What is an ER Model?

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** The Entity-Relationship (ER) Model is a high-level conceptual data model used to define data elements and their relationships for a given system.

</div>

It provides a visual representation through ER diagrams that depict:

- **Entities:** Real-world objects or concepts (e.g., User, Transaction, Merchant).
- **Attributes:** Properties of entities (e.g., User may have user_id, email, KYC_status).
- **Relationships:** Connections between entities (e.g., User initiates a Transaction).

**Use-case Example – Razorpay:**

- **Entities:** User, Merchant, Payment, Invoice
- **Relationships:** User → makes → Payment, Merchant → receives → Payment

### 2. How to Design Tables from Requirements?

Once entities and relationships are identified, translate them into relational tables.

**Steps:**

- Extract entities from requirements
- Define attributes for each entity
- Determine primary and foreign keys
- Normalize the schema (1NF, 2NF, 3NF)
- Add constraints and indexes

**Example – Razorpay Payment Flow:**

**Requirement:** A user pays a merchant through a payment gateway using a payment method.

```text
users(user_id, name, email, phone)
merchants(merchant_id, name, business_type)
payments(payment_id, user_id, merchant_id, amount, method, timestamp)
payment_methods(method_id, type, provider)
```

### 3. Mapping ER → Class Model

To integrate database design into the application layer, ER diagrams are mapped to object-oriented class models.

**Mapping Principles:**

- Each entity → becomes a class
- Each attribute → becomes a field
- Relationships → become associations (one-to-one, one-to-many, many-to-many)

**Example – Razorpay Class Model (Java):**

```java
import java.util.*;

class User {
    Long id;
    String name;
    String email;
    List<Payment> payments;
}

class Payment {
    Long id;
    User user;
    Merchant merchant;
    Double amount;
    String method;
}

// Merchant is referenced by Payment but not shown above — minimal stub so the fence compiles.
class Merchant {
    Long id;
    String name;
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Merchant merchant = new Merchant();
        merchant.id = 1L;
        merchant.name = "Acme Store";

        User user = new User();
        user.id = 100L;
        user.name = "Alex";
        user.email = "alex@example.com";
        user.payments = new ArrayList<>();

        Payment payment = new Payment();
        payment.id = 5001L;
        payment.user = user;
        payment.merchant = merchant;
        payment.amount = 499.00;
        payment.method = "UPI";
        user.payments.add(payment);

        System.out.println(user.name + " paid " + payment.amount + " to " + merchant.name + " via " + payment.method);
    }
}
```

**The same idea in Python**

```python
from typing import List


class Merchant:
    def __init__(self, id_: int, name: str) -> None:
        self.id = id_
        self.name = name


class Payment:
    def __init__(self, id_: int, user: "User", merchant: Merchant, amount: float, method: str) -> None:
        self.id = id_
        self.user = user
        self.merchant = merchant
        self.amount = amount
        self.method = method


class User:
    def __init__(self, id_: int, name: str, email: str) -> None:
        self.id = id_
        self.name = name
        self.email = email
        self.payments: List[Payment] = []


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    merchant = Merchant(1, "Acme Store")

    user = User(100, "Alex", "alex@example.com")

    payment = Payment(5001, user, merchant, 499.00, "UPI")
    user.payments.append(payment)

    print(f"{user.name} paid {payment.amount} to {merchant.name} via {payment.method}")
```

### 4. What is DAO?

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** DAO (Data Access Object) is a design pattern that abstracts and encapsulates all access to the data source. It separates persistence logic from business logic.

</div>

**Benefits:**

- Loose coupling between database and code
- Easier to test and maintain
- Encourages separation of concerns

**Example – Java DAO Interface:**

```java
import java.util.*;

// Payment is referenced by the interface below but not defined in this fence — minimal stub.
class Payment {
    Long id;
}

interface PaymentDAO {
    Payment getPaymentById(Long id);
    List<Payment> getPaymentsByUser(Long userId);
    void save(Payment payment);
}

// DemoPaymentDAO exists only to demonstrate the contract — not the canonical implementation.
class DemoPaymentDAO implements PaymentDAO {
    private final Map<Long, Payment> store = new LinkedHashMap<>();

    @Override
    public Payment getPaymentById(Long id) {
        return store.get(id);
    }

    @Override
    public List<Payment> getPaymentsByUser(Long userId) {
        return new ArrayList<>(store.values());
    }

    @Override
    public void save(Payment payment) {
        store.put(payment.id, payment);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        PaymentDAO dao = new DemoPaymentDAO();
        Payment payment = new Payment();
        payment.id = 1L;
        dao.save(payment);
        System.out.println("Fetched payment id: " + dao.getPaymentById(1L).id);
    }
}
```

**The same idea in Python**

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


# Payment is referenced by the interface below but not defined in this fence — minimal stub.
class Payment:
    def __init__(self, id_: int) -> None:
        self.id = id_


# Java's `interface` has no direct Python analogue — abc.ABC + @abstractmethod
# makes the contract explicit: a subclass that forgets a method fails at
# instantiation (TypeError) instead of silently duck-typing past it.
class PaymentDAO(ABC):
    @abstractmethod
    def get_payment_by_id(self, id_: int) -> Optional[Payment]:
        ...

    @abstractmethod
    def get_payments_by_user(self, user_id: int) -> List[Payment]:
        ...

    @abstractmethod
    def save(self, payment: Payment) -> None:
        ...


# DemoPaymentDAO exists only to demonstrate the contract — not the canonical implementation.
class DemoPaymentDAO(PaymentDAO):
    def __init__(self) -> None:
        self._store: Dict[int, Payment] = {}

    def get_payment_by_id(self, id_: int) -> Optional[Payment]:
        return self._store.get(id_)

    def get_payments_by_user(self, user_id: int) -> List[Payment]:
        return list(self._store.values())

    def save(self, payment: Payment) -> None:
        self._store[payment.id] = payment


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    dao: PaymentDAO = DemoPaymentDAO()
    payment = Payment(1)
    dao.save(payment)
    fetched = dao.get_payment_by_id(1)
    assert fetched is not None
    print(f"Fetched payment id: {fetched.id}")
```

### 5. What is Repository?

The Repository pattern is an abstraction that provides a collection-like interface for accessing domain objects. It's often used with ORMs like Spring Data JPA.

**DAO vs Repository:**

| DAO | Repository |
| --- | --- |
| Focused on persistence | Focused on domain object collection |
| More database-centric | More business/domain-centric |
| May include SQL details | Often auto-implemented by frameworks |

**Example – Spring Repository:**

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** This snippet needs Spring Data JPA on the classpath — it won't compile standalone in the sandbox editor.

</div>

```java
// requires: spring-data-jpa — not runnable in the sandbox
public interface PaymentRepository extends JpaRepository<Payment, Long> {
    List<Payment> findByUserId(Long userId);
}
```

Spring Data JPA auto-implements a repository like this from the interface declaration alone — a
framework capability with no Python analogue, so no translation is given here. The DAO example
above (`PaymentDAO` as `abc.ABC`) is the idiomatic Python shape for the underlying pattern; you
would still write `DemoPaymentDAO`'s body by hand.

### 6. Real-World Enhancements and Practices

Building scalable systems involves more than just ER modeling. Here are industry practices for robust systems:

- **Read/Write Optimization:** Use replicas for reads, batch inserts for writes.
- **Caching Layer:** Use Redis or Memcached to store frequently accessed data.
- **Auditing and Logging:** Store transaction logs and enable change data capture (CDC).
- **Security Best Practices:** Encrypt sensitive fields and use role-based access control (RBAC).
- **Schema Versioning:** Use Flyway or Liquibase for migrations.
- **Testing and Monitoring:** Write integration tests and use tools like Grafana/Prometheus for DB monitoring.

### Conclusion

Effective database design and integration in LLD are crucial for building robust backend systems like the Razorpay payment gateway. Understanding ER modeling, translating it into relational schema, mapping to class models, and adopting patterns like DAO and Repository ensures scalability and maintainability. Applying real-world practices further hardens the system against performance, security, and operational risks.

Mastering these principles sets a strong foundation for building high-quality, production-grade systems in any backend engineering role.
