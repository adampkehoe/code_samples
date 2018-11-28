Data_original=xlsread('Data.xlsx');
%Finding the linear regression model
Y=Data_original(:,3);
N=length(Y);
X=[ones(N,1),[1:N]'];
beta=inv(X'*X)*(X'*Y);
b0=beta(1);
b1=beta(2);
Data_residual=(Y-(b0+b1*[1:N]'));
xtdot=Data_residual;
xtbar=mean(xtdot);
xt=xtdot-xtbar;
%Fit the residual of linear regression model with AR(2)
X=[xt(2:N-1,1),xt(1:N-2,1)];
Y=[xt(3:N,1)];
phi_hat=inv(X'*X)*(X'*Y);
phi1=phi_hat(1);
phi2=phi_hat(2);
% Calculate the residual of the AR(2) model
Residual_AR2=Y-phi1*X(:,1)-phi2*X(:,2);
plot(Residual_AR2);
%RSS of the AR(2)RSS_AR2=sum(Residual_AR2.^2);
%This is variance a_t^2
Var_AR2_at=1/(N-2-2)*RSS_AR2;