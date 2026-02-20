include "globals.mzn";
include "lex_lesseq.mzn";

int: m;
set of int: courier = 1..m;
array[courier] of int: l;

int: n;
set of int: items = 1..n;
array[items] of int: s;

set of int: dis = 1..n+1;
array[dis, dis] of int: D;

array[courier, dis] of var dis: H;
int :max_load = max(l) + 1;
array[items] of int: max_dis = sort([max(j in items)(D[i,j]) | i in items]);
array[courier] of var 0..max_load: couriers_loads;
array[courier] of var 0..sum(D): total_distance;
% Load constraint per courier(not exceed the capacity)
constraint 
    forall(i in courier) (
        sum(j in items where H[i,j] != j)(s[j]) <= l[i]
        
    );
% Ensure each courier returns to the depot
constraint 
    forall(i in courier) (
        H[i, n+1] != n+1
    );
% Ensure each item is assigned to one courier
constraint 
    forall(j in items) (
        sum(i in courier)(H[i, j] != j) = 1
    );

% Ensure valid routnig (subcircuit)
constraint forall(k in courier) (
    subcircuit([H[k, i] |i in dis]) 
);
%symmetry_breaking:higher load couriers first
constraint forall(k in 1..m-1) (
    couriers_loads[k] >= couriers_loads[k+1]
);

constraint forall(c in courier) (
    total_distance[c] = sum(i in dis where H[c, i] != i) (D[i, H[c, i]])
);  % Calculate total distance traveled by each courier

% Bounds for Objective
int: lowbound = max(i in items)(D[n+1,i] + D[i,n+1]);
int: upbound = sum(i in items)(max(j in dis)(D[i, j])) * m;
var lowbound..upbound: obj;

% Objective
constraint obj = max(c in courier) (total_distance[c]); 

solve :: int_search(H, dom_w_deg, indomain_min) 
      :: restart_luby(200)
      ::relax_and_reconstruct(array1d(H),70)
         minimize obj;
output [
    "Courier assignments: ", 
    show([i | i in courier, j in items where H[i,j] != j]), "\n",  
    
    "Maximum distance: ", show(obj), "\n",  
    
    "Distances each courier: ", 
    show([sum(j in dis where H[i,j] != j)(D[j,H[i,j]]) | i in courier]), "\n",

    "Loads each courier: ", 
    show([sum(j in items where H[i,j] != j)(s[j]) | i in courier]), "\n",  
    
    "H: \n",
    concat([
        show(H[i,j]) ++ (if j == n+1 then "\n" else " " endif) 
        | i in courier, j in dis
    ]),

    "Solution: [",
    concat([
        show([j | j in items where H[i,j] != j]) ++ (if i < m then ", " else "" endif)
        | i in courier
    ]),
    "]\n"
];