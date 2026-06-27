"""Figure 2: 12 cross-layer component isomorphisms (bipartite graph).

Left side: 6 representative model-layer components.
Right side: 6 representative coordination-layer components.
Lines: solid = verified 8 pairs, dashed = predicted 4 pairs.
"""
import os
import graphviz

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# Build 12 pair labels, first 8 = verified (solid), last 4 = predicted (dashed)
pairs = [
    # verified (8)
    ("Hidden state h_t", "Context state", "verify"),
    ("Encoded input e", "User request", "verify"),
    ("LTI (A, B)", "Inbox decay exp(-lambda t)", "verify"),
    ("ACT Halting", "Task complexity + early stop", "verify"),
    ("MoE (64+2)", "Sparse activation (8+3)", "verify"),
    ("Attention window", "Rolling inbox", "verify"),
    ("LayerNorm (RMSNorm)", "Coordination bus quality gate", "verify"),
    ("KV cache", "Shared-lessons cache", "verify"),
    # predicted (4)
    ("Decoding (top-K)", "Dispatch top-K agents", "predict"),
    ("Position enc (RoPE)", "Time-stamp + lambda", "predict"),
    ("MoE router bias", "SkillDAG typed routing", "predict"),
    ("Beam termination", "ACT-style early stop", "predict"),
]

dot = graphviz.Digraph("iso12", format="png")
dot.attr(rankdir="LR", bgcolor="white", splines="spline",
         label=r"12 Cross-Layer Component Isomorphisms (8 verified + 4 predicted)",
         labelloc="t", fontsize="18", fontname="Helvetica")
dot.attr("node", shape="box", style="rounded,filled", fontname="Helvetica", fontsize="11")
dot.attr("edge", fontname="Helvetica", fontsize="9")

# Left column (model layer)
with dot.subgraph(name="cluster_model") as c:
    c.attr(label="Model layer (LLM)", style="rounded,dashed", color="#4C9BE8",
           fontcolor="#1f4f7a", fontsize="13")
    for i, (m, _, _) in enumerate(pairs):
        c.node(f"m{i}", m, fillcolor="#DCEBFA", color="#4C9BE8")

# Right column (coordination layer)
with dot.subgraph(name="cluster_coord") as c:
    c.attr(label="Coordination layer (agent)", style="rounded,dashed", color="#3D9970",
           fontcolor="#1f5a3d", fontsize="13")
    for i, (_, co, _) in enumerate(pairs):
        c.node(f"c{i}", co, fillcolor="#DCEEDD", color="#3D9970")

# Edges
for i, (_, _, status) in enumerate(pairs):
    if status == "verify":
        dot.edge(f"m{i}", f"c{i}", color="#1f4f7a", penwidth="1.6",
                 label="verified" if i == 0 else "")
    else:
        dot.edge(f"m{i}", f"c{i}", color="#E08A3C", style="dashed",
                 penwidth="1.4", label="predicted" if i == 8 else "")

# Legend (separate cluster, invisible nodes)
with dot.subgraph(name="cluster_legend") as c:
    c.attr(label="Edge legend", style="rounded", color="gray", fontcolor="gray", fontsize="10")
    c.node("lg_v", "verified (5/5 sub-tests)", shape="plaintext")
    c.node("lg_p", "predicted (this paper)", shape="plaintext")
    c.edge("lg_v", "lg_p", style="invis")
    c.edge("lg_v", "lg_p", color="#1f4f7a", penwidth="1.6",
           label=" solid = verified ", style="solid")
    # Render two legend rows
    c.node("lg_v2", "solid", shape="plaintext")
    c.node("lg_p2", "dashed", shape="plaintext")
    c.edge("lg_v2", "lg_p2", color="#E08A3C", style="dashed", penwidth="1.4")

OUT = os.path.join(OUT_DIR, "fig2_12_isomorphisms")
src = dot.render(filename=OUT, cleanup=True)
print(f"Wrote {src} ({os.path.getsize(src)} bytes)")