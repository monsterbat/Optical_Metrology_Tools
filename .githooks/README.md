# .githooks

`pre-commit-local` blocks anything that must not reach a public repository:
measurement data, reports, screenshots, build output, and a list of words.

## Why this exists

`.gitignore` only says "do not add this by default". It does not stop `git add -f`,
and it breaks silently if someone edits the wrong line. This repository is public,
and **a commit that reaches GitHub cannot be taken back** — old commits stay
reachable by their full SHA even after a force push.

So the rule is enforced by a hook that fails closed: if the guard itself cannot
run, the commit is refused. Not being able to save is a smaller problem than
publishing something that cannot be unpublished.

## What it blocks

| Shape | Examples |
|---|---|
| Paths | `test_data/`, `docs/`, `temp/`, `dist/`, `build/` |
| Data and reports | `.jmp` `.xls` `.xlsx` `.csv` `.dat` |
| Images and documents | `.png` `.jpg` `.gif` `.pdf` `.pptx` `.docx` — screenshots leak what text scanners cannot see |
| Words | read from `.git/forbidden-words.txt` |

The word list lives inside `.git/` on purpose: git never tracks anything under
`.git`, so the words themselves are not published by the guard that blocks them.

## Setting it up on a new clone

```bash
git config core.hooksPath .githooks          # or chain from a global hooks dir
printf 'word-one\nword-two\n' > .git/forbidden-words.txt
chmod 600 .git/forbidden-words.txt
```

Without that file the guard refuses every commit, which is the intended behaviour:
no list means no guard.
