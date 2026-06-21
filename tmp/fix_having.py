import os
import glob
import re

sql_dir = r"e:\DTSW\业务文档\需求实现\中台H3业务迁移(20251103)\离线任务正式迁移\other_sql_file"

def fix_having_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original_content = content
    
    # We will search for 'having' followed by 'rn'
    pattern = re.compile(r'having\s+rn\s*([=><]+)\s*(\d+)', re.IGNORECASE)
    
    while True:
        match = pattern.search(content)
        if not match:
            break
            
        operator = match.group(1)
        value = match.group(2)
        end_idx = match.end()
        start_idx = match.start()
        
        # Search backwards for the SELECT that corresponds to this having
        # We need to balance parentheses to find the right SELECT.
        # But SQL is tricky. Let's just find the closest previous "select" that is at the same parenthesis level.
        # Actually, if we just find the closest "select" (case insensitive) looking backwards:
        select_idx = -1
        parens = 0
        for i in range(start_idx, -1, -1):
            if content[i] == ')':
                parens += 1
            elif content[i] == '(':
                parens -= 1
                
            if parens < 0:
                # We stepped out of the query block, this means the SELECT must be inside
                pass
                
            if parens == 0:
                if content[i:i+6].lower() == 'select':
                    # Check if it's a whole word
                    if i == 0 or not content[i-1].isalpha():
                        select_idx = i
                        break
                        
        if select_idx != -1:
            # We found the select. 
            # Replace the select with "SELECT * FROM ( \n SELECT"
            # and the having with ") t WHERE rn [op] [val]"
            
            # Let's check if we already wrapped it previously
            # to avoid double wrapping if we run multiple times (though we process string dynamically)
            prefix = "select * from (\n" + " " * 8
            suffix = f"\n    ) t\n    where rn {operator} {value}"
            
            before = content[:select_idx]
            query_part = content[select_idx:start_idx]
            after = content[end_idx:]
            
            # Remove trailing whitespaces from query_part before replacing
            query_part = query_part.rstrip()
            
            content = before + prefix + query_part + suffix + after
        else:
            # Couldn't parse, just break to avoid infinite loop
            print(f"Failed to find SELECT for having in {filepath}")
            break

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed having in: {os.path.basename(filepath)}")

for filepath in glob.glob(os.path.join(sql_dir, "*.sql")):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if re.search(r'having\s+rn\s*[=><]+\s*\d+', content, re.IGNORECASE):
        fix_having_in_file(filepath)
        
print("Done with having.")
