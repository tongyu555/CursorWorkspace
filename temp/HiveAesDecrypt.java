import org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesDecrypt;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDF;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspectorFactory;
import org.apache.hadoop.io.BytesWritable;
import org.apache.hadoop.io.Text;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Base64;

/**
 * Hive AES 解密工具
 * 使用 Hive 的 GenericUDFAesDecrypt 进行解密
 * 
 * 编译方法:
 * javac -cp "hive-exec-2.3.9-core.jar" HiveAesDecrypt.java
 * 
 * 运行方法:
 * java -cp ".;hive-exec-2.3.9-core.jar" HiveAesDecrypt <密钥> <输入文件> [输出文件]
 */
public class HiveAesDecrypt {
    
    private GenericUDFAesDecrypt decryptUDF;
    private String secretKey;
    
    /**
     * 构造函数
     * @param secretKey 解密密钥
     */
    public HiveAesDecrypt(String secretKey) throws Exception {
        this.secretKey = secretKey;
        this.decryptUDF = new GenericUDFAesDecrypt();
        
        // 初始化 UDF
        initializeUDF();
    }
    
    /**
     * 初始化 Hive UDF
     */
    private void initializeUDF() throws Exception {
        // 创建参数的 ObjectInspector
        ObjectInspector[] arguments = new ObjectInspector[] {
            PrimitiveObjectInspectorFactory.writableBinaryObjectInspector,  // 密文 (二进制)
            PrimitiveObjectInspectorFactory.writableStringObjectInspector   // 密钥 (字符串)
        };
        
        // 初始化 UDF
        decryptUDF.initialize(arguments);
    }
    
    /**
     * 解密单条数据
     * @param ciphertextBase64 Base64编码的密文
     * @return 解密后的明文
     */
    public String decrypt(String ciphertextBase64) {
        try {
            // Base64 解码
            byte[] ciphertextBytes = Base64.getDecoder().decode(ciphertextBase64.trim());
            
            // 创建 Hive 所需的参数对象
            GenericUDF.DeferredObject[] arguments = new GenericUDF.DeferredObject[] {
                new GenericUDF.DeferredJavaObject(new BytesWritable(ciphertextBytes)),
                new GenericUDF.DeferredJavaObject(new Text(secretKey))
            };
            
            // 调用 UDF 进行解密
            Object result = decryptUDF.evaluate(arguments);
            
            if (result == null) {
                return "[解密失败] 返回null - 请检查密钥是否正确";
            }
            
            // 转换结果为字符串
            if (result instanceof BytesWritable) {
                BytesWritable bw = (BytesWritable) result;
                return new String(bw.getBytes(), 0, bw.getLength(), StandardCharsets.UTF_8);
            } else if (result instanceof byte[]) {
                return new String((byte[]) result, StandardCharsets.UTF_8);
            } else {
                return result.toString();
            }
            
        } catch (Exception e) {
            return "[解密异常] " + e.getMessage();
        }
    }
    
