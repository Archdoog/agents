# README, guide, and procedure cases

### readme-lead-in

- surface: readme
- pass: lint
- expect: SLOP003, SLOP004, STE003

```input
This guide will walk you through setup. Let's dive in!
```

- why: A lead-in, a stock phrase, and a contraction.

### doc-overview-steering

- surface: doc
- pass: lint
- expect: SLOP004, SLOP005, SLOP006

```input
## Overview

This section describes the cache. As you can see, it is a crucial component.
```

- why: A lead-in, reader steering, and a generated word under an empty heading.

### clean-how-to

- surface: doc
- pass: lint
- expect: clean

```input
## Rotate the signing key

1. Create a key: `make key`.
2. Upload it to the secret store.
3. If the deploy fails, restore the old key from the backup.
```

- why: A how-to page with one action in each step. A clean case.
