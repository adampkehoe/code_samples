clear all
close all
clc

Data = xlsread('time_series_final.xlsx');
Q = Data(14:296,1);
X11 = Data(14:296,7);
X22 = Data(14:296,2);

mod=1:260; % will use 240 years for training
val=261:283; % will use 23 years for validation 
k=1:length(X11);
k=k';

%%%%%%%% Detrending data %%%%%%%%
%% Fitting a linear deterministic trend:
% energy production trend
line_X1=polyfit(k,X11,1);
linevals_X1=(line_X1(1)*k+line_X1(2));

% mean temperature trend
line_X2=polyfit(k,X22,1);
linevals_X2=(line_X2(1)*k+line_X2(2));

%% Extracting the residuals:
res_X1=X11-linevals_X1;

res_X2=X22-linevals_X2;
% X11 = X11(1:240);
% X22 = X22(1:240);
% X1 = iddata(X11);
% X2 = iddata(X22);
X1 = X11;
X2 = X22;
% X1 = res_X1;
% X2 = res_X2;
%%%%%%%% Fit ARMAV Model ---- PHI structure [phi_11,0;phi_21,phi,22]
%% Sunspots
%Fitting Independant series to the models of various orders to the mean sunspot residuals:
sys_X2=cell(25,1);
% note here that we are simply fitting arma model to the number of sunspots
for n=1:25;
    sys_X2{n}=armax(X2(mod),[n n-1]);
end

%Determining the AIC for each model:
maic_X2=zeros(25,1);
for n=1:25;
maic_X2(n)=aic(sys_X2{n});
end

%Localizing the least complex adequate model, based on AIC:
[AIC_opt_X2,n]=min(maic_X2);
sys_opt_X2=sys_X2{n};

%Printing selected model:
fprintf('Selected Model for Number of Sunspots is [%d,%d]',n,n-1)
present(sys_opt_X2)

%Confirming the adequacy of the model:
figure()
resid(sys_opt_X2,X2(mod))
title('Confirmation of Adequacy of Chosen Models for Number of Sunspots','fontsize',11,'fontweight','demi')

r2 = resid(sys_opt_X2,X2(mod));
residuals2=r2.y;
RSS2=sum(residuals2.^2);
[E2,R2] = resid(sys_opt_X2,X2(mod));
%Getting the Green's Function Co-efficients:
t=0:200; % I look at 200steps
G_X2=GreenFunction(sys_opt_X2,t(end));
figure()
plot(G_X2)
title('G.F.s for Number of Sunspots Model','fontsize',11,'fontweight','demi')

%% Tree Rings
%Fitting Independant series to the models of various orders to the mean tree ring residuals:
sys_X1=cell(25,1);
% note here that we are simply fitting arma model to the width of tree rings
for n=1:25;
sys_X1{n}=armax(X1(mod),[n n-1]);

end

%Determining the AIC for each model:
maic_X1=zeros(25,1);
for n=1:25;
    maic_X1(n)=aic(sys_X1{n});
end

%Localizing the least complex adequate model, based on AIC:
[AIC_opt_X1,n]=min(maic_X1);
sys_opt_X1=sys_X1{n};

%Printing selected model:
fprintf('Selected Model for tree ring width is [%d,%d]',n,n-1)
present(sys_opt_X1)

%Confirming the adequacy of the model:
figure()
resid(sys_opt_X1,X1(mod))
title('Confirmation of Adequacy of Chosen Models for Width of Tree Rings','fontsize',11,'fontweight','demi')
r1 = resid(sys_opt_X1,X1(mod));
residuals1=r1.y;
RSS1=sum(residuals1.^2);
[E1,R1] = resid(sys_opt_X1,X1(mod));
%Getting the Green's Function Co-efficients:
t=0:200; % I look at 200steps
G_X1=GreenFunction(sys_opt_X1,t(end));
figure()
plot(G_X1)
title('G.F.s for Width of Tree Rings Model','fontsize',11,'fontweight','demi')
%% Width of Tree Rings (mm) driven by Number of Sunspots and White Noise:
%Creating iddata for use in modelling:
data_X1_X2=iddata(X11,X22,1);

%Testing models of order (n,n,n-1) - (AR,Input,MA):
sys_X1_X2=cell(25,1);
for n=1:25;
    sys_X1_X2{n}=armax(data_X1_X2(mod),[n,n,n-1,0]); % use help armax to see the meaning of the parameters used
end

