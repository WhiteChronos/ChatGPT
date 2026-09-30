#!/usr/bin/env python3
import argparse, json
from collections import defaultdict

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input_json")
    p.add_argument("output_json")
    a=p.parse_args()
    with open(a.input_json,"r",encoding="utf-8") as f:
        data=json.load(f)
    totals=defaultdict(lambda:{"cut_mm":0.0,"procurement_mm":0.0,"wire_count":0})
    trace=[]
    for w in data.get("wires",[]):
        key=w["procurement_code"]
        route=float(w["route_mm"])
        origin=float(w.get("origin_termination_mm",0))
        dest=float(w.get("destination_termination_mm",0))
        loop=float(w.get("service_loop_mm",0))
        allowance=float(w.get("manufacturing_allowance",0))
        if allowance < 0:
            raise ValueError("manufacturing_allowance must be non-negative")
        cut=route+origin+dest+loop
        proc=cut*(1+allowance)
        totals[key]["cut_mm"]+=cut
        totals[key]["procurement_mm"]+=proc
        totals[key]["wire_count"]+=1
        trace.append({"wire_id":w.get("wire_id"),"procurement_code":key,"cut_mm":cut,"procurement_mm":proc})
    out={"aggregates":{k:{"wire_count":v["wire_count"],"cut_m":round(v["cut_mm"]/1000,4),"procurement_m":round(v["procurement_mm"]/1000,4)} for k,v in sorted(totals.items())},"trace":trace}
    with open(a.output_json,"w",encoding="utf-8") as f:
        json.dump(out,f,indent=2,ensure_ascii=False)

if __name__=="__main__":
    main()
