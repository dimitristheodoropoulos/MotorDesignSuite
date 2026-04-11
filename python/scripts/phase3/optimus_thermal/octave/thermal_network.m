% thermal_network.m
% LPTN (Lumped Parameter Thermal Network) for motor nodes
% Nodes: Winding, Stator, Rotor, Housing, Coolant, Ambient
clear; clc;
nodes = {'Winding', 'Stator', 'Rotor', 'Housing', 'Coolant', 'Ambient'};
N = length(nodes);
% Thermal resistances [K/W]
R = [0, 0.05, 0.08, 0, 0, 0;
0.05, 0, 0.04, 0.06, 0, 0;
0.08, 0.04, 0, 0, 0.07, 0;
0, 0.06, 0, 0, 0.03, 0.10;
0, 0, 0.07, 0.03, 0, 0.05;
0, 0, 0, 0.10, 0.05, 0];
% Thermal capacitances [J/K]
C = [0.5; 2.0; 1.5; 3.0; 4.0; 1e6];
% Heat generation per node [W]
Q = [80.0; 30.0; 20.0; 5.0; 0.0; 0.0];
% Ambient temperature [C]
T_ambient = 25.0;
% Build conductance matrix
G = zeros(N, N);
for i = 1:N
for j = 1:N
if i ~= j && R(i,j) > 0
g = 1.0 / R(i,j);
G(i,j) = G(i,j) - g;
G(i,i) = G(i,i) + g;
end
end
end
% Transient simulation (Euler forward)
dt = 0.5;
t_end = 300.0;
steps = int32(t_end / dt);
T = ones(N, 1) * T_ambient;
T(N) = T_ambient;
history = zeros(steps, N);
for k = 1:steps
dT = (Q - G * T) ./ C;
dT(N) = 0.0; % ambient fixed
T = T + dt * dT;
history(k, :) = T';
end
time = linspace(0, t_end, steps);
% Save CSV
results_dir = fullfile(fileparts(fileparts(fileparts(mfilename('fullpath')))), ...
'results', 'optimus_thermal');
if ~exist(results_dir, 'dir')
mkdir(results_dir);
end
data = [time', history];
csvwrite(fullfile(results_dir, 'thermal_network_transient.csv'), data);
fprintf('âœ... Transient results saved\n');
% Plot transient
figure('Visible','off');
hold on;
colors_list = {'r','b','m','g','c','k'};
for i = 1:N-1
plot(time, history(:,i), 'Color', colors_list{i}, 'LineWidth', 2, ...
'DisplayName', nodes{i});
end
yline(T_ambient, '--k', 'Ambient');
xlabel('Time [s]');
ylabel('Temperature [Â°C]');
title('LPTN Transient Thermal Response');
legend('show');
grid on;
print('-dpng', fullfile(results_dir, 'thermal_network_transient.png'));
fprintf('âœ... Transient plot saved\n');
% Plot steady-state bar chart
steady = history(end, :);
figure('Visible','off');
bar(steady);
set(gca, 'XTickLabel', nodes);ylabel('Temperature [Â°C]');
title('LPTN Steady-State Temperatures');
grid on;
print('-dpng', fullfile(results_dir, 'thermal_network_steady_state.png'));
fprintf('âœ... Steady-state plot saved\n');
% Print steady-state summary
fprintf('\nSteady-State Temperatures:\n');
for i = 1:N
fprintf(' %-10s: %.1f Â°C\n', nodes{i}, steady(i));
end