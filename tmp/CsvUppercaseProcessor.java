package com.example.nifi.processor;

import com.example.nifi.utils.CsvUtils;
import org.apache.nifi.annotation.behavior.*;
import org.apache.nifi.annotation.documentation.*;
import org.apache.nifi.annotation.lifecycle.*;
import org.apache.nifi.components.*;
import org.apache.nifi.flowfile.FlowFile;
import org.apache.nifi.processor.*;
import org.apache.nifi.processor.exception.ProcessException;
import org.apache.nifi.processor.util.StandardValidators;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

/**
 * CSV 列名转大写处理器
 * 
 * 该处理器读取 CSV 文件，将列名转换为大写，并输出处理后的文件。
 */
@Tags({"csv", "uppercase", "header", "transform", "example"})
@CapabilityDescription("将 CSV 文件的列标题转换为大写字母。处理后的文件将包含新的列标题。")
@ReadsAttributes({
    @ReadsAttribute(attribute = "filename", description = "文件名属性，用于日志记录"),
    @ReadsAttribute(attribute = "mime.type", description = "文件的 MIME 类型")
})
@WritesAttributes({
    @WritesAttribute(attribute = "csv.row.count", description = "CSV 文件中的数据行数"),
    @WritesAttribute(attribute = "csv.header.count", description = "CSV 文件的列数"),
    @WritesAttribute(attribute = "processed.time", description = "处理完成的时间戳"),
    @WritesAttribute(attribute = "processor.name", description = "处理器名称")
})
@InputRequirement(InputRequirement.Requirement.INPUT_REQUIRED)
@SideEffectFree
@SupportsBatching
public class CsvUppercaseProcessor extends AbstractProcessor {
    
    // ========== 关系定义 ==========
    public static final Relationship SUCCESS = new Relationship.Builder()
            .name("success")
            .description("CSV 文件成功处理并转换后的输出")
            .build();
    
    public static final Relationship FAILURE = new Relationship.Builder()
            .name("failure")
            .description("CSV 文件处理失败时的输出")
            .build();
    
    public static final Relationship ORIGINAL = new Relationship.Builder()
            .name("original")
            .description("原始 CSV 文件（当选择保留原始文件时）")
            .build();
    
    private Set<Relationship> relationships;
    
    // ========== 属性定义 ==========
    public static final PropertyDescriptor CHARACTER_ENCODING = new PropertyDescriptor.Builder()
            .name("Character Encoding")
            .displayName("字符编码")
            .description("CSV 文件的字符编码格式")
            .required(true)
            .defaultValue("UTF-8")
            .addValidator(StandardValidators.CHARACTER_SET_VALIDATOR)
            .build();
    
    public static final PropertyDescriptor KEEP_ORIGINAL = new PropertyDescriptor.Builder()
            .name("Keep Original File")
            .displayName("保留原始文件")
            .description("是否保留原始文件副本")
            .required(true)
            .defaultValue("false")
            .allowableValues("true", "false")
            .addValidator(StandardValidators.BOOLEAN_VALIDATOR)
            .build();
    
    public static final PropertyDescriptor DELIMITER = new PropertyDescriptor.Builder()
            .name("CSV Delimiter")
            .displayName("CSV 分隔符")
            .description("CSV 文件使用的分隔符")
            .required(true)
            .defaultValue(",")
            .addValidator(StandardValidators.NON_EMPTY_VALIDATOR)
            .build();
    
    private List<PropertyDescriptor> properties;
    
    // ========== 统计计数器 ==========
    private AtomicLong filesProcessed = new AtomicLong(0);
    private AtomicLong rowsProcessed = new AtomicLong(0);
    
    // ========== 初始化方法 ==========
    @Override
    protected void init(final ProcessorInitializationContext context) {
        getLogger().info("初始化 CSV Uppercase Processor...");
        
        // 初始化关系集合
        final Set<Relationship> relationshipSet = new HashSet<>();
        relationshipSet.add(SUCCESS);
        relationshipSet.add(FAILURE);
        relationshipSet.add(ORIGINAL);
        this.relationships = Collections.unmodifiableSet(relationshipSet);
        
        // 初始化属性列表
        final List<PropertyDescriptor> propertyList = new ArrayList<>();
        propertyList.add(CHARACTER_ENCODING);
        propertyList.add(KEEP_ORIGINAL);
        propertyList.add(DELIMITER);
        this.properties = Collections.unmodifiableList(propertyList);
        
        getLogger().info("CSV Uppercase Processor 初始化完成");
    }
    
    // ========== 生命周期方法 ==========
    @OnScheduled
    public void onScheduled(final ProcessContext context) {
        getLogger().info("处理器调度开始，重置计数器");
        filesProcessed.set(0);
        rowsProcessed.set(0);
    }
    
