% helpers.m - common Octave functions for PowertrainSimSuite

function mean_val = safe_mean(array)
    % Returns mean, safely handling empty arrays
    if isempty(array)
        mean_val = NaN;
    else
        mean_val = mean(array);
    end
end

function save_plot(fig_handle, filepath)
    % Saves current figure to PNG
    print(fig_handle, '-dpng', filepath);
    printf("✅ Plot saved: %s\n", filepath);
end
