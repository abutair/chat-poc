# structured_output.py

import streamlit as st
import sqlite3
import json
import logging
import matplotlib.pyplot as plt

# 🚫 Blacklist of unsafe keywords
SQL_BLACKLIST = ['DROP', 'DELETE', 'ATTACH', 'DETACH', 'ALTER', ';', '--', 'PRAGMA']


def handle_structured_output(response_str, db_path: str) -> str:

    def execute_sql(query):
        if any(bad in query.upper() for bad in SQL_BLACKLIST):
            raise ValueError("❌ Unsafe SQL query detected.")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return columns, rows

    def render_single_output(output):
        try:
            if output["type"] == "text":
                code = output.get("value_code", "").strip()
                value = ""
                if code:
                    columns, rows = execute_sql(code)
                    value = rows[0][0] if rows and rows[0] else ""
                final_text = output["template"].format(value=value)
                st.markdown(final_text)
                return final_text

            elif output["type"] == "table":
                st.markdown(f"### {output.get('title', 'Table')}")
                columns, rows = execute_sql(output["code"])
                if not rows:
                    st.info("No results returned.")
                    return "Table: Empty"
                st.dataframe([dict(zip(columns, row)) for row in rows])
                return f"Table: {output.get('title', 'Untitled')}"

            elif output["type"] == "chart":
                st.markdown(f"### {output.get('title', 'Chart')}")
                columns, rows = execute_sql(output["code"])
                if not rows:
                    st.info("No results returned.")
                    return "Chart: Empty"

                x_key = output["x"]
                y_key = output["y"]
                kind = output.get("kind", "bar")

                x_vals = [row[columns.index(x_key)] for row in rows]
                y_vals = [row[columns.index(y_key)] for row in rows]

                if kind == "bar":
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.bar(x_vals, y_vals, color='#00b4d8')
                    ax.set_xlabel(x_key)
                    ax.set_ylabel(y_key)
                    ax.set_title(output.get("title", "Chart"))
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                elif kind == "line":
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.plot(x_vals, y_vals, marker='o', linestyle='-', color='#00b4d8')
                    ax.set_xlabel(x_key)
                    ax.set_ylabel(y_key)
                    ax.set_title(output.get("title", "Chart"))
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                elif kind == "pie":
                    fig, ax = plt.subplots()
                    ax.pie(y_vals, labels=x_vals, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig)
                else:
                    st.warning(f"Unsupported chart type: {kind}")
                return f"Chart: {output.get('title', 'Untitled')}"

            else:
                raise ValueError("Unknown response type")

        except Exception as e:
            logging.error(f"Structured output rendering failed: {e}")
            st.error("⚠️ Error while displaying output.")
            with st.expander("Show Debug Info"):
                st.code(str(output), language="json")
            return f"[Render error: {e}]"

    # Parse and render output
    try:
        parsed = json.loads(response_str)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}\nRaw: {response_str}")
        st.error("⚠️ Invalid response format.")
        with st.expander("Show Raw Response"):
            st.code(response_str, language="json")
        return "[Invalid JSON]"

    if isinstance(parsed, list):
        return "\n".join(render_single_output(obj) for obj in parsed)
    else:
        return render_single_output(parsed)
