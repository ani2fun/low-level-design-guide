"""Audit lessons against the prepare-standard: structure, code pairs, real outputs, quizzes, anchors."""
import json, os, re, subprocess, sys, tempfile, unicodedata

FENCE = re.compile(r"^(`{3,})(.*)$")


def blocks(text):
    """Yield (start_line, info, body, end_line) for every fenced block."""
    lines = text.split("\n")
    i = 0
    out = []
    while i < len(lines):
        m = FENCE.match(lines[i])
        if m:
            tick, info = m.group(1), m.group(2).strip()
            j = i + 1
            while j < len(lines) and not lines[j].startswith(tick):
                j += 1
            out.append((i + 1, info, "\n".join(lines[i + 1:j]), j + 1))
            i = j + 1
        else:
            i += 1
    return out, lines


def slug(h):
    h = h.strip().lower()
    h = re.sub(r"<[^>]+>", "", h)
    h = re.sub(r"[`*_]", "", h)
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)
    s = "".join(c for c in h if c.isalnum() or c in " -_" or unicodedata.category(c).startswith("L"))
    return s.replace(" ", "-")


def run_java(src, tmp):
    d = tempfile.mkdtemp(dir=tmp)
    p = os.path.join(d, "Main.java")
    open(p, "w").write(src)
    env = {**os.environ, "JAVA_TOOL_OPTIONS": ""}
    c = subprocess.run(["javac", "-d", d, p], capture_output=True, text=True, cwd=d, env=env)
    if c.returncode:
        return "", c.stderr, 1
    main = re.search(r"class\s+(\w+)[^{]*\{[^}]*?public\s+static\s+void\s+main", src, re.S)
    mains = [m for m in re.findall(r"class\s+(\w+)", src) if os.path.exists(os.path.join(d, m + ".class"))]
    cls = "Main" if os.path.exists(os.path.join(d, "Main.class")) else (main.group(1) if main else mains[-1])
    r = subprocess.run(["java", "-cp", d, cls], capture_output=True, text=True, timeout=60, cwd=d, env=env)
    err = "\n".join(l for l in r.stderr.splitlines() if "JAVA_TOOL_OPTIONS" not in l)
    return r.stdout, err, r.returncode


def run_py(src, tmp):
    r = subprocess.run([sys.executable, "-c", src], capture_output=True, text=True, timeout=60)
    return r.stdout, r.stderr, r.returncode


