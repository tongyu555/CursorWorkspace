import os
import re
import glob

sql_dir = r"e:\DTSW\业务文档\需求实现\中台H3业务迁移(20251103)\离线任务正式迁移\other_sql_file"

cache_re = re.compile(r'cache\s+table\s+([a-zA-Z0-9_.]+)', re.IGNORECASE)
having_re = re.compile(r'having\s+rn\s*[=<>]+\s*\d+', re.IGNORECASE)

files_with_cache = []
files_with_having = []

for filepath in glob.glob(os.path.join(sql_dir, "*.sql")):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    cache_matches = cache_re.findall(content)
    if cache_matches:
        files_with_cache.append((os.path.basename(filepath), cache_matches))
        
    if having_re.search(content):
        files_with_having.append(os.path.basename(filepath))

print("Files with cache table declarations:")
for f, m in files_with_cache:
    print(f"- {f}: {m}")

print("\nFiles with having rn:")
for f in files_with_having:
    print(f"- {f}")
