import org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesDecrypt;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDF;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;
import org.apache.hadoop.io.BytesWritable;
import org.apache.hadoop.io.Text;

import java.io.BufferedReader;
import java.io.FileReader;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

/**
 * Hive AES 解密工具 - IDEA直接运行版
 * 
 * 使用方法:
 * 1. 在IDEA中添加 hive-exec-2.3.9-core.jar 到项目依赖
 * 2. 修改下面的 SECRET_KEY 为你的密钥
 * 3. 直接运行 main 方法
 */
public class SimpleHiveDecrypt {
    
    // ========== 配置区域 - 修改这里 ==========
    
    // 密钥 - 请修改为你的实际密钥
    private static final String SECRET_KEY = "mykey123";
    
    // 输入文件 - 包含加密数据的文件路径
    private static final String INPUT_FILE = "E:\\cursor_test\\data_jiami.txt";
    
    // ========================================
    
    
    private GenericUDFAesDecrypt decryptUDF;
    
    public SimpleHiveDecrypt() throws Exception {
        this.decryptUDF = new GenericUDFAesDecrypt();
        
        // 初始化 UDF
        ObjectInspector[] arguments = new ObjectInspector[] {
            PrimitiveObjectInspectorFactory.writableBinaryObjectInspector,  // 密文
            PrimitiveObjectInspectorFactory.writableStringObjectInspector   // 密钥
        };
        decryptUDF.initialize(arguments);
    }
    
    /**
     * 解密单条数据
     */
    public String decrypt(String ciphertextBase64, String key) {
        try {
            // Base64 解码
            byte[] ciphertextBytes = Base64.getDecoder().decode(ciphertextBase64.trim());
            
            // 创建参数
            GenericUDF.DeferredObject[] arguments = new GenericUDF.DeferredObject[] {
                new GenericUDF.DeferredJavaObject(new BytesWritable(ciphertextBytes)),
                new GenericUDF.DeferredJavaObject(new Text(key))
            };
            
            // 解密
            Object result = decryptUDF.evaluate(arguments);
            
            if (result == null) {
                return "[解密失败 - 密钥可能不正确]";
            }
            
            // 转换结果
            if (result instanceof BytesWritable) {
                BytesWritable bw = (BytesWritable) result;
                return new String(bw.getBytes(), 0, bw.getLength(), StandardCharsets.UTF_8);
            } else if (result instanceof byte[]) {
                return new String((byte[]) result, StandardCharsets.UTF_8);
            } else {
                return result.toString();
            }
            
        } catch (Exception e) {
            return "[异常] " + e.getMessage();
        }
    }
    
    /**
     * 主函数 - 直接运行这个方法
     */
    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("Hive AES 解密工具");
        System.out.println("========================================");
        System.out.println("密钥: " + SECRET_KEY);
        System.out.println("文件: " + INPUT_FILE);
        System.out.println("========================================\n");
        
        try {
            SimpleHiveDecrypt decryptor = new SimpleHiveDecrypt();
            
            // 读取文件并解密
            BufferedReader reader = new BufferedReader(new FileReader(INPUT_FILE));
            String line;
            int lineNumber = 0;
            int successCount = 0;
            
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) {
                    continue;
                }
                
                lineNumber++;
                System.out.println("第 " + lineNumber + " 行:");
                System.out.println("  密文: " + line);
                
                String plaintext = decryptor.decrypt(line, SECRET_KEY);
                System.out.println("  明文: " + plaintext);
                
                if (!plaintext.startsWith("[")) {
                    successCount++;
                }
                System.out.println();
            }
            reader.close();
            
            System.out.println("========================================");
            System.out.println("解密完成! 成功: " + successCount + "/" + lineNumber + " 条");
            System.out.println("========================================");
            
        } catch (Exception e) {
            System.err.println("[错误] " + e.getMessage());
            e.printStackTrace();
            System.out.println("\n提示:");
            System.out.println("1. 请确保已添加 hive-exec-2.3.9-core.jar 到项目依赖");
            System.out.println("2. 请修改代码中的 SECRET_KEY 为正确的密钥");
            System.out.println("3. 请确保 INPUT_FILE 路径正确");
        }
    }
}







