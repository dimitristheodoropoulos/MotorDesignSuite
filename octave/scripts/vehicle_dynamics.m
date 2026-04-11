% Vehicle Dynamics Simulation (longitudinal model)
printf('=== Running Vehicle Dynamics Simulation ===\n');

project_root      = fileparts(fileparts(fileparts(mfilename('fullpath'))));
results_csv_dir   = fullfile(project_root, 'results', 'csv');
results_plots_dir = fullfile(project_root, 'results', 'plots');

if ~exist(results_csv_dir,   'dir'); mkdir(results_csv_dir);   end
if ~exist(results_plots_dir, 'dir'); mkdir(results_plots_dir); end

% Parameters
m      = 1200;   % vehicle mass [kg]
F_trac = 4000;   % traction force [N]
F_res  = 300;    % resistive force [N]
dt     = 0.1;    % time step [s]
t_end  = 20;     % simulation time [s]

% Simulation
t = 0:dt:t_end;
v = zeros(size(t));
x = zeros(size(t));

for k = 2:length(t)
    a    = (F_trac - F_res) / m;
    v(k) = v(k-1) + a * dt;
    x(k) = x(k-1) + v(k-1) * dt + 0.5 * a * dt^2;
end

% Save CSV
csvwrite(fullfile(results_csv_dir, 'vehicle_dynamics.csv'), [t' v' x']);

% Plot
figure('Visible', 'off');
subplot(2,1,1);
plot(t, v, 'b-', 'LineWidth', 2);
xlabel('Time (s)'); ylabel('Velocity (m/s)');
title('Vehicle Velocity vs Time'); grid on;

subplot(2,1,2);
plot(t, x, 'r-', 'LineWidth', 2);
xlabel('Time (s)'); ylabel('Position (m)');
title('Vehicle Position vs Time'); grid on;

print('-dpng', fullfile(results_plots_dir, 'vehicle_dynamics.png'));
printf('✅ Vehicle dynamics simulation complete.\n');