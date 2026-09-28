import os
import csv
import statistics

from utils.llm import ask_llm


def data_analytics_agent(
    query: str,
    file_path: str = None
) -> str:

    # ==========================================
    # 1. CHECK FILE
    # ==========================================

    if not file_path:
        return (
            "Please upload a CSV file so I can "
            "perform data analysis."
        )

    if not os.path.exists(file_path):
        return (
            f"I could not find the uploaded file: {file_path}"
        )

    # ==========================================
    # 2. CHECK FILE FORMAT
    # ==========================================

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension != ".csv":
        return (
            "Currently, the Data Analytics Agent supports "
            "CSV files. Please upload a CSV file."
        )

    # ==========================================
    # 3. READ CSV
    # ==========================================

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            rows = list(reader)
            columns = reader.fieldnames

    except Exception as e:

        return (
            f"I could not read the CSV file. "
            f"Error: {str(e)}"
        )

    # ==========================================
    # 4. CHECK DATA
    # ==========================================

    if not columns:
        return "The CSV file does not contain any columns."

    if not rows:
        return "The CSV file does not contain any data."

    # ==========================================
    # 5. BASIC DATA INFORMATION
    # ==========================================

    number_of_rows = len(rows)
    number_of_columns = len(columns)

    # ==========================================
    # 6. MISSING VALUES
    # ==========================================

    missing_values = {}

    for column in columns:

        missing_count = 0

        for row in rows:

            value = row.get(column, "")

            if value is None or value.strip() == "":
                missing_count += 1

        missing_values[column] = missing_count

    # ==========================================
    # 7. DETECT NUMERIC COLUMNS
    # ==========================================

    numeric_columns = {}

    for column in columns:

        values = []

        for row in rows:

            value = row.get(column, "")

            if value is None:
                continue

            value = value.strip()

            if value == "":
                continue

            try:
                values.append(float(value))
            except ValueError:
                pass

        if values:
            numeric_columns[column] = values

    # ==========================================
    # 8. BASIC STATISTICS
    # ==========================================

    statistics_summary = {}

    for column, values in numeric_columns.items():

        summary = {
            "count": len(values),
            "minimum": min(values),
            "maximum": max(values),
            "mean": statistics.mean(values)
        }

        if len(values) > 1:

            summary["median"] = statistics.median(values)

        statistics_summary[column] = summary

    # ==========================================
    # 9. SAMPLE DATA
    # ==========================================

    sample_rows = rows[:10]

    # ==========================================
    # 10. CREATE DATA CONTEXT
    # ==========================================

    context = f"""
Dataset Information:

File:
{file_path}

Number of Rows:
{number_of_rows}

Number of Columns:
{number_of_columns}

Columns:
{columns}

Missing Values:
{missing_values}

Numeric Columns:
{list(numeric_columns.keys())}

Statistics:
{statistics_summary}

Sample Data:
{sample_rows}
"""

    # ==========================================
    # 11. SEND TO LLM
    # ==========================================

    prompt = f"""
You are a Data Analytics Agent inside
Sovereign AI Workbench.

Your job is to analyze structured datasets
and provide clear and useful insights.

You can help with:

- Dataset summaries
- Column analysis
- Missing-value analysis
- Basic statistics
- Minimum and maximum values
- Mean and median
- Data quality observations
- Patterns in the provided sample
- Comparisons
- Basic business insights

IMPORTANT RULES:

1. Use ONLY the dataset information provided below.
2. Do not invent values or statistics.
3. Clearly distinguish facts from interpretations.
4. Mention the relevant column names.
5. Do not claim a trend or relationship unless the
   available data supports it.
6. If the requested analysis cannot be performed,
   clearly explain why.
7. Keep the response structured and easy to understand.

Dataset Context:
{context}

User Query:
{query}
"""

    answer = ask_llm(prompt)

    return answer