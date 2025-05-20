import streamlit as st
import pandas as pd
import json
import logging
import matplotlib.pyplot as plt
import traceback
from pandas.errors import EmptyDataError

# 🚫 Blacklist of unsafe keywords
BLACKLIST = ['__', 'import', 'os', 'sys', 'eval', 'exec', 'subprocess', 'open']

def is_code_safe(code):
    """Check if code contains unsafe keywords"""
    if any(bad in code for bad in BLACKLIST):
        return False
    return True

def handle_structured_output(response_str, sheets) -> str:

    def render_single_output(output, sheets):
        try:
            if output["type"] == "text":
                if "value_code" in output and output["value_code"].strip():
                    code = output["value_code"]
                    if not is_code_safe(code):
                        raise ValueError("❌ Unsafe code detected in value_code.")
                    
                    # Create a safe execution environment with limited globals
                    safe_globals = {
                        "__builtins__": {
                            "True": True, "False": False, "None": None,
                            "abs": abs, "bool": bool, "dict": dict, "float": float,
                            "int": int, "len": len, "list": list, "max": max, "min": min,
                            "range": range, "round": round, "str": str, "sum": sum,
                            "tuple": tuple, "type": type
                        }
                    }
                    
                    # Add pandas with proper imports for datetime functionality
                    safe_locals = {
                        "sheets": sheets, 
                        "pd": pd,
                        "datetime": pd.datetime,
                        "Timestamp": pd.Timestamp
                    }
                    
                    value = eval(code, safe_globals, safe_locals)
                    final_text = output["template"].format(value=value)
                else:
                    final_text = output["template"]
                st.markdown(final_text)
                return final_text

            elif output["type"] == "table":
                code = output["code"]
                if not is_code_safe(code):
                    raise ValueError("❌ Unsafe code detected in table code.")
                
                # Create a safe execution environment
                safe_globals = {
                    "__builtins__": {
                        "True": True, "False": False, "None": None,
                        "abs": abs, "bool": bool, "dict": dict, "float": float,
                        "int": int, "len": len, "list": list, "max": max, "min": min,
                        "range": range, "round": round, "str": str, "sum": sum,
                        "tuple": tuple, "type": type
                    }
                }
                
                # Add pandas with proper imports
                safe_locals = {
                    "sheets": sheets, 
                    "pd": pd,
                    "datetime": pd.to_datetime,
                    "Timestamp": pd.Timestamp,
                    "timedelta": pd.Timedelta,
                    "to_datetime": pd.to_datetime,
                    "to_timedelta": pd.to_timedelta,
                    "NaT": pd.NaT
                }
                
                df = eval(code, safe_globals, safe_locals)
                
                # Check if we got a DataFrame
                if not isinstance(df, pd.DataFrame):
                    raise TypeError(f"Expected DataFrame but got {type(df).__name__}")
                
                st.markdown(f"### {output.get('title', 'Table')}")
                
                # If it's a message-style DataFrame (for no data scenarios)
                if 'Message' in df.columns and len(df.columns) == 1:
                    st.warning(df['Message'].iloc[0])
                # If it's an error-style DataFrame
                elif 'Error' in df.columns and len(df.columns) == 1:
                    st.error(df['Error'].iloc[0])
                # Normal DataFrame
                else:
                    st.dataframe(df)
                
                return f"Table: {output.get('title', 'Untitled')}"

            elif output["type"] == "chart":
                code = output["code"]
                if not is_code_safe(code):
                    raise ValueError("❌ Unsafe code detected in chart code.")
                
                # Create a safe execution environment
                safe_globals = {
                    "__builtins__": {
                        "True": True, "False": False, "None": None,
                        "abs": abs, "bool": bool, "dict": dict, "float": float,
                        "int": int, "len": len, "list": list, "max": max, "min": min,
                        "range": range, "round": round, "str": str, "sum": sum,
                        "tuple": tuple, "type": type
                    }
                }
                
                # Add pandas with proper imports
                safe_locals = {
                    "sheets": sheets, 
                    "pd": pd,
                    "datetime": pd.datetime,
                    "Timestamp": pd.Timestamp,
                    "timedelta": pd.Timedelta,
                    "to_datetime": pd.to_datetime,
                    "to_timedelta": pd.to_timedelta,
                    "NaT": pd.NaT
                }
                
                df = eval(code, safe_globals, safe_locals)
                
                # Check if we got a DataFrame
                if not isinstance(df, pd.DataFrame):
                    raise TypeError(f"Expected DataFrame but got {type(df).__name__}")
                
                # Special case handling for "no data" message DataFrames
                if 'Message' in df.columns and len(df.columns) == 1:
                    st.markdown(f"### {output.get('title', 'Chart')}")
                    st.warning(df['Message'].iloc[0])
                    return f"Chart: {output.get('title', 'Untitled')} (No Data)"
                
                # Special case handling for error DataFrames  
                if 'Error' in df.columns and len(df.columns) == 1:
                    st.markdown(f"### {output.get('title', 'Chart')}")
                    st.error(df['Error'].iloc[0])
                    return f"Chart: {output.get('title', 'Untitled')} (Error)"
                
                st.markdown(f"### {output.get('title', 'Chart')}")
                
                chart_type = output.get("kind", "bar")
                x = output["x"]
                y = output["y"]
                
                # Check if the required columns exist
                if x not in df.columns:
                    st.error(f"Column '{x}' not found in the data")
                    return f"Chart Error: Column '{x}' not found"
                
                if y not in df.columns:
                    st.error(f"Column '{y}' not found in the data")
                    return f"Chart Error: Column '{y}' not found"
                
                # Check if we have data
                if len(df) == 0:
                    st.warning("No data available for chart")
                    return f"Chart: {output.get('title', 'Untitled')} (No Data)"
                
                # Generate the appropriate chart type
                try:
                    if chart_type == "bar":
                        st.bar_chart(df.set_index(x)[y])
                    elif chart_type == "line":
                        st.line_chart(df.set_index(x)[y])
                    elif chart_type == "pie":
                        fig, ax = plt.subplots()
                        ax.pie(df[y], labels=df[x], autopct='%1.1f%%', startangle=90)
                        ax.axis('equal')  # Equal aspect ratio ensures the pie is a circle.
                        st.pyplot(fig)
                    else:
                        st.warning(f"Unsupported chart type: {chart_type}")
                except Exception as chart_err:
                    st.error(f"Error creating chart: {str(chart_err)}")
                    
                return f"Chart: {output.get('title', 'Untitled')}"

            else:
                raise ValueError(f"Unknown response type: {output['type']}")

        except Exception as e:
            logging.error(f"Structured output rendering failed: {str(e)}")
            logging.error(traceback.format_exc())
            st.error("⚠️ Oops! Something went wrong while displaying the answer.")
            with st.expander("Show Debug Info"):
                st.code(str(e), language="text")
                st.code(traceback.format_exc(), language="python")
            return f"[Render error: {str(e)}]"

    # First, try to parse JSON (single or multi-object)
    try:
        parsed = json.loads(response_str)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}\nRaw: {response_str}")
        st.error("⚠️ Invalid response format. Could not parse the answer.")
        with st.expander("Show Raw Response"):
            st.code(response_str, language="json")
        return "[Invalid JSON]"

    # If it's a list of outputs, render each
    if isinstance(parsed, list):
        return "\n".join(render_single_output(obj, sheets) for obj in parsed)
    else:
        return render_single_output(parsed, sheets)