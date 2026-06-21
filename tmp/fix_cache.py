import os
import re
import glob

sql_dir = r"e:\DTSW\业务文档\需求实现\中台H3业务迁移(20251103)\离线任务正式迁移\other_sql_file"

for filepath in glob.glob(os.path.join(sql_dir, "*.sql")):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original_content = content
    
    # Extract cache tables
    cache_tables = []
    matches = re.finditer(r'(?i)cache\s+table\s+(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)', content)
    for m in matches:
        tname = m.group(1).lower()
        if tname != 'if':
            cache_tables.append(tname)
            
    if not cache_tables:
        continue
        
    # Remove database prefix from cache table declarations
    content = re.sub(r'(?i)(cache\s+table\s+)[a-zA-Z0-9_]+\.([a-zA-Z0-9_]+)', r'\1\2', content)
    
    # Remove database prefix from uncache table declarations
    content = re.sub(r'(?i)(uncache\s+table\s+(?:if\s+exists\s+)?)[a-zA-Z0-9_]+\.([a-zA-Z0-9_]+)', r'\1\2', content)
    
    # Remove database prefix from references to these cache tables
    for tname in set(cache_tables):
        pattern = re.compile(r'(?i)\b[a-zA-Z0-9_]+\.' + re.escape(tname) + r'\b')
        content = pattern.sub(tname, content)
        
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated cache tables in: {os.path.basename(filepath)}")

print("Done with cache tables.")
