# Augurio Colectivo

Ejercicio en vivo del taller **Cognición Aumentada · Universidad El Bosque**.
Web estática autocontenida (un solo `index.html`, sin build) conectada a tres flujos de n8n.

## Vistas

- `index.html` — portada con dos accesos.
- `index.html?vista=captura` — formulario de las tres preguntas.
- `index.html?vista=revelacion` — lectura colectiva (con grafo de agrupamiento) y lectura personal.
- `index.html?vista=revelacion&demo=1` — modo demo con datos de muestra, sin depender de n8n.

## Desarrollo local

```bash
python3 serve.py   # sirve en http://127.0.0.1:4321
```

El detalle de arquitectura, flujos de n8n y pendientes está en `spec_augurio.md`.
