import streamlit as st
import json
import logging
import matplotlib.pyplot as plt
from load_file import get_azure_connection

SQL_BLACKLIST = ['DROP', 'DELETE', 'ATTACH', 'DETACH', 'ALTER', ';', '--', 'PRAGMA', 'EXEC', 'EXECUTE', 'INSERT', 'UPDATE']


def handle_structured_output(response_str) -> str:

    def execute_sql(query):
        """Execute SQL query on Azure SQL Database"""
        if any(bad in query.upper() for bad in SQL_BLACKLIST):
            raise ValueError("❌ Unsafe SQL query detected.")
        
        try:
            conn = get_azure_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            
            rows = cursor.fetchall()
            
            rows = [tuple(row) for row in rows]
            
            conn.close()
            return columns, rows
            
        except Exception as e:
            raise Exception(f"Database query failed: {str(e)}")

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

                try:
                    x_idx = columns.index(x_key)
                    y_idx = columns.index(y_key)
                except ValueError:
                    st.error(f"Column not found. Available columns: {columns}")
                    return "Chart: Error"

                x_vals = [row[x_idx] for row in rows]
                y_vals = [row[y_idx] for row in rows]

                if kind == "bar":
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.bar(x_vals, y_vals, color='#00b4d8')
                    ax.set_xlabel(x_key)
                    ax.set_ylabel(y_key)
                    ax.set_title(output.get("title", "Chart"))
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                elif kind == "line":
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(x_vals, y_vals, marker='o', linestyle='-', color='#00b4d8')
                    ax.set_xlabel(x_key)
                    ax.set_ylabel(y_key)
                    ax.set_title(output.get("title", "Chart"))
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                elif kind == "pie":
                    fig, ax = plt.subplots(figsize=(8, 8))
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
                st.code(f"Error: {str(e)}")
            return f"[Render error: {e}]"

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