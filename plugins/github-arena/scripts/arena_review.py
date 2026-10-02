#!/usr/bin/env python3
"""Plan Arena-style review passes and deal strategy cards for GitHub work.

ChatGPT-compatible planning adapter inspired by Jakeschincariol/arena-skill.
It does not spawn subagents itself. Python 3.8+, standard library only.
"""
from __future__ import annotations
import argparse, itertools, json, random

REASONING = [
("first-principles","First principles"),("inversion","Inversion"),("analogy","Analogy"),
("adversarial","Adversarial"),("constraint-first","Constraint first"),("worked-example","Worked example"),
("socratic","Socratic"),("contrarian","Contrarian"),("systems-thinking","Systems thinking"),
("decomposition","Decomposition"),("working-backwards","Working backwards"),("probabilistic","Probabilistic"),
("dialectical","Dialectical"),("evidence-first","Evidence first"),("expert-panel","Expert panel")]
WORKFLOWS = [
("draft-critique-rewrite","Draft, critique, rewrite"),("outline-first","Outline first"),
("test-first","Test first"),("research-then-synthesise","Research, then synthesise"),
("three-drafts","Three drafts, pick one"),("requirements-checklist","Requirements checklist"),
("iterative-deepening","Iterative deepening"),("build-then-break","Build, then break"),
("smallest-version-first","Smallest version first"),("options-matrix","Options matrix"),
("open-questions-first","Open questions first"),("write-then-restructure","Write, then restructure")]
STRATEGIES = [
("simplest","Simplest thing that works"),("maximal-rigour","Maximal rigour"),
("user-empathy","User empathy first"),("edge-cases-first","Edge cases first"),
("speed","Speed"),("defensive","Defensive"),("clarity","Clarity above all"),
("completeness","Completeness"),("fewest-moving-parts","Fewest moving parts"),
("explicit-trade-offs","Explicit trade-offs"),("built-to-last","Built to last"),
("concrete-specifics","Concrete specifics")]
RUBRIC={"correctness":30,"completeness":25,"robustness":20,"specificity":15,"clarity":10}

def bracket_sizes(n):
    values=[n]
    while values[-1]>1: values.append((values[-1]+1)//2)
    return values

def upstream_call_estimate(n):
    matches=sum(x//2 for x in bracket_sizes(n)[:-1])
    return n+5*matches

def deal(n,seed):
    cards=list(itertools.product(REASONING,WORKFLOWS,STRATEGIES))
    if n<1 or n>len(cards): raise SystemExit(f"agents must be between 1 and {len(cards)}")
    rng=random.Random(seed); rng.shuffle(cards); return cards[:n]

def plan(args):
    n=16 if args.quick else args.agents
    sizes=bracket_sizes(n)
    print(json.dumps({"strategies":n,"rounds":len(sizes)-1,"alive_per_round":sizes,
      "upstream_equivalent_subagent_calls":upstream_call_estimate(n),
      "note":"This adapter plans the arena; it does not spawn isolated subagents."},indent=2))

def cards(args):
    n=16 if args.quick else args.agents
    rows=[]
    for i,(r,w,s) in enumerate(deal(n,args.seed),1):
        rows.append({"id":f"a{i:03d}","reasoning":{"id":r[0],"name":r[1]},
          "workflow":{"id":w[0],"name":w[1]},"strategy":{"id":s[0],"name":s[1]}})
    print(json.dumps({"seed":args.seed,"cards":rows},indent=2))

def rubric(_args): print(json.dumps(RUBRIC,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="command",required=True)
    q=sub.add_parser("plan"); q.add_argument("--agents",type=int,default=16); q.add_argument("--quick",action="store_true"); q.set_defaults(func=plan)
    c=sub.add_parser("cards"); c.add_argument("--agents",type=int,default=4); c.add_argument("--quick",action="store_true"); c.add_argument("--seed",type=int,default=7); c.set_defaults(func=cards)
    r=sub.add_parser("rubric"); r.set_defaults(func=rubric)
    args=p.parse_args(); args.func(args)
if __name__=="__main__": main()
