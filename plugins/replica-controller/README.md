# Replica Controller

## Task-scoped automatic entry points (1.2.0)

The package now contains eleven pinned Replica skills and four integration
skills: replica-workflow, superpowers-workflow, arena-workflow, and the existing
replica-power-arena coordinator. The first three run independently; the
coordinator selects the relevant combination. Official Superpowers and Arena
remain separate dependencies, not copied or reinstalled here.

Skill metadata allows implicit invocation where supported by the host. This
permits host selection during a user task; it does not intercept every message,
start a background service, or grant access to another computer.

The optional deterministic helper selects a plan from an explicit intent:

```powershell
python plugins/replica-controller/scripts/workflow.py plan --system replica --intent compare
python plugins/replica-controller/scripts/workflow.py plan --system superpowers --intent bugfix
python plugins/replica-controller/scripts/workflow.py plan --system arena --intent review
python plugins/replica-controller/scripts/workflow.py plan --system combined --intent build-from-reference
```

The agent reads the selected skills and executes the authorized task. The
helper always reports PLAN_ONLY; it does not invoke models, agents or shells.
`doctor` accepts repeated `--skills-root` and `--available-tool` values to check
local prerequisites. File presence or supplied inventory is not proof that a
new conversation loaded a skill. No periodic verification is configured.

Eleven pinned [Replica skills](https://github.com/Jakeschincariol/replica-skill),
six offline Python tools, and the `replica-power-arena` routing skill. Replica
handles application reconstruction; the existing official Superpowers plugin
guides development; the existing GitHub Arena adapter reviews evidence.

## Sources and scope

- Replica: `Jakeschincariol/replica-skill`, MIT, commit
  `77c9436fb3d18c3d58169efb8caf4fe906b0dc51`. Original skill/tool bytes and
  Jake Schincariol's copyright are preserved; see LICENSE and upstream-lock.json.
- Superpowers: official `obra/superpowers` / installed official marketplace
  plugin. It remains its own runtime; this package does not replace it.
- Arena methodology: `Jakeschincariol/arena-skill`; WhiteChronos's existing
  `plugins/github-arena` provides the MCP review tools.

The upstream repositories stay separate. Only the integration belongs here.
This package provides skills and CLI scripts, not an arbitrary remote-execution
MCP server. Installing it does not change the model, force every conversation,
give ChatGPT web access to Windows or automatically publish chat contents.

## Native Windows

Python 3.8+ is sufficient; the tools use the standard library. From this checkout:

```powershell
python plugins/replica-controller/scripts/replica.py verify
python plugins/replica-controller/scripts/replica.py run contrast plugins/replica-controller/skills/replica-design/tokens.json
python plugins/replica-controller/scripts/replica.py run parity path/to/project/replica/features.csv
```

Other tools: `imgdiff`, `reviews`, `sweep`, `listing`. Consult the corresponding
skill for input formats. Tool exit codes propagate; there is no shell expansion.
The dispatcher refuses unpinned scripts or modified upstream files. Local hashes
detect changes but are not a signature: review changes to the lock itself in Git.

To install all twelve skills in a Codex skill root, first dry-run:

```powershell
python plugins/replica-controller/scripts/replica.py install --dest "$env:USERPROFILE/.codex/skills" --receipt "$env:TEMP/replica-install.json" --dry-run
python plugins/replica-controller/scripts/replica.py install --dest "$env:USERPROFILE/.codex/skills" --receipt "$env:TEMP/replica-install.json"
```

All destinations are checked before copying. Existing matching skills are reused;
different human content is preserved and stops installation. The receipt lists
files and digests. To roll back, remove only receipt-listed files that still have
those digests; leave changed/additional files untouched. No existing skill is
backed up because none is overwritten. New skills become available on the next
Codex turn/session; verify discovery in the host before claiming activation.

The source skills retain Claude examples. The integration router explains native
Windows/Codex paths and the `npm.cmd`/Python adaptations. Project instructions and
existing user authorizations override examples in imported reference material.

## Verification

```powershell
python -B -m unittest discover -s plugins/replica-controller/tests -v
```

The six tools and eleven original skills are also covered by the upstream's
57 tests at the pinned commit. Record installed, tested and host-discovered
states separately. A parity score measures a declared sample of features, not
security, token savings or complete behavior of an application.

## GitHub workflow

Confirm origin, HEAD, branch and local changes; perform scoped work on a branch,
run relevant checks, apply Arena review, and create a PR with exact evidence.
Keep credentials, machine paths, user data and raw model traces out of commits.
Publishing, deployment, purchases and shared-main merges require authorization
for the concrete target. There are no automatic hooks, cron jobs or services.
