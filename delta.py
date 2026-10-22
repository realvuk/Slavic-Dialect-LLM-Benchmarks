import json
import os
import pandas as pd

def calculate_dialect_gap(json_input, benchmark_name="COPA"):
    # Load data dynamically from file path, raw string, or list/dict
    if isinstance(json_input, str):
        if os.path.isfile(json_input):
            with open(json_input, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = json.loads(json_input)
    else:
        data = json_input

    df = pd.DataFrame(data)

    # 1. Map fine-grained language keys to standard categories
    lang_map = {
        # Standard Languages
        'sl': 'std_sl',
        'hr': 'std_hr',
        'mk': 'std_mk',
        'sr': 'std_sr', 'srp_cyrl': 'std_sr', 'srp_latn': 'std_sr',

        # Dialects
        'sl-cer': 'dial_cer',
        'sl-prl': 'dial_prl',
        'hr-ckm': 'dial_ckm',
        'sr-tor': 'dial_tor', 'tor_cyrl': 'dial_tor', 'tor_latn': 'dial_tor'
    }

    # Filter out excluded languages (en, bg, bs, etc.)
    df['Mapped_Lang'] = df['Language'].map(lang_map)
    df = df.dropna(subset=['Mapped_Lang'])

    # 2. Average script splits per model/language group (handles Serbian PIQA splits)
    aggregated = df.groupby(['Model', 'Mapped_Lang'])['Accuracy'].mean().reset_index()

    # 3. Categorize into Standard vs Dialect
    aggregated['Type'] = aggregated['Mapped_Lang'].apply(
        lambda x: 'Standard' if x.startswith('std_') else 'Dialect'
    )

    # 4. Compute overall Mean Standard, Mean Dialect, and Delta per Model
    metrics = aggregated.groupby(['Model', 'Type'])['Accuracy'].mean().unstack()

    metrics['Benchmark'] = benchmark_name
    metrics['Delta'] = (metrics['Standard'] - metrics['Dialect']).round(3)
    metrics['Mean_Standard'] = metrics['Standard'].round(4)
    metrics['Mean_Dialect'] = metrics['Dialect'].round(4)

    # Output formatted DataFrame
    result = metrics.reset_index()[['Model', 'Benchmark', 'Mean_Standard', 'Mean_Dialect', 'Delta']]
    return result

# Execution
piqa_file_path = "/Users/vuk/Documents_Local/GitHub/Slavic-Dialect LLM Benchmarks/just_viz/piqa_old.json"
# Calculate Delta for PIQA
df_piqa_delta = calculate_dialect_gap(piqa_file_path, benchmark_name="PIQA")

# Display results
print(df_piqa_delta.to_string(index=False))
