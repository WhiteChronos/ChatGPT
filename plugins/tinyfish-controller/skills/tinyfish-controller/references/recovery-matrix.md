# TinyFish recovery matrix

| Finding | Classification | Action |
| --- | --- | --- |
| TinyFish service/account probe succeeds | `PASS` | Service is usable for capabilities independently proven available. |
| Service probe succeeds but Browser Profile listing/lookup fails | `DEGRADED` | Keep search/fetch usable; stop only profile-dependent browser work. |
| Browser Profile login is required | `USER_ACTION_REQUIRED` | Use provider-managed login; never request the password in chat. |
| Browser Profile creation/action is blocked by host/platform policy | `HOST_POLICY_BLOCKED` | Do not bypass policy and do not modify source code to fabricate support. |
| Browser run returns timeout/error | provider run remains authoritative | Poll the same run; do not start a duplicate run automatically. |
| Monitor requested without explicit ongoing-monitoring intent | `NOT_APPLICABLE` | Do not create or run a monitor. |
| Paid operation lacks sufficient wallet/credits | `USER_ACTION_REQUIRED` | Report the provider response; do not top up or change auto-reload silently. |
