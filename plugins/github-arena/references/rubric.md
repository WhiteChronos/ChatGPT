# Arena review rubric

| Criterion | Weight | Question |
| --- | ---: | --- |
| Correctness | 30 | Is it technically and factually right? |
| Completeness | 25 | Does it meet every stated requirement? |
| Robustness | 20 | Does it survive attacks, edge cases, and regressions? |
| Specificity | 15 | Can the user act without guessing? |
| Clarity | 10 | Is it easy to understand and apply? |

Weighted total = `(correctness*30 + completeness*25 + robustness*20 + specificity*15 + clarity*10) / 10`.

A verified fatal flaw makes a candidate ineligible to beat a non-fatal candidate. On a tie, prefer fewer standing defects, then higher correctness.
