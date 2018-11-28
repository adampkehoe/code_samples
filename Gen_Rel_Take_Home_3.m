#Calculating critical viewing angles

for r0=2.25
for n=1:559 %calculating as if n=1000(i.e., time-step =1/1000 of 90 degrees), but once n>559, theta>50.33 degrees which is the critical angle for r0=2.25 at which the observer sees only the edge of the black hole.
theta(1)=0; %initial viewing angle
b(1)=.000001; %initial impact parameter (using b~0)
theta(n+1)=n*(pi/2)/1000; %incremental viewing angles
b(n+1)=r0*sin(theta(n+1))/((1-2/r0).^(1/2)); %value for b at particular viewing angle
for s=1:300 %this for loop approximates the integral solution for the angle phi (angle at which to look for star in the absence of the black hole) for each respective impact parameter/initial viewing angle
u(1)=0; 
u(s+1)=s*(1/r0)/300; %u goes from 0 to M/r0
d(s)=(u(s+1)-u(s))/2*(((1/((1/b(n)).^2-(u(s+1)).^2+2*(u(s+1)).^3).^(1/2)))+((1/((1/b(n)).^2-(u(s)).^2+2*(u(s)).^3).^(1/2)))); %simple midpt approximation for integral
ang(1)=0;
ang(s+1)=ang(s)+d(s); %incrementally produces the integral from 0 to M/r0 by adding integral from 0 to M/300r0 to integral from 0 to 2M/300r0, and so on, basic recursive integrating method
y(n+1)=ang(s+1); %ang(300) will be the phi value for a respective theta/impact parameter
end
h(1)=0;
h(n+1)=theta(n+1)*360/(2*pi); %changes initial viewing angle from radians to degrees
t(1)=0;
t(n+1)=y(n+1)*360/(2*pi); %changes respective phi value from radians to degrees
plot (h(n), t(n))
hold on
end
end

