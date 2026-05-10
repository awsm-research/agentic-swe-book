## 11.3 Software Versioning — A Promise to Your Users

A version number is a contract. It tells whoever consumes your software what kind of change they are receiving and how cautious they should be about installing it. If the contract is honest, downstream users can upgrade with confidence; if it is dishonest, they pin to old versions and the ecosystem fragments.

### Semantic Versioning

The dominant convention for libraries is *semantic versioning* (SemVer), formalised by Tom Preston-Werner in 2013 ([SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)). Versions take the form `MAJOR.MINOR.PATCH`, with rules:

- Increment **PATCH** for backwards-compatible bug fixes — the API is unchanged.
- Increment **MINOR** for backwards-compatible additions — new endpoints, new optional parameters.
- Increment **MAJOR** for incompatible changes — removed methods, renamed fields, behavioural changes that break callers.

The contract is that `^1.4.2` (any 1.x version ≥ 1.4.2) is safe to upgrade automatically; a jump to `2.0.0` is not. SemVer works when authors honour it. It fails when they do not — which is most of the time. The Python typing library `typing-extensions` and the JavaScript date library `moment` have both shipped breaking changes in patch releases. Library authors under-version because *their* change feels small; the consumer's broken build is two ecosystems away.

### Calendar Versioning

For products and services, time is often a more honest signal than feature scope. *Calendar versioning* (CalVer) encodes the release date in the version string: `2024.7.1` (year, month, sequence). Ubuntu (`24.04`), JetBrains IDEs (`2024.2`), and pip (`24.1`) all use CalVer. The advantage is that users can see at a glance how old their installation is and whether the security team's "patch within 90 days" policy applies. The disadvantage is that CalVer carries no information about backwards compatibility; consumers must read the changelog rather than trust the number.

A useful rule of thumb: **libraries use SemVer, applications use CalVer.** A library is consumed by other code that needs a compatibility contract; an application is consumed by humans who want to know whether they are running last week's binary.

### Pre-releases and Build Metadata

SemVer also defines suffixes:

- `-alpha`, `-beta`, `-rc.1` — pre-releases, ordered before the unsuffixed version (`1.5.0-rc.1` is older than `1.5.0`).
- `+sha.abc1234` — build metadata, ignored for ordering. Useful for traceability: the version `1.5.0+sha.abc1234` says "release 1.5.0, built from commit abc1234".

Pin pre-release suffixes in lockfiles — `^1.5.0` does not match `1.5.0-rc.1` by default, which has surprised more than one team racing to fix a release-candidate bug.

### Anti-patterns

A few versioning practices are almost always wrong:

- **ZeroVer** — staying on `0.x` forever (`0.142.0`) to "avoid the commitment" of 1.0. The convention is that 0.x has *no* compatibility guarantees, so every minor release can break consumers. If your library has users, ship 1.0.
- **Marketing versions** — jumping from `4.x` to `7.0` because the salesperson wanted a bigger number. This breaks every dependency tool that assumes versions are monotonic.
- **Floating tags in production** — depending on `latest`, `:stable`, or `^1.0.0` in a Dockerfile. The build is no longer reproducible; the same `docker build` next month produces a different image.

### Case: The left-pad and colors.js Incidents

In March 2016, a developer named Azer Koçulu unpublished his eleven-line `left-pad` package from npm after a trademark dispute. Within hours, builds across the JavaScript ecosystem failed — including those of Babel, React, and at one point, Atom — because they depended on `left-pad` transitively, with floating version ranges, and had no local cache ([Williams, 2016](https://www.theregister.com/2016/03/23/npm_left_pad_chaos/)). The ecosystem learned to pin and to mirror.

The lesson did not stick for everyone. In January 2022, the maintainer of the `colors.js` package (used by ~22,000 dependent packages) deliberately published a version that printed `LIBERTY LIBERTY LIBERTY` in a loop and crashed any process that imported it. Floating version ranges propagated the sabotage to thousands of build pipelines overnight ([Sharma, 2022](https://www.bleepingcomputer.com/news/security/dev-corrupts-npm-libs-colors-and-faker-breaking-thousands-of-apps/)).

Both incidents make the same point. **Floating versions outsource your release engineering to strangers.** A reproducible build pins every dependency, transitively, by exact version — and ideally by content hash.

---
