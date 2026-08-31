# Module 1 Source

This directory contains the implementation of the AML-to-UTM PoC.

Recommended responsibility boundaries:

```text
aml/
    language definition, parser, interpreter

utm/
    UTM model and simulator

translation/
    AML-IR → UTM-IR

verification/
    semantic equivalence

certificate/
    Module 1 certificate generation
```

Do not implement future reversible or quantum stages here.
