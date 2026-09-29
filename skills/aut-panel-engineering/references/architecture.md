# Architecture

Engineering loop:

`BOOTSTRAP -> DATACENTER -> DATASHEET -> SELECT -> LI -> LOAD -> BOM -> LAYOUT -> RENDER -> QA -> MEMORY -> RELEASE`

Learning loop:

`OBSERVE -> FEATURES -> LEARN -> PROPOSE -> SANDBOX -> QA -> HUMAN_GATE -> APPLY -> VERSION`

The learning loop may improve implementation, layout search, QA prioritization, or tool selection. It cannot bypass the engineering loop.

Each panel has isolated namespaces for component instances, sources, I/O, loads, LI/BOM, layout/render, QA, memory and training examples. Shared manufacturer data may be referenced, but panel-specific state must not be mixed.
