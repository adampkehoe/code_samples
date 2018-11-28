%Systems Modeling Assignment 5 - test of sigmoid-like function for different growth parameters
%representing different effective marketing schemes
%B&W TV, Color TV, AC, Clothes Dryers, Water Softeners, 
%Record Players, Motels, Cell Phones, McDonald's, Steam Irons
%Avg .03 for p and .38 for q

for k = 1:11
fp = [0 .1 .2 .3 .4 .5 .6 .7 .8 .9 1];
fq = 1 - fp;

avgp = .03;
avgq = .38;
p0 = [.028 .005 .01 .017 .018 .025 .007 .004 .018 .029];
q0 = [.25 .84 .42 .36 .30 .65 .36 1.78 .54 .33];
m = 80000000;

Pmax = 10;
P = [1 2 3 4 5 6 7 8 9 10];
PDist = Pmax - P;

a = avgp;
c = avgq;
b = .1;
d = 1;

p = @(a,b,fp,PDist) a - b*log(1-fp*PDist/Pmax);
q = @(c,d,fq,PDist) c - d*log(1-fq*PDist/Pmax);

figure(k)

for i = 1:10
N = @(t) P(i)*m*(1-exp(-(p(a,b,fp(k),PDist(i))+q(c,d,fq(k),PDist(i)))*t))/(1+q(c,d,fq(k),PDist(i))/p(a,b,fp(k),PDist(i))*exp(-(p(a,b,fp(k),PDist(i))+q(c,d,fq(k),PDist(i)))*t));
n = @(t) P(i)*m*p(a,b,fp(k),PDist(i))*(p(a,b,fp(k),PDist(i))+q(c,d,fq(k),PDist(i)))^2*exp(-(p(a,b,fp(k),PDist(i))+q(c,d,fq(k),PDist(i)))*t)/(p(a,b,fp(k),PDist(i))+q(c,d,fq(k),PDist(i))*exp(-(p(a,b,fp(k),PDist(i))+q(c,d,fq(k),PDist(i)))*t))^2;
fplot (n,[0 10])
hold on
legend ('P = 1','P = 2','P = 3','P = 4','P = 5','P = 6','P = 7','P = 8','P = 9','P = 10 = Pmax','Location','southeast')
%legend ('Profit from P = 1','Profit from P = 2','Profit from P = 3','Profit from P = 4','Profit from P = 5','Profit from P = 6','Profit from P = 7','Profit from P = 8','Profit from P = 9','Profit from P = 10','Location','southeast')
title (['Variable Profit over time for fp = ' num2str(fp(k)) ' '])
end
end





