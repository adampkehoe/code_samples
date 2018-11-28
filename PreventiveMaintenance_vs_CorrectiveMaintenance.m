clear

%Preventive maintenance times to be tested
L = [1 5 10 15 20 25 30 35 40 45 50];
%Upper and lower limits of processing time uniform distribtuion
U = 15;
H = 10;

%Initialize actors, time horizon, steps, etc.
A = 1;
step = .01;
M = zeros(5,1);
MaxT = 20000;
Wstep = 50;
P = [0 .99 .98 .95 .9 .8 .7 .6 .5 .4 .3 .2 .1];
compare = length(P);
Q = size(P,2);
Ratios = zeros(compare,Q+1);
makespan = zeros(compare,Q+1);
completiontime = zeros(compare,Q+1);
A = ones(1,13);
q(1) = 0;
 
for i = 2:size(P,2)
    q(i) = 1;
while A(i) > P(i)
    A(i) = A(i) * q(i);
    q(i) = q(i) - step;
end
end

%generate jobs
for i = 1:5000
    s(i) = (U-H) * rand(1) + H;
end

%sort jobs
p = sort(s);
for i = 1:size(p,2)
    if mod(i,size(M,1)) ~= 0
    M(mod(i,size(M,1)),i) = p(i);
    else 
    M(size(M,1), i) = p(i);
    end
end
%copy M
N = M;
r = [];

%generate random numbers to be compared against to check if machine has
%failed based on failure probability
for j = 1:size(M,1)
for z = 1:MaxT/Wstep
    r(j,z) = rand(1);
end
end
E = zeros(10,1);
R = zeros(10,1);

%comparing different preventive maintenance times
for v = 1:compare
 
F = 1;
X = 1;
Opt(v) = 1 - ((U+H)/2 + L(v))/(3*(U+H)/2 + Wstep);
while X > Opt(v)
X = X * F;
F = F - step;
end
q(size(P,2) + 1) = F;
V(v) = F;
 
for k = 1:size(q,2)
R(v,k) = 0;
E(v,k) = 0;
W = 0;
a = 1;
D = [];
T = 0;
B = ones(5,1);
M = N;
z = 1;

%Simulation
while T < MaxT
    if T >= W
    [sel, n] = max(M~=0, [], 2);
    for j = 1:size(M,1)
        if B(j) < q(k) && B(j) ~= 0 && n(j) ~= 1
            B(j) = 1;
            M(j,n(j)) = M(j,n(j)) + L(v);
            R(v,k) = R(v,k) + 1;
        end
    end    
    for j = 1:size(M,1)
        if r(j,z) > B(j)
        B(j) = 0;
        E(v,k) = E(v,k) + 1;
        else
        B(j) = B(j) - step;
        end
end  
    z = z + 1;
    W = W + Wstep;
    end
    while T < W
       [sel, c] = max(M~=0, [], 2);
        for j = 1:size(M,1)
            Min(j) = M(j,c(j));
        if M(j,c(j)) <= 0
            Min(j) = 50 + j;
        end
        end
        [m I] = min(Min(Min>0));
        if min(Min) == 51
            finish = T;
            T = MaxT;
        else
        if sum(B) == 0
            T = W;
        else
        if B(I) == 0
        while B(I) == 0
            Min(I) = 50 + Min(I);
            [m I] = min(Min(Min>0));       
        end
        end
        if M(I,c(I)) <= 0
            T = W;
        else
        delta = M(I,c(I));
        if T + M(I,c(I)) <= W
            for j = 1:size(M,1)
                if B(j) ~= 0
                M(j,c(j)) = M(j,c(j)) - delta;          
                end
            end
            T = T + delta;   
            D(a) = T;
            a = a + 1;         
        else
            for j = 1:size(M,1)
                if B(j) ~= 0
                M(j,c(j)) = M(j,c(j)) - W + T;
                end
            end
            T = W;
        end
        end
        end
        end
    end
    for j = 1:size(M,1)
        if B(j) == 0 && c(j) ~= 1
           B(j) = 1;
           M(j,c(j)) = p(c(j));
        end
    end
end
 
YesP(k) = sum(D);
x(k) = D(a-1);
end
NoP = YesP(1);
Ratios = YesP/NoP;
makespan = x;
completiontime = YesP;
SumR(v,:) = Ratios;
SumM(v,:) = makespan;
SumC(v,:) = completiontime;
OptMakespan = sum(M(size(M,1),:));
end

