include "globals.mzn";
include "lex_lesseq.mzn";

% Input Parameters
int: m;
set of int: courier = 1..m;
array[courier] of int: l;

int: n;
set of int: items = 1..n;
array[items] of int: s;

set of int: dis = 1..n+1;
array[dis, dis] of int: D;

% Decision Variables
array[courier, dis] of var dis: H;
int: max_load = max(l) + 1;
array[items] of int: max_dis = sort([max(j in items)(D[i,j]) | i in items]);
array[courier] of var 0..max_load: couriers_loads;
array[courier] of var 0..sum(D): total_distance;

% Constraints
constraint 
    forall(i in courier) (
        sum(j in items where H[i,j] != j)(s[j]) <= l[i]
    );  % Ensure total item size assigned to a courier does not exceed its capacity

constraint 
    forall(i in courier) (
        H[i, n+1] != n+1
    );  % Ensure couriers do not return to the depot

constraint 
    forall(j in items) (
        sum(i in courier)(H[i, j] != j) = 1
    );  % Ensure each item is assigned to exactly one courier

constraint forall(k in courier) (
    subcircuit([H[k, i] | i in dis]) 
);  % Ensure valid routes for each courier (subcircuit constraint)

constraint forall(k in 1..m-1) (
    couriers_loads[k] >= couriers_loads[k+1]
);  % Ensure non-increasing load distribution among couriers

constraint forall(c in courier) (
    total_distance[c] = sum(i in dis where H[c, i] != i) (D[i, H[c, i]])
);  % Calculate total distance traveled by each courier

% Bounds for Objective
int: lowbound = max(i in items)(D[n+1,i] + D[i,n+1]);
int: upbound = sum(i in items)(max(j in dis)(D[i, j])) * m;
var lowbound..upbound: obj;

% Objective
constraint obj = max(c in courier) (total_distance[c]);  

% Solve and Output
solve :: restart_luby(200)
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