%Determining the AIC for each model:
maic_X1_X2=zeros(25,1);
for n=1:25;
    maic_X1_X2(n)=aic(sys_X1_X2{n});
end

%Localizing the least complex adequate, based on AIC:
[AIC_opt_X1_X2,n]=min(maic_X1_X2);
sys_opt_X1_X2=sys_X1_X2{n};

%Printing selected model:
fprintf('Selected Model for the Width of Tree Rings driven by the Number of Sunspots, based on AIC, is [%d,%d]',n,n-1)
present(sys_opt_X1_X2)

%Confirming the adequacy of the model:
figure()
resid(sys_opt_X1_X2,data_X1_X2(mod))
title('Confirmation of Adequacy of Chosen Models for Width of Tree Rings driven by the Number of Sunspots','fontsize',11,'fontweight','demi')
r12 = resid(sys_opt_X1_X2,data_X1_X2(mod));
residuals12=r12.y;
RSS12=sum(residuals12.^2);
[E12,R12] = resid(sys_opt_X1_X2,data_X1_X2(mod));
%Getting the Green's Function Co-efficients:
t=0:200;
% Get G22 values
G_X1_X2_22=GreenFunction(sys_opt_X1_X2,t(end));
 
%create a temp model to get other green's functions
%  sys_opt_X2.a = sys_opt_X1_X2.b;
%  sys_opt_X2.c = sys_opt_X1_X2.c;
% %Get G21 values
sys_temp.a = sys_opt_X1_X2.b;
sys_temp.c = sys_opt_X1_X2.c;
G_X1_X2_21=GreenFunction(sys_temp,t(end));
% %
%% Number of Sunspots driven by Width of Tree Rings (mm) and White Noise:
%Creating iddata for use in modelling:
data_X2_X1=iddata(X22,X11,1);

%Testing models of order (n,n,n-1) - (AR,Input,MA):
sys_X2_X1=cell(25,1);
for n=1:25;
    sys_X2_X1{n}=armax(data_X2_X1(mod),[n,n,n-1,0]); % use help armax to see the meaning of the parameters used
end

%Determining the AIC for each model:
maic_X2_X1=zeros(25,1);
for n=1:25;
    maic_X2_X1(n)=aic(sys_X2_X1{n});
end

%Localizing the least complex adequate, based on AIC:
[AIC_opt_X2_X1,n]=min(maic_X2_X1);
sys_opt_X2_X1=sys_X2_X1{n};

%Printing selected model:
fprintf('Selected Model for the Number of Sunspots driven by the Width of Tree Rings, based on AIC, is [%d,%d]',n,n-1)
present(sys_opt_X2_X1)

%Confirming the adequacy of the model:
figure()
subplot(2,1,1)
resid(sys_opt_X2_X1,data_X2_X1(mod))
title('Confirmation of Adequacy of Chosen Models for Number of Sunspots driven by Width of Tree Rings','fontsize',11,'fontweight','demi')
r21 = resid(sys_opt_X2_X1,data_X2_X1(mod));
residuals21=r21.y;
RSS21=sum(residuals21.^2);
[E21,R21] = resid(sys_opt_X2_X1,data_X2_X1(mod));
%Getting the Green's Function Co-efficients:
t=0:200;
% Get G22 values
G_X2_X1_22=GreenFunction(sys_opt_X2_X1,t(end));
% create a temp model to get other green's functions
sys_temp2.a = sys_opt_X2_X1.b;
sys_temp2.c = sys_opt_X2_X1.c;
% Get G21 values
G_X2_X1_21=GreenFunction(sys_temp2,t(end));


%% Prediction of values in validation set
% one step ahead prediction - should be easy enough to expand this for
% multiple steps ahead

% predict the temperature and then energy
for j = 1:23
    predicted_X2_res(j) = forecast(sys_opt_X2,X22(1:mod(end) + j - 1),1);
    % to predict the next energy, include the predicted temps as future
    % inputs
    predicted_X2(j) = predicted_X2_res(j);% + linevals_X2((mod(end)+j));
    predicted_X1_X2_res{j} = forecast(sys_opt_X1_X2,data_X1_X2(1:mod(end) + j - 1),1,predicted_X2_res(j));
    
    predicted_X1_res(j) = forecast(sys_opt_X1,X11(1:mod(end) + j - 1),1);
    % factor back trend
   
    %+ linevals_X2((mod(end)+j));
    predicted_X1_X2(j) = predicted_X1_X2_res{j}.y;% + linevals_X1((mod(end)+j));
    %+ linevals_X1((mod(end)+j));
    predicted_X1(j) = predicted_X1_res(j);% + linevals_X1((mod(end)+j));
    %+ linevals_X1((mod(end)+j));
    predicted_X2_X1_res{j} = forecast(sys_opt_X2_X1,data_X2_X1(1:mod(end) + j - 1),1,predicted_X1_res(j));
    predicted_X2_X1(j) = predicted_X2_X1_res{j}.y;% + linevals_X2((mod(end)+j));
