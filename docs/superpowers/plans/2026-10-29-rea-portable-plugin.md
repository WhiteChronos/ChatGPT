# REA portable plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans when isolated subagents are unavailable.

**Goal:** Package the independent REA code and safe onboarding Skills for Codex and ChatGPT Web.

**Architecture:** Portable Agent Plugins manifest plus legacy compatibility overlay; tools remain powered by the unchanged SDK server. A remote private MCP connection is configured independently and must be observed in the actual host.

**Tech Stack:** JSON manifests, MCP SDK Python, pytest, Skills.

**Spec:** docs/superpowers/specs/2026-10-29-rea-portable-plugin.md

## Tasks
1. [ ] Write failing tests for plugin identity, skill discovery, onboarding and safe defaults.
2. [ ] Implement manifests, onboarding and operation Skills with explicit remote-MCP gates.
3. [ ] Run all REA tests locally, record SDK-dependent skips and CI verification.
4. [ ] Build plugin distribution ZIP and inspect layout for unsafe paths and secrets.
5. [ ] Publish only isolated REA changes to PR #119; confirm current CI and report host-dependent gates.
