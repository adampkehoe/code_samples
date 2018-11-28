% F=Fredholm 
% u(x)=f(x)+int(K(x,z)u(z)dz,a,b)

n=8;
a=0; b=1;
h=(b-a)/(n-1);

%x and z assume the same values
%K will be generated such that
%the permutations of (x(j), z(k)) will be exhausted

x=(a:h:b)';
z=x;

%K and f are known functions.

K=@(x,z) exp(abs(x-z));
f=@(x) x.^2;

for j=1:n
   for k=1:n
       if j<=k
m(j,k)=2*K(x(j),z(k));
       end
       if j>=k
m(j,k)=2*K(x(j),z(k));        
       end
   end
end

% %manipulate indexing to 
% %specify which elements are 
% %multiplied by which coefficients

for j=1:n/2
    for k=1:n/2
m(j,k)=2*K(x(2*j),z(2*k));
    end
end
for j=1:n/2
    for k=1:n/2
m(j,k)=4*K(x(2*j-1),z(2*k-1));
    end
end

for j=1:n
    for k=1:n
m(j,1)=K(x(j),z(1));
m(j,n)=K(x(j),z(n));
    end
end

% %compute f at each point

fx=f(x);
I=eye(n);
L=I-(h/3)*m;
p=L\fx;

%Gauss w/ pivot
n=size(L,1);
for i=1:n
    %keeping the column constant for each iteration, this switches
    %elements among rows based on whether an element in
    %a lower row is larger than that of a higher row
    for j=i+1:n
            if abs(L(j,i))>abs(L(i,i))
                M=fx(i);
               fx(i)=fx(j);
               fx(j)=M;
               U=L(i,:);
               L(i,:)=L(j,:);
               L(j,:)=U;
              
            end
    end
    
    %ensuring our first element will equal 1 
    %and that fx(i) is also divided accordingly
    fx(i)=fx(i)/L(i,i);
    L(i,:)=L(i,:)/L(i,i);
    
    %subtract so that each subsequent element 
    %in the column will equal 0
    for j=i+1:n
        fx(j)=fx(j)-fx(i)*(L(j,i));
        L(j,:)=L(j,:)-L(i,:)*(L(j,i));     
    end
    
end

%if L(n,n)=0, the system does not have a unique solution
if L(n,n)==0
    disp('No solution');
    return
end

%matrix is now in row-echelon form
%so now continue with complete pivoting
%so that the solution=fx
for i=n:-1:1
    for j=i-1:-1:1
        fx(j)=fx(j)-fx(j+1)*L(j,i);
        L(j,:)=L(j,:)-L(j+1,:)*L(j,i);       
        for q=n:-1:1
            L1=L;
            L1(q,q)=0;
            B=L1(j,q);
            if B~=0
                fx(j)=fx(j)-L(j,q)*fx(q);
                L(j,q)=0; 
            end
        end
         end
    end

solution=fx;
