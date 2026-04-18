import json

# Leer notebook original
with open('notebooks/eda_regresion.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Modificar celda 0 (carga de datos)
cell0 = nb['cells'][0]
source_lines = cell0['source']
new_source = []
for line in source_lines:
    if 'SELECT * FROM jugadores' in line:
        line = line.replace('SELECT * FROM jugadores', 'SELECT * FROM jugadores_promediados')
    new_source.append(line)
cell0['source'] = new_source

# Insertar nueva celda después de la celda 0: transformación logarítmica y análisis
new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "log_transform_cell",
    "metadata": {},
    "outputs": [],
    "source": [
        "# Transformación logarítmica del target (para reducir asimetría)\n",
        "df['log_valor_mercado'] = np.log1p(df['valor_mercado_eur_TARGET'])\n",
        "\n",
        "# Visualizar distribuciones\n",
        "fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n",
        "axes[0].hist(df['valor_mercado_eur_TARGET'], bins=50, edgecolor='black', alpha=0.7)\n",
        "axes[0].set_title('Distribución original del valor de mercado')\n",
        "axes[0].set_xlabel('Valor (€)')\n",
        "axes[0].set_ylabel('Frecuencia')\n",
        "\n",
        "axes[1].hist(df['log_valor_mercado'], bins=50, edgecolor='black', alpha=0.7, color='orange')\n",
        "axes[1].set_title('Distribución log-transformada (log1p)')\n",
        "axes[1].set_xlabel('log(1 + Valor)')\n",
        "axes[1].set_ylabel('Frecuencia')\n",
        "\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "print(\"Asimetría (skewness) original:\", df['valor_mercado_eur_TARGET'].skew())\n",
        "print(\"Asimetría después de log1p:\", df['log_valor_mercado'].skew())\n",
        "\n",
        "# Nota: Para modelado, usar 'log_valor_mercado' como target. Después aplicar expm1 para volver a euros.\n"
    ]
}

nb['cells'].insert(1, new_cell)

# Guardar nuevo notebook
with open('notebooks/eda_regresion_promediados.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook 'eda_regresion_promediados.ipynb' creado exitosamente.")