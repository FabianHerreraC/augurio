# Augurio Colectivo

Ejercicio en vivo del taller **Cognición Aumentada · Universidad El Bosque**.
Web estática autocontenida (un solo `index.html`, sin build) conectada a tres flujos de n8n.

## Vistas

- `index.html` — página de participantes: presentación de Augurio, acceso a las preguntas y resultados (lectura colectiva con grafo y lectura individual).
- `index.html?vista=captura` — formulario de las tres preguntas.
- `index.html?fac=1` — lo mismo que la raíz más el panel de facilitador.
- `index.html?demo=1` — modo demo con datos de muestra, sin depender de n8n.

## Desarrollo local

```bash
python3 serve.py   # sirve en http://127.0.0.1:4321
```

El detalle de arquitectura, flujos de n8n y pendientes está en `spec_augurio.md`.
