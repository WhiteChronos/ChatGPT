#!/usr/bin/env python3
import argparse

def clamp(v):
    return max(0.0, min(5.0, float(v)))

p=argparse.ArgumentParser(description="Score an AUT Panel improvement proposal (0-100).")
p.add_argument("--frequency", type=float, required=True, help="0-5 occurrence frequency")
p.add_argument("--severity", type=float, required=True, help="0-5 engineering impact")
p.add_argument("--detectability", type=float, required=True, help="0-5 ease of deterministic detection")
p.add_argument("--benefit", type=float, required=True, help="0-5 expected benefit")
p.add_argument("--risk", type=float, required=True, help="0-5 implementation risk")
a=p.parse_args()
frequency, severity, detectability, benefit, risk=map(clamp,[a.frequency,a.severity,a.detectability,a.benefit,a.risk])
raw=(0.25*frequency+0.30*severity+0.15*detectability+0.20*benefit+0.10*(5-risk))/5*100
print(f"{raw:.1f}")
