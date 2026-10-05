# Plan: redo the seven older lessons to the prepared-lesson standard

Status: nothing has been rewritten yet. This branch only carries this plan and the checker.
Before merging into `main`, move `_plans/` to `_docs/` (local-only, gitignored) and delete it from the branch.

## 1. Decisions already made by Aniket

- **Redo all seven lessons**, starting from the original text at commit `00009b2`, not from the
  current rewrites. Use `git show 00009b2:<path>` to get each original.
- **Behavioural split (approved):**
  1. `04-design-patterns/03-behavioural-design-patterns.md` (URL kept): Strategy, Template Method, State.
     `01-oop/03` links here for Template Method.
  2. `04-design-patterns/04-behavioural-requests-and-undo.md`: Command, Chain of Responsibility, Memento.
  3. `04-design-patterns/05-behavioural-object-communication.md`: Observer, Mediator.
  4. `04-design-patterns/06-behavioural-traversal.md`: Iterator, Visitor.
  Delete the agent-created `04-behavioural-state-execution.md` and `05-behavioural-routing-messages.md`.
- **Finish by merging into `main`**, pushing, and deleting the working branch.

## 2. Audit of the earlier agent rewrites (why they are being redone)

What passed: all code examples ran, the printed outputs matched, the quiz JSON was valid, and
`dev-tools/validate-book` reported "✓ renders".

What failed:
- The behavioural file was split without asking first.
- Content was lost:
  - Behavioural went from 4,001 lines to about 1,700, creational from 2,077 to 595, and structural from 2,344 to 917.
  - **Builder is missing**. The creational table of contents still links to `#3-builder-pattern`.
  - All 27 Mermaid class diagrams were dropped from the SOLID, creational, structural and behavioural lessons.
  - The "problem, then its issues, then the solution" walk-throughs, the real-world examples, and the pros and cons sections were all cut.
- Missing from every rewritten lesson:
  - the concept coach block (`<div class="concept-coach"></div>`) under "Your Turn";
  - inline `<abbr title="…">[n]</abbr>` citations;
  - one quiz per objective (each lesson had only 2);
  - the red `#da5233` callout around the gotcha table;
  - the three-step "How to read the Intuition boxes" callout.
- Wrong styling and content:
  - "Predict, then check" used `#8e155c` instead of `#6d28d9`, and gave the answer straight away.
  - Most Earned rules don't state a cost.
  - The "Concrete bite" entries were analogies, not runnable surprises.
- Factual errors to fix, and to list in the commit messages:
  - SOLID says Robert C. Martin "introduced" SOLID and that his 2002 book is "the origin of the SOLID acronym". Michael Feathers coined the acronym. OCP comes from Bertrand Meyer (1988), and LSP from Barbara Liskov (1987, and Liskov & Wing 1994).
  - Creational gives the Factory *Method* definition ("subclasses alter the type") but shows a static simple factory. It also says that editing that factory follows OCP.
  - UML:
    - It says interfaces contain "only abstract methods", which has been false since Java 8 (default and static methods).
    - It presents `<<abstract>>` as the UML notation for an abstract class. UML's own notation is an italic name or `{abstract}`; `<<abstract>>` is a tool convention.
    - Section 3 says the relationships are "explained individually" below, and nothing follows.
    - The `<details>` question asks about class-diagram perspectives the lesson never teaches.
  - Original `01-oop/05`:
    - It calls `String name` a "primitive field" (String is an immutable reference type).
    - It says `Cloneable` signals "to the JVM". It actually tells `Object.clone()` that a field-for-field copy is legal.
    - It says "If Address did not override clone(), … would fail". It is a *compile* error, because `Object.clone()` is protected.
    - The shallow-vs-deep table says shallow cloning does not copy object references. It does copy them: it copies the references, not the objects they point to.
    - Its "Efficiency" and "Working with Immutable Objects" reasons for cloning are dubious. Remove them or fix them.
- The two practice problems in `01-oop/05` (University/College and Library cloning) were in the
  original as prose. The agent converted them to practice blocks in a **non-standard format**: an empty `java run` was put inside
  `problem`, and the test cases used `input`/`output`. Re-do them in the standard format used by `01-oop/03`:
  the `problem` block with the statement, then a `java run` starter with TODOs, then `testcases` with
  `args`/`cases` (each arg is one stdin line), then an `editorial` block containing a `java solution`.

## 3. Order of work (one commit per lesson or chapter)

