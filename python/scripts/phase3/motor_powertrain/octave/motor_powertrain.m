% Headless Octave demo for motor analysis
graphics_toolkit('gnuplot');        % headless plotting
set(0, 'defaultfigurevisible', 'off');  % no GUI window

theta = linspace(0, 2*pi, 100);
torque = sin(5*theta) + 0.1*randn(size(theta));

% Directories
results_dir = "../../phase3_results";
csv_dir     = [results_dir "/csv"];
plots_dir   = [results_dir "/plots"];

% Create directories if not existing
if ~exist(csv_dir, "dir")
    mkdir(csv_dir);
end
if ~exist(plots_dir, "dir")
    mkdir(plots_dir);
end

% Save CSV
csvwrite([csv_dir "/motor_torque.csv"], [theta' torque']);

% Plot headless
h = figure;
plot(theta, torque);
xlabel('Theta [rad]');
ylabel('Torque [Nm]');
title('Motor Torque Demo');
print(h, [plots_dir "/motor_torque.png"], '-dpng');
close(h);

disp("✅ Motor torque CSV and plot saved in phase3_results");
