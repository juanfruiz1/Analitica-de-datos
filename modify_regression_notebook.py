#!/usr/bin/env python3
import json
import sys

# Load the notebook
with open('notebooks/eda_regresion.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the index of the cell that loads data (cell with SELECT * FROM jugadores)
load_data_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'SELECT * FROM jugadores' in source:
            load_data_idx = i
            break

if load_data_idx is None:
    print("Error: Could not find data loading cell")
    sys.exit(1)

# Create new cell for log transformation and visualization
log_transform_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "log_transform",
    "metadata": {},
    "outputs": [],
    "source": [
        "# ================================================\n",
        "# TRANSFORMACIÓN LOGARÍTMICA DEL TARGET\n",
        "# ================================================\n",
        "# El valor de mercado tiene una distribución extremadamente asimétrica.\n",
        "# Aplicamos log1p para reducir la asimetría y mejorar el rendimiento del modelo.\n",
        "\n",
        "df['log_valor_mercado'] = np.log1p(df['valor_mercado_eur_TARGET'])\n",
        "\n",
        "# Visualizar distribuciones\n",
        "fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n",
        "\n",
        "# Distribución original\n",
        "axes[0].hist(df['valor_mercado_eur_TARGET'], bins=50, edgecolor='black', alpha=0.7)\n",
        "axes[0].set_title('Distribución original del valor de mercado')\n",
        "axes[0].set_xlabel('Valor (€)')\n",
        "axes[0].set_ylabel('Frecuencia')\n",
        "\n",
        "# Distribución log-transformada\n",
        "axes[1].hist(df['log_valor_mercado'], bins=50, edgecolor='black', alpha=0.7, color='orange')\n",
        "axes[1].set_title('Distribución log-transformada (log1p)')\n",
        "axes[1].set_xlabel('log(1 + Valor)')\n",
        "axes[1].set_ylabel('Frecuencia')\n",
        "\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "# Medir asimetría\n",
        "print(\"Asimetría (skewness) original:\", df['valor_mercado_eur_TARGET'].skew())\n",
        "print(\"Asimetría después de log1p:\", df['log_valor_mercado'].skew())\n",
        "\n",
        "# NOTA IMPORTANTE:\n",
        "# Para el modelado, usaremos 'log_valor_mercado' como variable objetivo.\n",
        "# Las predicciones estarán en escala logarítmica.\n",
        "# Para convertir predicciones a euros: np.expm1(prediccion_log)\n"
    ]
}

# Insert after the data loading cell
nb['cells'].insert(load_data_idx + 1, log_transform_cell)

# Find cell that does train_test_split (search for 'train_test_split' or 'test_size')
split_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'train_test_split' in source or 'test_size' in source:
            split_idx = i
            break

if split_idx is not None:
    # Replace with GroupShuffleSplit to avoid data leakage
    old_cell = nb['cells'][split_idx]
    old_source = ''.join(old_cell['source'])
    
    # Check if it's a simple train_test_split
    if 'from sklearn.model_selection import train_test_split' in old_source:
        # Keep the import but add GroupShuffleSplit
        new_source = old_source.replace(
            'from sklearn.model_selection import train_test_split',
            'from sklearn.model_selection import train_test_split, GroupShuffleSplit'
        )
    else:
        # Add import if not present
        new_source = 'from sklearn.model_selection import GroupShuffleSplit\n' + old_source
    
    # Replace the split logic (we'll need to see the exact code, but let's assume)
    # This is a bit tricky without knowing the exact code. Instead, we'll add a new cell
    # after the split cell with the GroupShuffleSplit approach.
    # We'll create a new cell that overrides the split.
    
    # Create a new cell for GroupShuffleSplit
    group_split_cell = {
        "cell_type": "code",
        "execution_count": None,
        "id": "group_shuffle_split",
        "metadata": {},
        "outputs": [],
        "source": [
            "# ================================================\n",
            "# EVITAR DATA LEAKAGE: GroupShuffleSplit\n",
            "# ================================================\n",
            "# Los jugadores aparecen múltiples veces (años diferentes).\n",
            "# Para evitar que un mismo jugador aparezca en train y test,\n",
            "# usamos GroupShuffleSplit agrupando por player_id.\n",
            "\n",
            "# Asegurarse de tener definidas X y y (features y target log-transformado)\n",
            "# X = df.drop(columns=['valor_mercado_eur_TARGET', 'log_valor_mercado', 'id_observacion', 'player_id', 'fecha_valoracion'])\n",
            "# y = df['log_valor_mercado']  # Target log-transformado\n",
            "\n",
            "from sklearn.model_selection import GroupShuffleSplit\n",
            "\n",
            "# Crear splitter que mantiene jugadores separados\n",
            "gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)\n",
            "\n",
            "# Obtener índices de train y test\n",
            "train_idx, test_idx = next(gss.split(X, y, groups=df['player_id']))\n",
            "\n",
            "# Crear conjuntos\n",
            "X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]\n",
            "y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]\n",
            "\n",
            "print(f\"Train: {X_train.shape}, Test: {X_test.shape}\")\n",
            "print(f\"Jugadores únicos en train: {df['player_id'].iloc[train_idx].nunique()}\")\n",
            "print(f\"Jugadores únicos en test: {df['player_id'].iloc[test_idx].nunique()}\")\n",
            "\n",
            "# NOTA: Comentar o eliminar el train_test_split anterior si existe.\n"
        ]
    }
    
    # Insert after the split cell
    nb['cells'].insert(split_idx + 1, group_split_cell)

# Save the modified notebook
with open('notebooks/eda_regresion_modified.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Modified notebook saved as 'eda_regresion_modified.ipynb'")

# Also create a notebook for averaged data
# We'll create a copy of the modified notebook but change the data source
with open('notebooks/eda_regresion_modified.ipynb', 'r', encoding='utf-8') as f:
    nb_prom = json.load(f)

# Change the data loading query
for i, cell in enumerate(nb_prom['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'SELECT * FROM jugadores' in source:
            cell['source'] = [line.replace('SELECT * FROM jugadores', 'SELECT * FROM jugadores_promediados') for line in cell['source']]
            # Also update the comment
            for j, line in enumerate(cell['source']):
                if 'jugadores' in line and '#' in line:
                    cell['source'][j] = line.replace('jugadores', 'jugadores_promediados (datos promediados por jugador)')
            break

# Update title cell if exists
for i, cell in enumerate(nb_prom['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])
        if 'Regresión' in source:
            cell['source'] = ['# EDA Regresión - Datos Promediados (jugadores_promediados)\n\n',
                             'Este notebook utiliza la tabla `jugadores_promediados` donde cada jugador aparece una sola vez con estadísticas promediadas a lo largo de su carrera.\n']
            break

# Save the averaged notebook
with open('notebooks/eda_regresion_promediados.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb_prom, f, indent=1)

print("Averaged notebook saved as 'eda_regresion_promediados.ipynb'")