1. `01-oop/05-relationships-and-object-behaviour.md`
2. `02-solid-principles/01-solid-principles.md`
3. `03-uml/00-uml.md`
4. `04-design-patterns/00-introduction-design-patterns.md`, `01-creational…`, `02-structural…`
5. The behavioural split into four lessons (see section 1)
6. Validate, merge into `main`, push, and delete the branch

### Detailed outline for lesson 1 (`01-oop/05`), already worked out

H1: "Relationships & Object Behaviour — Who Owns Whom". Sections:
1. **Association.** Use the Person/Passport (one-to-one) and Teacher/Students (one-to-many) examples, and add Student/Course (many-to-many).
   *Concrete bite:* `Teacher` keeps the caller's list. Adding a student to that list after the teacher is created changes whom the teacher teaches.
   *Earned rule:* decide whether to make a defensive copy of the collection you receive.
2. **Aggregation.** A Department and its Employees: when the department is dropped, the employees still exist.
   *Concrete bite:* one employee belongs to two departments at once. Aggregation allows that sharing, and composition does not.
3. **Composition.** A House creates its Rooms. Put the ANTI-PATTERN first: `getRooms()` returns the internal list, so outside code can
   add a Room and keep a Room alive after the house is gone. Then show the fix: an unmodifiable view in Java, a tuple in Python.
   *Concrete bite:* in a garbage-collected language, "the part dies with the whole" is only true if no reference to the part escapes.
   Cite UML 2.5.1 §9.5.3 for composite aggregation (paraphrase, don't quote). Add the University/College practice problem.
4. **Shallow copy.** Person/Address with `super.clone()`, and `copy.copy` in Python.
5. **Deep copy.** Show both a recursive `clone()` and a copy constructor (preferred), and `copy.deepcopy` in Python.
   Make the `final` field + `clone()` problem a Predict item, and run it first.
   Add the Library cloning practice problem.
6. Mental-model summary, red gotcha table, then 5 quizzes (one per objective) and a `<details>` question, then Sources, the Predict callout, and Your Turn with the concept coach.
Sources: the OMG UML 2.5.1 specification; the `Object.clone()` and `Cloneable` Javadoc for Java SE 21; Bloch, *Effective Java*, 3rd edition, Item 13;
and the documentation for Python's `copy` module.
Java guide link: `/synapse/programming-languages/java/classes-and-objects/references-equality-and-the-object-model`
(already used in the repo). **Verify every Java guide link exists** before using it.

## 4. Rules (from the original prompt; these are not negotiable)

- Copy the structure, tone and callout `<div>` styles from `00-basics/01-design-principles.md`, `01-oop/02`–`04`,
  and `06-multithreading-concurrency/*`. `01-oop/03` is the closest model for these lessons.
- Every example is a `java run` fence, then a blank line, then a `python run` fence. Python uses only the standard library.
- Run every example on Java 21 and Python 3.11, and paste the real output byte for byte. Label separate outputs when Java and Python differ.
  Label output that changes from run to run as *(illustrative — …)*.
- Put `// ⚠️ ANTI-PATTERN — … Do not copy it.` in deliberately bad code. Run every Predict answer and every claimed behaviour.
- The quiz JSON must be valid, and each `answer` must equal one of its `options` exactly.
- Prose: write complete plain sentences. No bare "§N" in prose; it is fine inside `<abbr>` titles and the Sources list. No private jargon.
  Define each term where it first appears. Quote sources exactly or paraphrase them; never invent a quotation.
- Links: `/synapse/low-level-design/<chapter>/<lesson>`, with the NN- prefixes dropped. Every table-of-contents anchor must match a heading.
- Don't touch `07-best-practices` or `08-practice-lld-design-system`.
- Commits: author and committer must be `Aniket Kakde <a.r.kakde@gmail.com>`, with **no** Co-Authored-By, Claude-Session or any other
  Claude attribution. One commit per lesson or chapter. Each message says what changed and why, and lists the factual errors fixed.

## 5. Tools

- `python3 _plans/check_lessons.py <lesson.md> …` checks the following:
  - frontmatter and the required callouts;
  - table-of-contents anchors and link forms;
  - Java/Python pairing;
  - quiz JSON;
  - and it **compiles and runs every pair**, comparing the results with the documented outputs.
  Add `--norun` to check structure only. It flags numbered sections without code, which is expected for prose-only sections.
  It also flags `java run` starters inside practice blocks; ignore those.
- Book validator: clone `https://github.com/ani2fun/synapse` and run `dev-tools/validate-book <path-to-this-repo>`
  (needs cargo). It must print "✓ renders". The one warning about `order: 4` in `book.json` is already known.
