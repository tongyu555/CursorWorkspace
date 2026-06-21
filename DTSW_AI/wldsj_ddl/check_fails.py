import re
import sys

file_path = r'E:\CursorWorkspace\DTSW_AI\Spark_Thrift\tool\runs\2026-05-26\hx_ddl_20260427_final_20260526_160125_486\result.txt'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

failures = re.findall(r'\[FAIL\] (.*?(?=\[FAIL\]|\[OK\]|exit_code|---|$))', content, re.DOTALL)
actual_failures = []
for fail in failures:
    if 'TableAlreadyExistsException' not in fail:
        actual_failures.append(fail)

print(f"Total non-AlreadyExists failures: {len(actual_failures)}")
if actual_failures:
    print("First 3 actual failures:")
    for f in actual_failures[:3]:
        print("--------------------")
        print(f[:500] + '...')
