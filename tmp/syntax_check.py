import sys
from pyspark.sql import SparkSession
from pyspark.sql.utils import ParseException

spark = SparkSession.builder.appName("SyntaxCheck").getOrCreate()

with open(sys.argv[1], "r", encoding="utf-8") as f:
    sql_text = f.read()

# split by semicolon but ignore inside quotes
sqls = [s.strip() for s in sql_text.split(";") if s.strip()]
has_error = False
for q in sqls:
    if q.startswith("--"):
        continue
    try:
        spark.sql(f"EXPLAIN {q}")
    except Exception as e:
        if "Table or view not found" in str(e) or "AnalysisException" in str(e):
            # This is fine, we just want to catch ParseException (syntax error)
            pass
        elif "ParseException" in str(e) or "Syntax error" in str(e) or "mismatched input" in str(e):
            print("Syntax Error in query:\n", q)
            print("Error detail:", e)
            has_error = True

if not has_error:
    print("Syntax check passed!")
