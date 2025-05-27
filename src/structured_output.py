# structured_output.py

import streamlit as st
import sqlite3
import json
import logging
import matplotlib.pyplot as plt

# 🚫 Blacklist of unsafe keywords
SQL_BLACKLIST = ['DROP', 'DELETE', 'ATTACH', 'DETACH', 'ALTER', ';', '--', 'PRAGMA']

def execute_sql(query, db_path):
    if any(bad in query.upper() for bad in SQL_BLACKLIST):
        raise ValueError("❌ Unsafe SQL query detected.")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return columns, rows

def plot_chart(kind, x_vals, y_vals, x_key, y_key, title):
    fig, ax = plt.subplots(figsize=(8, 4))
    if kind == "bar":
        ax.bar(x_vals, y_vals)
    elif kind == "line":
        ax.plot(x_vals, y_vals, marker='o', linestyle='-')
    elif kind == "pie":
        fig, ax = plt.subplots()
        ax.pie(y_vals, labels=x_vals, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
    else:
        st.warning(f"Unsupported chart type: {kind}")
        return
    if kind != "pie":
        ax.set_xlabel(x_key)
        ax.set_ylabel(y_key)
        ax.set_title(title)
        plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

def render_single_output(output, db_path):
    try:
        output_type = output.get("type")
        title = output.get("title", output_type.capitalize())

        if output_type == "text":
            code = output.get("value_code", "").strip()
            value = ""
            if code:
                columns, rows = execute_sql(code, db_path)
                value = rows[0][0] if rows and rows[0] else ""
            final_text = output["template"].format(value=value)
            st.markdown(final_text)
            return final_text

        elif output_type in {"table", "chart"}:
            st.markdown(f"### {title}")
            columns, rows = execute_sql(output["code"], db_path)
            if not rows:
                st.info("No results returned.")
                return f"{output_type.capitalize()}: Empty"

            if output_type == "table":
                st.dataframe([dict(zip(columns, row)) for row in rows])
                return f"Table: {title}"

            x_key, y_key = output["x"], output["y"]
            kind = output.get("kind", "bar")
            x_vals = [row[columns.index(x_key)] for row in rows]
            y_vals = [row[columns.index(y_key)] for row in rows]

            # if len(x_vals) > 100:
            #     st.info("Chart generation skipped: too many entries")
            #     return f"Chart: Empty"

            plot_chart(kind, x_vals, y_vals, x_key, y_key, title)
            return f"Chart: {title}"

        else:
            raise ValueError("Unknown response type")

    except Exception as e:
        logging.error(f"Structured output rendering failed: {e}")
        st.error("⚠️ Error while displaying output.")
        # with st.expander("Show Debug Info"):
        #     st.code(str(output), language="json")
        return f"[Render error: {e}]"

def handle_structured_output(response_str, db_path: str) -> str:
    try:
        parsed = json.loads(response_str)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}\nRaw: {response_str}")
        st.error("⚠️ Invalid response format.")
        # with st.expander("Show Raw Response"):
        #     st.code(response_str, language="json")
        return "[Invalid JSON]"

    if isinstance(parsed, list):
        return "\n".join(render_single_output(obj, db_path) for obj in parsed)
    else:
        return render_single_output(parsed, db_path)
