"""Balanced radial constant-PQ load flow using backward/forward sweep.
All quantities are per unit on one consistent three-phase base.
"""
import math

DEMO={"load_scale":1.0,"q_support":0.0,"support_bus":"B4","buses":[
 {"id":"B1","parent":"SOURCE","r":0.012,"x":0.025,"p":0.25,"q":0.12},
 {"id":"B2","parent":"B1","r":0.016,"x":0.030,"p":0.22,"q":0.10},
 {"id":"B3","parent":"B2","r":0.020,"x":0.035,"p":0.18,"q":0.09},
 {"id":"B4","parent":"B3","r":0.025,"x":0.040,"p":0.20,"q":0.11}]}

def finite(value, name, low=0, high=100):
    if isinstance(value,bool): raise ValueError(name+" must be numeric.")
    v=float(value)
    if not math.isfinite(v) or not low <= v <= high: raise ValueError(name+" is outside its valid range.")
    return v

def topology(rows):
    if not isinstance(rows,list) or not 1 <= len(rows) <= 100: raise ValueError("Provide 1–100 buses.")
    nodes={}
    for b in rows:
        name=str(b["id"]).strip()
        if not name or name=="SOURCE" or name in nodes: raise ValueError("Bus IDs must be unique and cannot be SOURCE.")
        nodes[name]={"id":name,"parent":str(b["parent"]),**{k:finite(b[k],k) for k in ("r","x","p","q")}}
    order=[]; pending=dict(nodes); seen={"SOURCE"}
    while pending:
        ready=[n for n,b in pending.items() if b["parent"] in seen]
        if not ready: raise ValueError("Network has a cycle or is disconnected from SOURCE.")
        for n in ready: order.append(n); seen.add(n); del pending[n]
    return nodes,order

def solve(nodes,order,scale,support,target):
    v={n:1+0j for n in ["SOURCE"]+order}; converged=False
    for iteration in range(1,501):
        currents={}
        for n in order:
            if abs(v[n])<0.05: raise ValueError("Voltage collapsed in this scenario; reduce load or impedance.")
            b=nodes[n]; s=complex(b["p"]*scale,b["q"]*scale-(support if n==target else 0))
            currents[n]=(s/v[n]).conjugate()
        for n in reversed(order):
            parent=nodes[n]["parent"]
            if parent!="SOURCE": currents[parent]+=currents[n]
        new={"SOURCE":1+0j}
        for n in order:
            b=nodes[n]; new[n]=new[b["parent"]]-complex(b["r"],b["x"])*currents[n]
        error=max(abs(new[n]-v[n]) for n in order); v=new
        if error<1e-10: converged=True; break
    if not converged: raise ValueError("Load flow did not converge in 500 iterations; no valid result reported.")
    rows=[]; loss=0j
    for n in order:
        b=nodes[n]; branch_loss=abs(currents[n])**2*complex(b["r"],b["x"]); loss+=branch_loss
        rows.append({"bus":n,"parent":b["parent"],"voltage_pu":round(abs(v[n]),7),"angle_deg":round(math.degrees(math.atan2(v[n].imag,v[n].real)),5),"branch_current_pu":round(abs(currents[n]),7),"branch_loss_pu":round(branch_loss.real,8)})
    source_current=sum((currents[n] for n in order if nodes[n]["parent"]=="SOURCE"),0j)
    source_power=source_current.conjugate()
    return {"buses":rows,"active_loss_pu":round(loss.real,8),"reactive_loss_pu":round(loss.imag,8),"source_p_pu":round(source_power.real,8),"source_q_pu":round(source_power.imag,8),"iterations":iteration,"min_voltage_pu":min(r["voltage_pu"] for r in rows)}

def analyse(data):
    nodes,order=topology(data["buses"])
    scale=finite(data.get("load_scale",1),"Load scale",0,5)
    support=finite(data.get("q_support",0),"Reactive support",0,5)
    target=str(data.get("support_bus",order[-1]))
    if target not in nodes: raise ValueError("Support bus must exist in the network.")
    base=solve(nodes,order,scale,0,target); scenario=solve(nodes,order,scale,support,target)
    ranking=sorted(scenario["buses"],key=lambda row:row["voltage_pu"])
    return {"summary":[["Lowest voltage",str(scenario["min_voltage_pu"])+" pu"],["Low-voltage bus",ranking[0]["bus"]],["Active losses",str(scenario["active_loss_pu"])+" pu"],["Iterations",str(scenario["iterations"])]],"rows":scenario["buses"],"chart":{"labels":[r["bus"] for r in scenario["buses"]],"values":[r["voltage_pu"] for r in scenario["buses"]],"label":"Bus voltage (pu)","reference":0.95},"notes":["Base minimum voltage: "+str(base["min_voltage_pu"])+" pu. Scenario minimum voltage: "+str(scenario["min_voltage_pu"])+" pu.","Low-voltage ranking is a voltage-magnitude screen, not a voltage-stability index or a collapse-margin calculation.","Reactive support is ideal fixed-Q injection; it is not a dynamic SVC, STATCOM or UPFC model. 0.95 pu is an illustrative threshold."],"baseline":base,"scenario":scenario}
