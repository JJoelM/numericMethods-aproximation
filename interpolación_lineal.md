# interpolacion_lineal.md

```markdown
# Método de Interpolación Lineal para Aproximación de Raíces

El método de **Interpolación Lineal** (también conocido como método de la **regla falsa**) es un procedimiento numérico para aproximar raíces de una función continua `f(x)` en un intervalo `[a, b]`.

## Principio

Si `f(a)` y `f(b)` tienen signos opuestos, según el **Teorema del Valor Intermedio**, existe al menos una raíz en `(a, b)`. La idea es aproximar la función por una línea recta que conecta los puntos `(a, f(a))` y `(b, f(b))` y tomar el punto donde esta línea cruza el eje x como la nueva aproximación `xr`.

### Fórmula de Interpolación Lineal

\[
x_r = b - f(b) \frac{a - b}{f(a) - f(b)}
\]

- `a`, `b`: extremos del intervalo actual
- `f(a)`, `f(b)`: valores de la función en los extremos
- `xr`: nueva aproximación a la raíz

---

## Procedimiento

1. Evaluar `f(a)` y `f(b)`.
2. Calcular `xr` usando la fórmula.
3. Evaluar `f(xr)`.
4. Determinar el subintervalo que contiene la raíz:
   - Si `f(a) * f(xr) < 0`, la raíz está en `[a, xr]` → actualizar `b = xr`
   - Si `f(xr) * f(b) < 0`, la raíz está en `[xr, b]` → actualizar `a = xr`
5. Repetir hasta que se cumpla el criterio de convergencia:
   - Tolerancia en `xr` (`|xr - xr_prev| < tol`)
   - Número máximo de iteraciones

---

## Ventajas

- Más rápido que el **método de bisección** en muchos casos.
- Garantiza convergencia si la función es continua y `f(a)` y `f(b)` tienen signos opuestos.

## Limitaciones

- Si `f(a)` y `f(b)` son muy cercanos, puede haber división por cero.
- No garantiza convergencia si la función no es aproximadamente lineal en el intervalo.
- Puede converger lentamente para funciones muy curvas.
