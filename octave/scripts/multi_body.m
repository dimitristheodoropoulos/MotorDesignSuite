% Simple multi-body kinematic chain
clear; clc;

t = linspace(0, 10, 200);
theta1 = sin(t);   % άρθρωση 1
theta2 = cos(t);   % άρθρωση 2
theta3 = 0.5*sin(2*t); % άρθρωση 3

% Αποθήκευση αποτελεσμάτων
data = [t' theta1' theta2' theta3'];
csvwrite('results/csv/multi_body.csv', data);

% Γράφημα
figure;
plot(t, theta1, 'r-', t, theta2, 'g-', t, theta3, 'b-');
xlabel('Time [s]'); ylabel('Joint angle [rad]');
legend('Joint1','Joint2','Joint3');
title('Kinematic chain joint angles');
grid on;
print -dpng 'results/plots/multi_body.png';