def audit(path, run=True):
    text = open(path).read()
    bl, lines = blocks(text)
    issues = []
    add = lambda ln, msg: issues.append((ln, msg))

    # frontmatter
    fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not fm:
        add(1, "no frontmatter")
    else:
        for k in ("title:", "summary:", "essential: true"):
            if k not in fm.group(1):
                add(1, f"frontmatter missing {k}")
    for needle, what in [("💡 **The core idea.**", "core-idea callout"),
                         ("You'll be able to", "objectives list"),
                         ("📘 **How to read the Intuition boxes.**", "intuition-reading callout"),
                         ("🧪 **Predict, then check.**", "predict callout"),
                         ('<div class="concept-coach"></div>', "concept coach"),
                         ("## 📚 Sources", "sources heading"),
                         ("<details>", "details question"),
                         ("<abbr title=", "inline abbr citations"),
                         ("border-left:4px solid #da5233", "red gotcha callout")]:
        if needle not in text:
            add(0, f"missing {what}")
    for n, l in enumerate(text.split("\n"), 1):
        if "§" in re.sub(r"<abbr[^>]*>", "", l) and not re.match(r"^\d+\. ", l):
            add(n, "bare §: " + l.strip()[:100])

    # headings / anchors (outside code)
    in_code = set()
    for s, _, _, e in bl:
        in_code.update(range(s, e + 1))
    heads = [slug(re.sub(r"^#+\s*", "", l)) for n, l in enumerate(lines, 1)
             if n not in in_code and re.match(r"^#{1,6}\s", l)]
    for n, l in enumerate(lines, 1):
        if n in in_code:
            continue
        for a in re.findall(r"\]\(#([^)]+)\)", l):
            if a not in heads:
                add(n, f"anchor #{a} has no heading")
        for u in re.findall(r"\]\((/[^)]+)\)", l):
            if not u.startswith("/synapse/"):
                add(n, f"non-synapse link {u}")
        for u in re.findall(r"\]\(((?!https?:|#|/)[^)]+)\)", l):
            add(n, f"relative link {u}")

    # numbered sections: each needs Output/Analysis/Intuition/Mechanism/Concrete bite/Earned rule
    sec_idx = [n for n, l in enumerate(lines, 1) if n not in in_code and re.match(r"^## \d+\.", l)]
    end_idx = sec_idx[1:] + [next((n for n, l in enumerate(lines, 1) if n > (sec_idx[-1] if sec_idx else 0)
                                    and n not in in_code and re.match(r"^## (?!\d)", l)), len(lines))]
    for s, e in zip(sec_idx, end_idx):
        body = "\n".join(lines[s - 1:e - 1])
        if "Mental-model" in lines[s - 1] or "summary" in lines[s - 1].lower() or "checklist" in lines[s - 1].lower():
            continue
        for k in ["**Output", "**Analysis.**", "**Intuition.**", "Mechanism.", "Concrete bite.", "Earned rule."]:
            if k not in body:
                add(s, f"section '{lines[s-1][:50]}' lacks {k}")

    # code pairs + outputs
    tmp = tempfile.mkdtemp()
    for idx, (s, info, body, e) in enumerate(bl):
        if info == "quiz":
            try:
                q = json.loads(body)
                if q["answer"] not in q["options"]:
                    add(s, "quiz answer not in options")
            except Exception as ex:
                add(s, f"quiz JSON invalid: {ex}")
        if info.startswith("java") and "run" in info:
            nxt = bl[idx + 1] if idx + 1 < len(bl) else None
            if not nxt or not nxt[1].startswith("python run") or any(x.strip() for x in lines[e:nxt[0]-1]):
                add(s, "java run not immediately followed by python run")
                continue
            if "ANTI-PATTERN" in body and not re.search(r"ANTI-PATTERN.*Do not copy it", body):
                add(s, "anti-pattern marker not at top")
            # gather following output blocks until next java run / heading
            outs = []
            k = idx + 2
            while k < len(bl) and not bl[k][1].startswith(("java", "python", "quiz")):
                label = lines[bl[k][0] - 3] if bl[k][0] >= 3 else ""
                label = (lines[bl[k][0] - 2] or label)
                outs.append((label, bl[k][2], bl[k][0]))
                k += 1
                if len(outs) == 2:
                    break
            outs = [o for o in outs if "Output" in o[0]]
            if not outs:
                add(s, "no Output block after pair")
                continue
            if not run:
                continue
            jo, je, jc = run_java(body, tmp)
            po, pe, pc = run_py(nxt[2], tmp)
            if jc:
                add(s, f"java fails: {je.strip()[:300]}")
            if pc:
                add(nxt[0], f"python fails: {pe.strip()[:300]}")
            jo, po = jo.rstrip("\n"), po.rstrip("\n")
            illus = "illustrative" in "\n".join(lines[outs[0][2] - 4:outs[0][2]])
            for label, ob, ln in outs:
                ob = ob.rstrip("\n")
                if "Java" in label:
                    if ob != jo and not illus:
                        add(ln, f"Java output mismatch\n--doc--\n{ob}\n--real--\n{jo}")
                elif "Python" in label:
                    if ob != po and not illus:
                        add(ln, f"Python output mismatch\n--doc--\n{ob}\n--real--\n{po}")
                else:
                    if (ob != jo or ob != po) and not illus:
                        add(ln, f"shared output mismatch\n--doc--\n{ob}\n--java--\n{jo}\n--py--\n{po}")
    return issues


if __name__ == "__main__":
    run = "--norun" not in sys.argv
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        iss = audit(p, run)
        print(f"===== {p}: {len(iss)} issues")
        for ln, m in iss:
            print(f"  L{ln}: {m}")
