%Adam Kehoe
%General Relativity Take Home portion of Exam 1
%October 13, 2015

%equation for the trajectory of a person advancing toward a blackhole, w/ ri=rinitial/M and rf=rfinal/M%
f=@(r1,r2) 2.^(1/2)/3*((r1).^(3/2)-(r2).^(3/2));

%the following plots the trajectory of a person who proceeds toward the blackhole
%from an initial location in the rain frame

ri=10;
rf=0:.01:10;
plot (rf, f(ri,rf),'g');
hold on

%the following are equations for the paths of headlights taillights
%emitted as the person travels along his trajectory

%headlight
g=@(r1,r2) (r1-r2)-2*2.^(1/2)*(r1.^(1/2)-r2.^(1/2))+4*log((sqrt(2)+r1.^(1/2))/(sqrt(2)+r2.^(1/2)));
%taillight
h=@(r1,r2) -(r1-r2)-2*2.^(1/2)*(r1.^(1/2)-r2.^(1/2))+4*log((sqrt(2)-r2.^(1/2))/(sqrt(2)-r1.^(1/2)));

%the following are plots of the paths of the headlights and taillights as
%they are emitted at different initial r values, i.e., r1's

for r1=1:1:ri %telling the program to change the initial position by one for each iteration
    for r2=0:.01:r1; %traces the path of the headlight as it advances from its initial position to the center of the bh
w=g(r1,r2)+f(ri,r1); %the function must be shifted by an amount equal to the time value of the person of the frame at the particular point at which the light is emitted 
plot(r2,w,'b');
hold on
    end
    if r1>2 %traces the path of the taillight at an initial position greater than that of the event horizon
        for r2=r1:.01:15
q=h(r1,r2)+f(ri,r1);
plot(r2,q,'r');
hold on
        end
    else
    end
end
for r1=1:1:2 
    for r2=0:.01:r1 %traces the path of the taillight within the event horizon
q=h(r1,r2)+f(ri,r1);
plot(r2,q,'r');
hold on
    end
end
for r1=1.99 %because the function is undefined at r1=2 (since ln(0) is undefined), I set r1=1.99 to show that 
            %the path of the taillight emitted within the event horizon
            %proceeds toward the black holes
    for r2=0:.01:r1
q=h(r1,r2)+f(ri,r1);
plot(r2,q,'r');
hold on
    end
end      
    
%the plot is attached, the green line is the path of the person, the blue
%lines are different paths for the headlights emitted along the way, and
%the red lines are different paths for the taillights emitted along the way

%I set my y-axis to be scaled to 35 as its maximum value to show that the
%taillight emitted near the event horizon does indeed go toward the center
%of the black hole