end
for j = 1:23
    factor2(j) = (sum(G_X2(1:j).^2));
    factor1(j) = (sum(G_X1(1:j).^2));
    factor12(j) = (sum(G_X1_X2_22(1:j).^2));%+sum(G_X1_X2_21(1:j).^2);
    factor21(j) = (sum(G_X2_X1_22(1:j).^2));%+sum(G_X2_X1_21(1:j).^2);
end

% get the associated confidence interval - one sigma here, scale as desired
for j = 1:23
pred_ci_X2(j)=(RSS2/(length(residuals2)-1))*(factor2(j));
predicted_X2_ub(j)=predicted_X2(j)+1.96*sqrt(pred_ci_X2(j));
predicted_X2_lb(j)=predicted_X2(j)-1.96*sqrt(pred_ci_X2(j));
% remember to factor in two green's function contributions for the combined
% model
pred_ci_X1_X2(j)=(RSS12/(length(residuals12)-1))*factor12(j);
predicted_X1_X2_ub(j)=predicted_X1_X2(j)+1.96*sqrt(pred_ci_X1_X2(j));
predicted_X1_X2_lb(j)=predicted_X1_X2(j)-1.96*sqrt(pred_ci_X1_X2(j));

pred_ci_X1(j)=(RSS1/(length(residuals1)-1))*(factor1(j)); 
predicted_X1_ub(j)=predicted_X1(j)+1.96*sqrt(pred_ci_X1(j));
predicted_X1_lb(j)=predicted_X1(j)-1.96*sqrt(pred_ci_X1(j));

pred_ci_X2_X1(j)=(RSS21/(length(residuals21)-1))*factor21(j);
predicted_X2_X1_ub(j)=predicted_X2_X1(j)+1.96*sqrt(pred_ci_X2_X1(j));
predicted_X2_X1_lb(j)=predicted_X2_X1(j)-1.96*sqrt(pred_ci_X2_X1(j));
end

figure()
subplot(2,1,1)
plot(Q(261:283),X11(261:283),'k',Q(261:283),predicted_X1,'b',Q(261:283),predicted_X1_ub,'g',Q(261:283),predicted_X1_lb,'r')
title('23 year Forecast for Width of Tree Rings','fontsize',11,'fontweight','demi')
subplot(2,1,2)
plot(Q(261:283),X11(261:283),'k',Q(261:283),predicted_X1_X2,'b',Q(261:283),predicted_X1_X2_ub,'g',Q(261:283),predicted_X1_X2_lb,'r')
title('23 year Forecast for Width of Tree Rings driven by Number of Sunspots','fontsize',11,'fontweight','demi')
figure()
subplot(2,1,1)
plot(Q(261:283),X22(261:283),'k',Q(261:283),predicted_X2,'b',Q(261:283),predicted_X2_ub,'g',Q(261:283),predicted_X2_lb,'r')
title('23 year Forecast for Number of Sunspots','fontsize',11,'fontweight','demi')
subplot(2,1,2)
plot(Q(261:283),X22(261:283),'k',Q(261:283),predicted_X2_X1,'b',Q(261:283),predicted_X2_X1_ub,'g',Q(261:283),predicted_X2_X1_lb,'r')
title('23 year Forecast for Number of Sunspots driven by Width of Tree Rings','fontsize',11,'fontweight','demi')
%Sunspot(9,8) Tree(7,6) TreebySunspot(15,15,14)->(8,7) SunspotbyTree(7,7,6)
%->(5,4)
figure()
subplot(2,1,1)
plot(Q(1:283),X11)
title('Width of Tree Rings (cm)','fontsize',11,'fontweight','demi')
hold on
subplot(2,1,2)
plot(Q(1:283),X22)
title('Number of Sunspots','fontsize',11,'fontweight','demi')

roots1 = roots(sys_opt_X1.a);
roots2 = roots(sys_opt_X2.a);
roots12 = roots(sys_opt_X1_X2.a);
roots21 = roots(sys_opt_X2_X1.a);


