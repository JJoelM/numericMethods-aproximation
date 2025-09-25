function metodo_iteracion()
    % Solicitar función al usuario
    f_str = input('Ingrese la función f(x) (use x como variable, ej: exp(-x)-x): ', 's');
    g_str = input('Ingrese la función g(x) para la iteración (x = g(x)): ', 's');

    % Vectorizar las funciones automáticamente
    f_str_vec = vectorize_function(f_str);
    g_str_vec = vectorize_function(g_str);

    % Convertir strings a funciones manejables
    f = str2func(['@(x) ' f_str_vec]);
    g = str2func(['@(x) ' g_str_vec]);

    % Parámetros iniciales
    x0 = input('Ingrese el valor inicial x0: ');
    tol = input('Ingrese la tolerancia (ej: 0.0001): ');
    max_iter = input('Ingrese el máximo número de iteraciones (ej: 50): ');
    aitken = input('¿Aplicar Aceleración de Aitken? (s/n): ', 's');

    % Inicializar variables
    iteraciones = 0;
    error = tol + 1;
    resultados = [];
    x_vals_iter = [x0]; % Almacenar todos los valores de x para la gráfica

    % Método de iteración
    if lower(aitken) == 's'
        % Con Aceleración de Aitken
        x_ant = x0;
        x_act = g(x_ant);
        x_sig = g(x_act);
        x_vals_iter = [x_vals_iter; x_act; x_sig];

        while error > tol && iteraciones < max_iter
            % Fórmula de Aitken
            if (x_sig - 2*x_act + x_ant) != 0
                x_aitken = x_act - (x_sig - x_act)^2 / (x_sig - 2*x_act + x_ant);
            else
                fprintf('División por cero en Aitken. Deteniendo iteración.\n');
                break;
            end

            error = abs(x_aitken - x_ant);
            iteraciones = iteraciones + 1;
            resultados = [resultados; iteraciones, x_aitken, error];

            % Actualizar valores para siguiente iteración
            x_ant = x_aitken;
            x_act = g(x_ant);
            x_sig = g(x_act);
            x_vals_iter = [x_vals_iter; x_aitken; x_act; x_sig];
        end
    else
        % Sin Aceleración de Aitken
        x_act = x0;

        while error > tol && iteraciones < max_iter
            x_sig = g(x_act);
            error = abs(x_sig - x_act);
            iteraciones = iteraciones + 1;
            resultados = [resultados; iteraciones, x_sig, error];
            x_vals_iter = [x_vals_iter; x_sig];
            x_act = x_sig;
        end
    end

    % Mostrar resultados en tabla
    if isempty(resultados)
        fprintf('\nNo se realizaron iteraciones. Verifique los parámetros.\n');
    else
        fprintf('\nIteración\tAproximación\t\tError\n');
        fprintf('--------------------------------------------\n');
        for i = 1:size(resultados, 1)
            fprintf('%d\t\t%.8f\t%.8f\n', resultados(i,1), resultados(i,2), resultados(i,3));
        end

        % Graficar CORRECTAMENTE el método de iteración
        x_min = min(x_vals_iter) - 0.5;
        x_max = max(x_vals_iter) + 0.5;
        x_vals = linspace(x_min, x_max, 1000);

        figure;

        % Graficar y = x (línea identidad)
        plot(x_vals, x_vals, 'k-', 'LineWidth', 2); hold on;

        % Graficar y = g(x)
        try
            y_vals_g = arrayfun(g, x_vals);
            plot(x_vals, y_vals_g, 'b-', 'LineWidth', 2);
        catch
            y_vals_g = zeros(size(x_vals));
            for i = 1:length(x_vals)
                try
                    y_vals_g(i) = g(x_vals(i));
                catch
                    y_vals_g(i) = NaN;
                end
            end
            plot(x_vals, y_vals_g, 'b-', 'LineWidth', 2);
        end

        % Graficar la iteración (escalera)
        if lower(aitken) == 's'
            % Para Aitken, graficar puntos principales
            plot(resultados(:,2), resultados(:,2), 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
            title('Método de Iteración con Aceleración de Aitken');
        else
            % Para iteración normal, graficar la escalera completa
            x_escalera = [];
            y_escalera = [];

            for i = 1:length(x_vals_iter)-1
                x_escalera = [x_escalera; x_vals_iter(i); x_vals_iter(i)];
                y_escalera = [y_escalera; x_vals_iter(i); x_vals_iter(i+1)];
            end

            plot(x_escalera, y_escalera, 'r-', 'LineWidth', 1);
            plot(x_vals_iter, x_vals_iter, 'ro', 'MarkerSize', 6, 'MarkerFaceColor', 'r');
            title('Método de Iteración de Punto Fijo');
        end

        % Graficar el punto inicial
        plot(x0, x0, 'go', 'MarkerSize', 8, 'MarkerFaceColor', 'g');

        % Líneas de referencia
        plot([x_min, x_max], [0, 0], 'k--', 'LineWidth', 0.5);
        plot([0, 0], [x_min, x_max], 'k--', 'LineWidth', 0.5);

        xlabel('x');
        ylabel('y');

        if lower(aitken) == 's'
            legend('y = x', 'y = g(x)', 'Aproximaciones Aitken', 'Punto inicial', 'Location', 'best');
        else
            legend('y = x', 'y = g(x)', 'Trayectoria iteración', 'Aproximaciones', 'Punto inicial', 'Location', 'best');
        end

        grid on;
        axis equal;

        % Mostrar raíz final
        fprintf('\nRaíz aproximada: %.8f\n', resultados(end,2));
        fprintf('Iteraciones totales: %d\n', iteraciones);
        fprintf('Error final: %.8f\n', resultados(end,3));
        fprintf('Verificación: f(raíz) = %.8f\n', f(resultados(end,2)));
    end
end

function f_vec = vectorize_function(f_str)
    % Función para vectorizar automáticamente operaciones
    f_vec = f_str;

    % Reemplazar operadores no vectorizados por vectorizados
    f_vec = strrep(f_vec, '*', '.*');
    f_vec = strrep(f_vec, '/', './');
    f_vec = strrep(f_vec, '^', '.^');
end