    @OnStopped
    public void onStopped(final ProcessContext context) {
        getLogger().info("处理器停止，共处理 {} 个文件，{} 行数据", 
            filesProcessed.get(), rowsProcessed.get());
    }
    
    // ========== 核心处理逻辑 ==========
    @Override
    public void onTrigger(ProcessContext context, ProcessSession session) throws ProcessException {
        FlowFile flowFile = session.get();
        if (flowFile == null) {
            return;
        }
        
        final String filename = flowFile.getAttribute("filename");
        final boolean keepOriginal = context.getProperty(KEEP_ORIGINAL).asBoolean();
        
        getLogger().debug("开始处理文件: {}", new Object[]{filename});
        
        // 克隆原始文件（如果需要保留）
        FlowFile originalCopy = null;
        if (keepOriginal) {
            originalCopy = session.clone(flowFile);
            getLogger().debug("已克隆原始文件副本");
        }
        
        try {
            // 读取属性
            final String encoding = context.getProperty(CHARACTER_ENCODING).getValue();
            final String delimiter = context.getProperty(DELIMITER).getValue();
            
            // 读取 FlowFile 内容到字节数组
            final ByteArrayOutputStream contentBuffer = new ByteArrayOutputStream();
            session.read(flowFile, inputStream -> {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    contentBuffer.write(buffer, 0, bytesRead);
                }
            });
            final byte[] contentBytes = contentBuffer.toByteArray();
            
            // 处理 CSV 文件
            final ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            final List<String> newHeaders;
            
            try (ByteArrayInputStream inputStream = new ByteArrayInputStream(contentBytes)) {
                // 调用工具类处理 CSV
                newHeaders = CsvUtils.convertHeadersToUppercase(inputStream, outputStream);
            }
            
            // 计算行数（使用新的输入流）
            final long rowCount;
            try (ByteArrayInputStream inputStream = new ByteArrayInputStream(contentBytes)) {
                rowCount = CsvUtils.countRows(inputStream);
            }
            rowsProcessed.addAndGet(rowCount);
            
            // 添加处理属性
            Map<String, String> attributes = new HashMap<>();
            attributes.put("csv.row.count", String.valueOf(rowCount));
            attributes.put("csv.header.count", String.valueOf(newHeaders.size()));
            attributes.put("processed.time", String.valueOf(System.currentTimeMillis()));
            attributes.put("processor.name", "CsvUppercaseProcessor");
            attributes.put("csv.delimiter", delimiter);
            attributes.put("csv.encoding", encoding);
            
            // 写入处理后的内容
            flowFile = session.write(flowFile, out -> {
                out.write(outputStream.toByteArray());
            });
            
            // 更新属性
            flowFile = session.putAllAttributes(flowFile, attributes);
            
            // 记录成功
            filesProcessed.incrementAndGet();
            getLogger().info("成功处理文件: {}，共 {} 行，{} 列", 
                new Object[]{filename, rowCount, newHeaders.size()});
            
            // 传输到成功关系
            session.transfer(flowFile, SUCCESS);
            
            // 传输原始文件副本
            if (originalCopy != null) {
                session.transfer(originalCopy, ORIGINAL);
            }
            
        } catch (Exception e) {
            getLogger().error("处理文件失败: {}", new Object[]{filename}, e);
            
            // 移除未使用的克隆副本（避免资源泄露）
            if (originalCopy != null) {
                session.remove(originalCopy);
            }
            
            // 记录失败属性
            flowFile = session.putAttribute(flowFile, "error.message", 
                e.getMessage() != null ? e.getMessage() : "Unknown error");
            flowFile = session.putAttribute(flowFile, "error.class", e.getClass().getName());
            
            // 传输到失败关系
            session.transfer(flowFile, FAILURE);
        }
    }
    
    // ========== 处理器信息方法 ==========
    @Override
    public Set<Relationship> getRelationships() {
        return this.relationships;
    }
    
    @Override
    protected List<PropertyDescriptor> getSupportedPropertyDescriptors() {
        return this.properties;
    }
    
    // ========== 自定义验证方法 ==========
    @Override
    protected Collection<ValidationResult> customValidate(ValidationContext context) {
        final List<ValidationResult> results = new ArrayList<>();
        
        // 检查分隔符长度
        String delimiter = context.getProperty(DELIMITER).getValue();
        if (delimiter.length() > 1) {
            results.add(new ValidationResult.Builder()
                    .subject(DELIMITER.getName())
                    .valid(false)
                    .explanation("分隔符只能是单个字符")
                    .build());
        }
        
        return results;
    }
    
    // ========== 获取处理器描述 ==========
    @Override
    public String toString() {
        return "CSV Uppercase Processor";
    }
}