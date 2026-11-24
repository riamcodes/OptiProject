# Step 4: time-expanded integer model (JuMP + Gurobi)
# Inputs come from:  python model/export_for_julia.py   ->  model/julia_inputs/
#
# using Pkg; Pkg.add(["JuMP", "Gurobi", "CSV", "DataFrames"])

using JuMP, Gurobi, CSV, DataFrames

arcs  = CSV.read(joinpath(@__DIR__, "julia_inputs", "arcs.csv"), DataFrame; stringtype=String)
rides = CSV.read(joinpath(@__DIR__, "julia_inputs", "rides.csv"), DataFrame; stringtype=String).code
A = 1:nrow(arcs)                                  # one arc = one row

# Handy index lists (which arcs leave / enter each node, which arcs enter each ride)
nodes_out = Dict{Tuple{String,Int},Vector{Int}}()
nodes_in  = Dict{Tuple{String,Int},Vector{Int}}()
for a in A
    push!(get!(nodes_out, (arcs.from[a], arcs.from_slot[a]), Int[]), a)
    push!(get!(nodes_in,  (arcs.to[a],   arcs.to_slot[a]),   Int[]), a)
end
ride_nodes = union(keys(nodes_in), filter(k -> k[1] != "ENTRANCE", collect(keys(nodes_out))))

model = Model(Gurobi.Optimizer)

# ---- YOUR PART -------------------------------------------------------------
# 1. Variables: one binary x[a] per arc
#
# 2. Objective: minimize total (walk + wait) over chosen arcs   -> column arcs.cost_min
#
# 3. Constraints
#    (start)      exactly one arc leaves ("ENTRANCE", 0)
#    (flow)       for every node in ride_nodes: arcs out <= arcs in
#    (visit once) for every ride r: arcs whose `to` is r sum to exactly 1
#
#    Tip: get(nodes_out, node, Int[]) returns an empty list when a node has no arcs.
# -----------------------------------------------------------------------------

optimize!(model)
println("Integer optimum: ", objective_value(model), " min")

# Ride order: follow the chosen arcs from the entrance
chosen = Dict((arcs.from[a], arcs.from_slot[a]) => a for a in A if value(x[a]) > 0.5)
node, order = ("ENTRANCE", 0), String[]
while haskey(chosen, node)
    a = chosen[node]; push!(order, arcs.to[a]); global node = (arcs.to[a], arcs.to_slot[a])
end
println("Order: ", join(order, " -> "))

# LP relaxation: same model with 0 <= x <= 1
relax_integrality(model)
optimize!(model)
println("LP relaxation: ", objective_value(model), " min")
