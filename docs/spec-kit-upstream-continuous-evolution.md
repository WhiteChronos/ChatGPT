# Spec Kit upstream tracking and controlled continuous evolution

Official source: https://github.com/github/spec-kit (MIT). WhiteChronos uses six complementary local-document skills, not cloned upstream runtime.
Official upstream SDD lifecycle documented: constitution -> specify -> plan -> tasks -> implement -> converge.
The six-file method from the user video is a **mapping**, not a claim that these are exact Spec Kit-native commands.

## Governed update loop
1. Identify an upstream tagged release and its exact SHA; compare with last reviewed baseline.
2. Classify changes: core commands, templates, breaking integrations, dependency or security behavior.
3. Reproduce an observed deficiency in one of six skill workflows or the reference validator.
4. Propose minimal revision, test valid and adversarial six-file fixture sets.
5. Compare requirements, architecture, constitution/rules, tasks, memory and scenarios; do not remove critical constraints.
6. Attach evidence to a draft PR; human review and explicit SHA-scoped merge consent.
7. Track feedback across later tasks. Do not claim automatic background self-learning or installation from GitHub to ChatGPT.

## Boundaries
The GitHub repository stores the *configuration and proof*, not a running ChatGPT Web plugin. Updating skills in GitHub does not auto-update installed ChatGPT skills. No scheduled upstream sync is activated by this document. No merge, deploy, paid inference, remote host setup or silent installation.
