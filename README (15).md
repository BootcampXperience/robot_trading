# SmartEnergyForecasting
## 📊 Pronóstico de Demanda Eléctrica con Skforecast

Este proyecto implementa un flujo completo de **forecasting de series temporales** para la demanda eléctrica en Perú, utilizando la librería [**skforecast**](https://skforecast.org/). El objetivo es comparar un modelo **univariado** (solo lags de la serie) contra un modelo **multivariado** (lags + variables exógenas de calendario).

## 🚀 Flujo del proyecto

1. **Carga y preparación de datos**

   * Lectura desde Excel (`pandas`).
   * Conversión a `datetime` y fijar frecuencia de 30 minutos.

2. **Análisis exploratorio**

   * Visualización de la serie.
   * Medias móviles (24h, 7d) para identificar tendencias y estacionalidad.

3. **Ingeniería de características**

   * Ciclo intradía (0–1).
   * Variables dummy para día de la semana.
   * Indicador de feriados (librería `holidays`).

4. **Partición de datos**

   * Última semana reservada como conjunto de prueba.

5. **Modelado con Skforecast**

   * **Univariado:** lags de la serie + XGBoost.
   * **Multivariado:** lags + exógenas.
   * Validación temporal con `TimeSeriesFold`.
   * Optimización de hiperparámetros con `grid_search_forecaster`.

6. **Evaluación**

   * Predicciones sobre la última semana.
   * Gráficos comparativos (train, test, predicciones).
   * Métricas: **MSE** y **MAE**.

## 📌 Requisitos

* Python 3.9+
* Librerías: `pandas`, `numpy`, `matplotlib`, `seaborn`, `skforecast`, `xgboost`, `lightgbm`, `scikit-learn`, `holidays`.

## ▶️ Uso

1. Instalar dependencias:

   ```bash
   pip install -q skforecast xgboost lightgbm scikit-learn pandas matplotlib seaborn holidays
   ```
2. Ejecutar el script paso a paso (o el notebook).
3. Revisar los gráficos y métricas para comparar modelos.

## 📈 Resultados esperados

* El modelo **univariado** captura la inercia de la serie.
* El modelo **multivariado** mejora la predicción al incorporar información de calendario y feriados.
