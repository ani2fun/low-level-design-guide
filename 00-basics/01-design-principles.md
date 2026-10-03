Software design principles are guidelines that help software developers create systems that are easy to understand, maintain, and extend. These principles can be applied at both the high-level and low-level design stages.

Here are three cornerstone software design principles: **DRY**, **KISS**, and **YAGNI**.

---

## 1. DRY: Don't Repeat Yourself

> Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.

In simple terms, avoid duplication of logic or code. Repeating code makes the system hard to maintain and error-prone. If a change is required, you might forget to update all occurrences.

**Importance:**

* Reduces redundancy
* Easier maintenance
* Single point of change

### Example

**Bad Code (Violates DRY):**
The logic for calculating the area is repeated. If we need to change the logic, we have to do it in multiple places.

```python
if __name__ == "__main__":
    length1 = 10
    width1 = 5
    area1 = length1 * width1
    print("Area1:", area1)

    length2 = 8
    width2 = 4
    area2 = length2 * width2
    print("Area2:", area2)

```

**Good Code (Follows DRY):**
We create a single `calculateArea` method. Now, logic changes only happen in one place.

```python
class AreaCalculator:
    @staticmethod
    def calculateArea(length, width):
        return length * width

if __name__ == "__main__":
    area1 = AreaCalculator.calculateArea(10, 5)
    area2 = AreaCalculator.calculateArea(8, 4)

    print("Area1:", area1)
    print("Area2:", area2)

```

### Applying DRY in Practice

* Identify repetitive code and replace it with a single, reusable code segment.
* Extract common functionality into methods or utility classes.
* Leverage libraries and frameworks when available.
* Refactor duplicate logic regularly across classes or layers.

### When Not to Use DRY

* **Premature Abstraction:** Don't extract common code too early. Two code blocks might look similar now but change in different ways later. Extracting them can create unnecessary coupling.
* *Example:* If `AdminReport` and `UserReport` currently share `generateReport()` logic but are likely to develop different formatting rules later, combining them makes future changes harder.


* **Performance-Critical Code:** Don't apply DRY if it causes inefficiency. Sometimes, repeating optimized low-level logic is faster than calling a generalized, reusable method (which introduces function calls, indirection, or blocks inlining).
* *Example:* In a game engine, small arithmetic might be written directly inside a hot loop instead of a generic helper function to keep the path highly optimized.


* **Sacrificing Readability:** If extracting repeated code makes the codebase less readable, prefer clarity.
* *Example:* Instead of a generic `process()` method handling unrelated operations via flags, keep clear, explicit methods like `validateUser()` and `validateOrder()`.


* **Legacy Codebases:** Don't refactor for DRY's sake unless necessary and well-tested. Introducing DRY can accidentally change behavior if automated tests are missing.
* *Example:* Combining validation code in an old, untested payment system might break subtle functionality. Leave it alone unless modifying that specific feature.



---

## 2. KISS: Keep It Simple, Stupid

> Simplicity should be a key goal in design, and unnecessary complexity should be avoided.

Use the simplest possible solution that works. Avoid clever, convoluted, or overengineered code.

**Importance:**

* Easier debugging
* Improved readability
* Better maintainability
* Faster development

### Example

**Bad Code (Too Complex):**
This uses extra variables, adds unnecessary if-else logic, and makes the code longer and harder to follow.

```python
class NumberUtils:
    @staticmethod
    def isEven(number):
        # Using unnecessary logic to determine evenness
        isEven = False

        if number % 2 == 0:
            isEven = True
        else:
            isEven = False

        return isEven

```

**Good Code (Simple and Clear):**
This is a simple, one-liner solution that is easy to read and avoids overengineering.

```python
class NumberUtils:
    @staticmethod
    def isEven(number):
        return number % 2 == 0

```

---

## 3. YAGNI: You Aren't Gonna Need It

> Always implement things when you actually need them, never when you just foresee that you need them.

Don't add functionality until it is necessary. Avoid building features that you think you *might* need in the future. This keeps the codebase clean and reduces waste.

**Importance:**

* Reduced waste
* Simplified codebase
* Faster development

### Example

Assume you are building a note-taking app to create and view notes. If you start thinking ahead—*"What if later they want categories? Or tagging? Or syncing with Google Drive? I should prepare for that!"*—you create unnecessary complexity and waste time on features that may never be prioritized.

### When Not to Use YAGNI

* **When requirements are well-known:** If a feature is guaranteed and soon to be implemented, preparing for it now might be more efficient.
* *Example:* You're writing a messaging service currently supporting text, but image support is committed for two sprints away. Designing the data model to handle attachments now saves significant refactoring later.


* **Performance-Critical Areas:** In systems where performance is a first-class concern, preemptively building and testing real-world usage patterns can catch bottlenecks early before architecture is locked in.