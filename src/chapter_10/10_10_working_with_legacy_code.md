## 10.10 Working with Legacy Code

Feathers' definition is worth restating: *legacy code is code without tests*. Under this definition, code an agent produced last week with no tests is legacy code, regardless of its age. The techniques for working with legacy systems are therefore relevant to every team using AI assistants.

The key concept is the *seam* — a place where you can change behaviour without editing the code itself. A function that takes a database connection as a parameter has a seam at the parameter; you can pass a fake connection in tests. A function that constructs the connection internally does not have a seam, and must be refactored before it can be tested. Identifying seams is the first step in taming legacy code.

Feathers' *sprout method* and *wrap method* techniques add new functionality alongside legacy code without modifying it. New code is written cleanly, with tests; legacy code is left alone until it can be incrementally absorbed. The technique is the small-scale version of the strangler fig.

### Code Archaeology

When the original author is unavailable — and on a long-lived system, this is the norm rather than the exception — the commit history becomes the primary source. `git log --follow` traces a file's history across renames; `git blame` identifies the last author of each line; commit messages, when written carefully, preserve the *why* that the code itself does not record. Teams that write disposable commit messages ("WIP", "fix bug", "address review") are accumulating a kind of historical debt — they are deleting their own future investigative tools.

---
