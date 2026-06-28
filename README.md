# Monitor de Calidad del Aire

Dashboard interactivo desarrollado con Dash + Plotly que visualiza datos reales de calidad del aire (SINCA) para la estación Los Andes, Región de Aysén. Muestra Temperatura, MP2.5, Humedad y Velocidad del Viento en el período 2015 – 2026.

## Requisitos

- Python 3.8 o superior
- pip

## Instalación y ejecución

1.  **Clonar el repositorio**

    ```bash
    git clone https://github.com/martinabarca-chl/monitor_air_quality.git
    cd monitor_air_quality
    ```

2.  **Crear y activar un entorno virtual**

    ```bash
    python -m venv venv
    ```

    - **Windows:**

      ```bash
      venv\Scripts\activate
      ```

    - **macOS / Linux:**

      ```bash
      source venv/bin/activate
      ```

3.  **Instalar dependencias**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación**

    ```bash
    python app.py
    ```

5.  **Abrir en el navegador**

    ```
    http://127.0.0.1:8050
    ```

## Estructura del proyecto

```
app.py          → Punto de entrada (layout + servidor)
config.py       → Colores, estilos, constantes
components.py   → Componentes UI reutilizables (KPIs, cajas)
charts.py       → Constructores de gráficos Plotly
tabs.py         → Contenido de las pestañas (datos + layouts)
callbacks.py    → Lógica de interacción (callbacks Dash)
data/           → Carga y limpieza de datos CSV
assets/         → CSS e imágenes
requirements.txt → Dependencias del proyecto
README.md       → Documentación
```

## Datos

Fuente: Sistema de Información Nacional de Calidad del Aire (SINCA)

[https://sinca.mma.gob.cl](https://sinca.mma.gob.cl)