    /**
     * 从文件批量解密
     * @param inputFile 输入文件路径
     * @param outputFile 输出文件路径 (可选)
     */
    public void decryptFromFile(String inputFile, String outputFile) {
        System.out.println("========================================");
        System.out.println("Hive AES 批量解密工具");
        System.out.println("========================================");
        System.out.println("输入文件: " + inputFile);
        System.out.println("密钥: " + secretKey);
        if (outputFile != null) {
            System.out.println("输出文件: " + outputFile);
        }
        System.out.println("========================================\n");
        
        List<String> results = new ArrayList<>();
        int successCount = 0;
        int failCount = 0;
        
        try (BufferedReader reader = new BufferedReader(new FileReader(inputFile))) {
            String line;
            int lineNumber = 0;
            
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                line = line.trim();
                
                if (line.isEmpty()) {
                    continue;
                }
                
                System.out.println("第 " + lineNumber + " 行:");
                System.out.println("  密文: " + line);
                
                // 解密
                String plaintext = decrypt(line);
                System.out.println("  明文: " + plaintext);
                
                if (plaintext.startsWith("[解密")) {
                    failCount++;
                } else {
                    successCount++;
                }
                
                // 保存结果
                results.add(plaintext);
                System.out.println();
            }
            
            // 如果指定了输出文件，写入结果
            if (outputFile != null) {
                try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile))) {
                    for (String result : results) {
                        writer.write(result);
                        writer.newLine();
                    }
                }
                System.out.println("解密结果已保存到: " + outputFile);
            }
            
            // 统计信息
            System.out.println("\n========================================");
            System.out.println("解密完成!");
            System.out.println("成功: " + successCount + " 条");
            System.out.println("失败: " + failCount + " 条");
            System.out.println("========================================");
            
        } catch (FileNotFoundException e) {
            System.err.println("[错误] 找不到文件: " + inputFile);
        } catch (IOException e) {
            System.err.println("[错误] 读取文件失败: " + e.getMessage());
        }
    }
    
    /**
     * 交互式解密模式
     */
    public void interactiveMode() {
        System.out.println("========================================");
        System.out.println("Hive AES 交互式解密工具");
        System.out.println("========================================");
        System.out.println("密钥: " + secretKey);
        System.out.println("请输入Base64编码的密文 (输入 'exit' 退出):");
        System.out.println("========================================\n");
        
        BufferedReader consoleReader = new BufferedReader(new InputStreamReader(System.in));
        
        try {
            while (true) {
                System.out.print("密文 > ");
                String ciphertext = consoleReader.readLine();
                
                if (ciphertext == null || ciphertext.trim().equalsIgnoreCase("exit")) {
                    System.out.println("退出程序");
                    break;
                }
                
                ciphertext = ciphertext.trim();
                if (ciphertext.isEmpty()) {
                    continue;
                }
                
                String plaintext = decrypt(ciphertext);
                System.out.println("明文 > " + plaintext);
                System.out.println();
            }
        } catch (IOException e) {
            System.err.println("[错误] 读取输入失败: " + e.getMessage());
        }
    }
    
    /**
     * 打印使用说明
     */
    private static void printUsage() {
        System.out.println("========================================");
        System.out.println("Hive AES 解密工具 - 使用说明");
        System.out.println("========================================");
        System.out.println("\n用法:");
        System.out.println("  方式1 (批量解密): java -cp \".;hive-exec-2.3.9-core.jar\" HiveAesDecrypt <密钥> <输入文件> [输出文件]");
        System.out.println("  方式2 (交互模式): java -cp \".;hive-exec-2.3.9-core.jar\" HiveAesDecrypt <密钥>");
        System.out.println("\n参数说明:");
        System.out.println("  <密钥>      : 用于解密的密钥字符串 (必需)");
        System.out.println("  <输入文件>  : 包含加密数据的文本文件，每行一个Base64密文 (可选)");
        System.out.println("  [输出文件]  : 解密结果输出文件 (可选，不指定则只在控制台显示)");
        System.out.println("\n示例:");
        System.out.println("  # 批量解密并保存到文件");
        System.out.println("  java -cp \".;hive-exec-2.3.9-core.jar\" HiveAesDecrypt mykey123 data_jiami.txt result.txt");
        System.out.println("\n  # 批量解密只显示在控制台");
        System.out.println("  java -cp \".;hive-exec-2.3.9-core.jar\" HiveAesDecrypt mykey123 data_jiami.txt");
        System.out.println("\n  # 交互式解密");
        System.out.println("  java -cp \".;hive-exec-2.3.9-core.jar\" HiveAesDecrypt mykey123");
        System.out.println("\n注意: Linux/Mac 系统使用 ':' 分隔classpath");
        System.out.println("  java -cp \".:hive-exec-2.3.9-core.jar\" HiveAesDecrypt <参数>");
        System.out.println("========================================");
    }
    
    /**
     * 主函数
     */
    public static void main(String[] args) {
        // 检查参数
        if (args.length < 1) {
            printUsage();
            System.exit(1);
        }
        
        String secretKey = args[0];
        
        try {
            HiveAesDecrypt decryptor = new HiveAesDecrypt(secretKey);
            
            if (args.length >= 2) {
                // 批量解密模式
                String inputFile = args[1];
                String outputFile = args.length >= 3 ? args[2] : null;
                decryptor.decryptFromFile(inputFile, outputFile);
            } else {
                // 交互式模式
                decryptor.interactiveMode();
            }
            
        } catch (Exception e) {
            System.err.println("[错误] 初始化解密器失败: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}








