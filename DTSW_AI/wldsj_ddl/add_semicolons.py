import re

input_file = r'e:\CursorWorkspace\DTSW_AI\wldsj_ddl\hx_ddl_20260427_clean.sql'
output_file = r'e:\CursorWorkspace\DTSW_AI\wldsj_ddl\hx_ddl_20260427_final.sql'

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

parts = re.split(r'(?=\bCREATE\s+(?:EXTERNAL\s+)?TABLE\b)', content)

new_parts = []
for p in parts:
    p_stripped = p.rstrip()
    if p_stripped:
        if not p_stripped.endswith(';'):
            # add semicolon
            p = p_stripped + ';\n\n'
        else:
            p = p_stripped + '\n\n'
    new_parts.append(p)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("".join(new_parts))

print("Added semicolons.")
