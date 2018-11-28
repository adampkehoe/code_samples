#Calculates trajectory of light in proximity to a black hole and critical angles

r0=10; %initial radial distance
ang=[120 130 140 150 152.5]'; %initial launch angles
theta=(ang*2*pi/360); %converting initial launch angles into radians
c=@(s)theta(s); %setting up a function to call theta
dt=.01; %arbitrary time step that preserves that gives an approximation for the actual solution
f= @(r,b) -((1-2/r).^2-((1-2/r).^3)*b.^2/r.^2).^(1/2); %formula for dr
g= @(r,b) (b/r.^2*(1-2/r)); %formula for dphi

for s=1:1:5; %for loop to cycle through values of the impact parameter
    b(s)=r0*sin(c(s))/((1-2/r0).^(1/2)); %formula for impact parameter
for n=1:5000 %holding the impact parameter constant, plots the trajectory of the function
    r(1)=10;%initial position
    A(1)=0;%initial angle
    
    if isreal(f(r(n),b(s))) %conditional loop to test if dr is real
     F(n)=dt*f(r(n),b(s)); %approximation for dr at a particular r value
     G(n)=dt*g(r(n),b(s)); %approximation for dphi
    else %if dr is not real, change the sign for dr since the radial distance is now growing
     F(n)=-dt*f(r(n),b(s));
     G(n)=dt*g(r(n),b(s));
    end
    
    v(n)=((F(n)/dt).^2+(r(n)*G(n)/dt).^2)^(1/2); %instantaneous velocity of light at any given point
    x(n)=r(n)*cos(A(n));%position of the light in cartesian coordinates
    y(n)=r(n)*sin(A(n));
    plot(x(n),y(n));
    hold on
    
    A(n+1)=A(n)+G(n);%recursive formula that takes the initial angle A(1) and adding all preceding dphis to get the next angle
    r(n+1)=r(n)+(F(n));%same story for the radius
    
end    
V(s)=min(abs(v));%finds the minimum speed for a particular trajectory
end

