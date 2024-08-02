import plotly.express as px

# palette_set = px.colors.qualitative.Alphabet
palette_set = px.colors.qualitative.Prism

reserved_str = """? & | ! { } [ ] ( ) ^ ~ * : \ " ' + -"""
esc_dict = {chr: f"\\{chr}" for chr in reserved_str}
esc_dict.pop(" ")
