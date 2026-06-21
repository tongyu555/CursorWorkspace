# Python 学习重点知识与面试总结

## 目录
1. [Python 核心基础与重要语法](#一-python-核心基础与重要语法)
2. [Python 常用基础库与第三方包](#二-python-常用基础库与第三方包)
3. [Python 常见高频面试题总结](#三-python-常见高频面试题总结)

---

## 一、 Python 核心基础与重要语法

### 1. 基础数据类型
Python 中的变量不需要显式声明类型。核心的数据结构分为 **可变(Mutable)** 与 **不可变(Immutable)** 两种。
- **不可变类型**：`int` (整型), `float` (浮点型), `bool` (布尔型), `str` (字符串), `tuple` (元组)。一旦创建，其在内存中的值不可改变。
- **可变类型**：`list` (列表), `dict` (字典), `set` (集合)。可以在原处进行元素的增删改。

**常用写法示例：**
```python
# 列表推导式 (List Comprehension) - 极其常用，用于快速生成列表
squares = [x**2 for x in range(10) if x % 2 == 0]

# 字典推导式
squares_dict = {x: x**2 for x in range(5)}

# 集合操作
set_a, set_b = {1, 2, 3}, {3, 4, 5}
print(set_a & set_b)  # 交集 {3}
print(set_a | set_b)  # 并集 {1, 2, 3, 4, 5}
```

### 2. 函数与参数传递 (`*args` 和 `**kwargs`)
Python 的函数支持默认参数、关键字参数、不定长参数等。
- `*args`：用于接收任意数量的位置参数，将其封装为一个**元组**。
- `**kwargs`：用于接收任意数量的关键字参数，将其封装为一个**字典**。

```python
def my_func(a, b=2, *args, **kwargs):
    print(f"a: {a}, b: {b}")
    print(f"args: {args}")     # tuple
    print(f"kwargs: {kwargs}") # dict

my_func(1, 3, 4, 5, name="Alice", age=25)
```

### 3. 面向对象 (OOP) 与魔法方法
Python 是一门完全面向对象的语言。类中的“魔法方法”(Magic Methods) 形如 `__xxx__`，能在特定场景下被自动调用。
- `__init__(self)`：初始化方法（构造函数）。
- `__str__(self)`：定义对象的字符串表示，用于 `print()`。
- `__call__(self)`：使类的实例可以像函数一样被调用。

```python
class Person:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Person: {self.name}"

p = Person("Bob")
print(p) # 输出: Person: Bob
```

### 4. 装饰器 (Decorators)
装饰器是 Python 中的核心高级特性，本质是一个函数，用于在**不修改原函数代码**的前提下，为函数**增加额外功能**（如日志打印、性能测试、权限校验等）。

```python
import time

# 定义一个装饰器
def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[{func.__name__}] 耗时: {end_time - start_time:.4f}s")
        return result
    return wrapper

# 使用装饰器
@timer_decorator
def heavy_computation():
    time.sleep(1)
    return "Done!"

heavy_computation()
```

### 5. 生成器 (Generators) 与迭代器 (Iterators)
- **迭代器**：实现了 `__iter__` 和 `__next__` 方法的对象，可以通过 `next()` 获取下一个值。
- **生成器**：一种特殊的迭代器，通过 `yield` 关键字返回数据。它不会一次性把所有数据加载到内存，而是“用一个生成一个”，非常适合处理海量数据。

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# 遍历生成器，占用极小内存
for num in fibonacci(5):
    print(num)
```

### 6. 上下文管理器 (Context Manager)
使用 `with` 语句可以自动管理资源的获取与释放（如文件操作、数据库连接）。即使发生异常也能保证资源被正确释放。

```python
# 推荐写法
with open("test.txt", "w", encoding="utf-8") as f:
    f.write("Hello World!")
# 离开 with 块时，自动调用 f.close()
```

---

## 二、 Python 常用基础库与第三方包

### 1. 常用内置标准库
- **`os` / `sys`**：操作系统接口，路径处理、环境变量、命令行参数读取等。
- **`json`**：处理 JSON 数据的序列化 (`json.dumps`, `json.dump`) 与反序列化 (`json.loads`, `json.load`)。
- **`datetime` / `time`**：时间与日期的处理及格式化。
- **`re`**：正则表达式模块，用于字符串的复杂匹配与替换。
- **`collections`**：提供额外的高性能数据结构，如 `defaultdict` (带默认值的字典), `Counter` (计数器), `deque` (双端队列)。
- **`itertools`**：提供用于操作迭代对象的函数，如排列组合。

### 2. 常用第三方库（需要 pip install）
| 库名 | 核心作用 | 常见用法示例 / 适用场景 |
| :--- | :--- | :--- |
| **`requests`** | 发送 HTTP 请求的利器，比内置的 `urllib` 简单无数倍。 | `requests.get('https://api.github.com')` |
| **`pandas`** | 数据分析与处理，提供强大的 DataFrame 结构，处理表格数据如 Excel、CSV。 | `pd.read_csv('data.csv')`<br/>`df.groupby('category').sum()` |
| **`numpy`** | 科学计算基础库，支持高效的多维数组(ndarray)与矩阵运算。 | `np.array([1, 2, 3])` |
| **`matplotlib` / `seaborn`**| 数据可视化，用于绘制折线图、柱状图、散点图等。 | `plt.plot(x, y)` |
| **`fastapi` / `flask`** | Web 开发框架。Flask 轻量灵活；FastAPI 现代且性能极高，自带异步与接口文档生成。 | 开发后端 RESTful API 服务。 |
| **`pytest`** | 单元测试框架，比自带的 `unittest` 更加简洁易用。 | `pytest test_main.py` |

---

## 三、 Python 常见高频面试题总结

### 1. `is` 和 `==` 的区别是什么？
- **`==`**：比较两个对象的**值**是否相等（调用 `__eq__` 方法）。
- **`is`**：比较两个对象的**内存地址**是否相同（即是否是同一个对象，等同于 `id(a) == id(b)`）。
*(注：Python 为了优化，对小整数和短字符串存在内存池驻留机制，在这部分区间内 `is` 和 `==` 结果可能一致，但这仅仅是底层优化策略。)*

### 2. Python 中的深拷贝 (Deep Copy) 和浅拷贝 (Shallow Copy)
- **直接赋值** (`a = b`)：仅仅是对象的引用传递。
- **浅拷贝** (`copy.copy(obj)` 或 `list[:]`)：创建一个新对象，但新对象内部的子元素依然是原对象子元素的引用。
- **深拷贝** (`copy.deepcopy(obj)`)：创建一个全新对象，并且递归地拷贝原对象内部所有的子对象，两者完全独立。

### 3. 什么是 GIL (Global Interpreter Lock)？它对并发有什么影响？
- **定义**：GIL 是全局解释器锁。CPython（Python的官方实现）因为内存管理非线程安全，引入了 GIL，**确保同一时刻只有一个线程在执行 Python 字节码**。
- **影响**：导致 Python 的多线程无法真正利用多核 CPU 的并行计算能力。
- **解决方案**：
  - **CPU 密集型任务**（如大量数学计算）：使用**多进程** (`multiprocessing`) 来避开 GIL。
  - **IO 密集型任务**（如网络请求、文件读写）：使用**多线程** (`threading`) 或 **异步IO** (`asyncio`，协程)。因为在等待 IO 时，线程会释放 GIL。

### 4. 什么是鸭子类型 (Duck Typing)？
Python 属于动态强类型语言，推崇鸭子类型：*“如果它走起来像鸭子，叫起来像鸭子，那么它就是鸭子。”*
意味着我们不关注对象的类型本身，只关注对象**是否拥有我们需要的方法或属性**。例如，只要对象实现了 `__iter__` 方法，就可以放在 `for` 循环中遍历，不管它是列表、字典还是自定义类。

### 5. 简述 Python 的垃圾回收 (GC) 机制
Python 内存管理主要以**引用计数**为主，**标记-清除**和**分代回收**为辅。
- **引用计数 (Reference Counting)**：每个对象都有一个引用数量的计数器。当有变量指向它时计数 +1，引用销毁时 -1。当计数降为 0 时，对象内存立即被释放。
- **标记-清除 (Mark-Sweep)**：主要用于解决**循环引用**（比如 A 引用 B，B 又引用 A，导致引用计数永远不为 0）的问题。
- **分代回收 (Generational Collection)**：为了提高垃圾回收效率，Python 将对象分为新生代、中年代、老年代。存活越久的对象越少被执行 GC 扫描。

### 6. 列表推导式与生成器表达式的区别？
- 列表推导式：`[x for x in range(1000)]`，使用中括号。直接在内存中生成一个包含 1000 个元素的完整列表。占用内存大。
- 生成器表达式：`(x for x in range(1000))`，使用小括号。返回一个生成器对象，按需产生值，极大地节省内存。

### 7. 说说闭包 (Closure)
闭包是指一个**内层函数**中引用了**外层函数的作用域**中的变量，并且外层函数的返回值是这个内层函数。闭包是实现装饰器的基础。
```python
def outer(msg):
    def inner():
        print(f"Message: {msg}") # 引用了外部作用域的变量 msg
    return inner
```
