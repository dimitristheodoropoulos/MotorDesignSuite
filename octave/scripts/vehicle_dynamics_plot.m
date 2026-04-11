% Octave Vehicle Dynamics Plotting for PowertrainSimSuite Phase3

project_root = fileparts(mfilename('fullpath'));
results_dir = fullfile(project_root, '../../results/csv');
plots_dir   = fullfile(project_root, '../../results/plots');

if ~exist(results_dir, 'dir')
    error("Results directory not found: %s", results_dir);
end
if ~exist(plots_dir, 'dir'); mkdir(plots_dir); end

% --- Load simulation results ---
dyn_csv = fullfile(results_dir, 'vehicle_dynamics.csv');
if ~exist(dyn_csv, 'file')
    error("Vehicle dynamics results not found: %s", dyn_csv);
end

printf("Loading vehicle dynamics data from %s...\n", dyn_csv);

data = csvread(dyn_csv, 1, 0);  % skip header row
t = data(:,1);   % time [s]
x = data(:,2);   % position [m]
v = data(:,3);   % velocity [m/s]
a = data(:,4);   % acceleration [m/s^2]
F = data(:,5);   % force [N]

% --- Safe graphics toolkit ---
try
    graphics_toolkit("qt");
    printf("Using Qt toolkit.\n");
catch
    graphics_toolkit("gnuplot");
    printf("Qt not available. Using gnuplot headless.\n");
end

% --- Force headless fonts ---
set(0,'DefaultAxesFontName','Liberation Sans');
set(0,'DefaultTextFontName','Liberation Sans');
set(0,'DefaultFigureVisible','off');

% --- Plot velocity ---
figure;
plot(t, v, 'b-', 'LineWidth', 1.5);
title('Vehicle Velocity over Time');
xlabel('Time [s]'); ylabel('Velocity [m/s]');
grid on;
print('-dpng', fullfile(plots_dir, 'vehicle_velocity.png'));

% --- Plot acceleration ---
figure;
plot(t, a, 'r-', 'LineWidth', 1.5);
title('Vehicle Acceleration over Time');
xlabel('Time [s]'); ylabel('Acceleration [m/s^2]');
grid on;
print('-dpng', fullfile(plots_dir, 'vehicle_acceleration.png'));

% --- Plot force ---
figure;
plot(t, F, 'g-', 'LineWidth', 1.5);
title('Applied Force over Time');
xlabel('Time [s]'); ylabel('Force [N]');
grid on;
print('-dpng', fullfile(plots_dir, 'vehicle_force.png'));

% --- Plot trajectory ---
figure;
plot(t, x, 'm-', 'LineWidth', 1.5);
title('Vehicle Position over Time');
xlabel('Time [s]'); ylabel('Position [m]');
grid on;
print('-dpng', fullfile(plots_dir, 'vehicle_position.png'));

printf("✅ Vehicle dynamics plots saved in %s\n", plots_dir);
