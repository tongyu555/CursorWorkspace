#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hive AES 解密工具
支持解密使用 Hive GenericUDFAesEncrypt 加密的数据
"""

import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


def prepare_key(key_string: str, key_length: int = 128) -> bytes:
    """
    准备AES密钥
    
    Hive的实现:
    - 如果密钥长度不足,使用SHA-256哈希后截取
    - 支持128, 192, 256位密钥
    
    参数:
        key_string: 原始密钥字符串
        key_length: 密钥长度(位), 可选 128, 192, 256
    
    返回:
        bytes: 处理后的密钥
    """
    key_bytes = key_string.encode('utf-8')
    
    # 根据密钥长度要求调整
    if key_length == 128:
        required_length = 16  # 128位 = 16字节
    elif key_length == 192:
        required_length = 24  # 192位 = 24字节
    elif key_length == 256:
        required_length = 32  # 256位 = 32字节
    else:
        raise ValueError(f"不支持的密钥长度: {key_length}")
    
    # 如果密钥长度不够,使用SHA-256哈希
    if len(key_bytes) < required_length:
        hashed = hashlib.sha256(key_bytes).digest()
        return hashed[:required_length]
    
    # 如果密钥长度足够,直接截取
    return key_bytes[:required_length]


def aes_decrypt_ecb(ciphertext_base64: str, key_string: str, key_length: int = 128) -> str:
    """
    AES-ECB模式解密 (Hive默认模式)
    
    参数:
        ciphertext_base64: Base64编码的密文
        key_string: 密钥字符串
        key_length: 密钥长度(位)
    
    返回:
        str: 解密后的明文
    """
    try:
        # 1. Base64解码
        ciphertext_bytes = base64.b64decode(ciphertext_base64)
        
        # 2. 准备密钥
        key = prepare_key(key_string, key_length)
        
        # 3. 创建AES-ECB解密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.ECB(),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # 4. 解密
        decrypted_padded = decryptor.update(ciphertext_bytes) + decryptor.finalize()
        
        # 5. 移除PKCS7填充 (等同于Java的PKCS5Padding)
        unpadder = padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        # 6. 转换为UTF-8字符串
        return plaintext_bytes.decode('utf-8')
        
    except base64.binascii.Error:
        return "[错误] Base64格式不正确"
    except ValueError as e:
        return f"[错误] 解密失败 - 可能是密钥错误或数据损坏: {e}"
    except UnicodeDecodeError:
        return "[错误] UTF-8解码失败 - 解密结果不是有效的文本"
    except Exception as e:
        return f"[错误] 未知异常: {e}"


def aes_decrypt_cbc(ciphertext_base64: str, key_string: str, iv_string: str = None, key_length: int = 128) -> str:
    """
    AES-CBC模式解密
    
    参数:
        ciphertext_base64: Base64编码的密文
        key_string: 密钥字符串
        iv_string: 初始化向量(IV)字符串,如果为None则使用全零IV
        key_length: 密钥长度(位)
    
    返回:
        str: 解密后的明文
    """
    try:
        # 1. Base64解码
        ciphertext_bytes = base64.b64decode(ciphertext_base64)
        
        # 2. 准备密钥
        key = prepare_key(key_string, key_length)
        
        # 3. 准备IV (16字节)
        if iv_string is None:
            iv = b'\x00' * 16  # 默认全零IV
        else:
            iv_bytes = iv_string.encode('utf-8')
            if len(iv_bytes) < 16:
                iv = hashlib.md5(iv_bytes).digest()
            else:
                iv = iv_bytes[:16]
        
        # 4. 创建AES-CBC解密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # 5. 解密
        decrypted_padded = decryptor.update(ciphertext_bytes) + decryptor.finalize()
        
        # 6. 移除PKCS7填充
        unpadder = padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        # 7. 转换为UTF-8字符串
        return plaintext_bytes.decode('utf-8')
        
    except Exception as e:
        return f"[错误] 解密失败: {e}"


def batch_decrypt(ciphertext_list: list, key_string: str, mode: str = 'ECB', iv_string: str = None, key_length: int = 128) -> list:
    """
    批量解密
    
    参数:
        ciphertext_list: Base64编码的密文列表
        key_string: 密钥字符串
        mode: 加密模式 ('ECB' 或 'CBC')
        iv_string: IV字符串(仅CBC模式需要)
        key_length: 密钥长度(位)
    
    返回:
        list: 解密结果列表
    """
    results = []
    mode_upper = mode.upper()
    
    for idx, ciphertext in enumerate(ciphertext_list, 1):
        print(f"正在解密第 {idx}/{len(ciphertext_list)} 条数据...")
        
        if mode_upper == 'ECB':
            result = aes_decrypt_ecb(ciphertext, key_string, key_length)
        elif mode_upper == 'CBC':
            result = aes_decrypt_cbc(ciphertext, key_string, iv_string, key_length)
        else:
            result = f"[错误] 不支持的模式: {mode}"
        
        results.append(result)
    
    return results


def interactive_mode():
    """交互式解密模式"""
    print("=" * 60)
    print("Hive AES 解密工具")
    print("=" * 60)
    
    # 选择模式
    print("\n请选择加密模式:")
    print("1. ECB模式 (Hive默认, 推荐)")
    print("2. CBC模式")
    
    mode_choice = input("请输入选项 (1或2, 默认1): ").strip() or "1"
    mode = 'ECB' if mode_choice == '1' else 'CBC'
    
    # 选择密钥长度
    print("\n请选择密钥长度:")
    print("1. 128位 (Hive默认, 推荐)")
    print("2. 192位")
    print("3. 256位")
    
    key_choice = input("请输入选项 (1/2/3, 默认1): ").strip() or "1"
    key_length_map = {'1': 128, '2': 192, '3': 256}
    key_length = key_length_map.get(key_choice, 128)
    
    # 输入密钥
    key_string = input("\n请输入密钥: ").strip()
    if not key_string:
        print("[错误] 密钥不能为空!")
        return
    
    # 如果是CBC模式,询问IV
    iv_string = None
    if mode == 'CBC':
        iv_input = input("请输入IV (留空使用全零IV): ").strip()
        iv_string = iv_input if iv_input else None
    
    # 选择单条或批量解密
    print("\n请选择解密方式:")
    print("1. 单条解密")
    print("2. 批量解密")
    
    decrypt_choice = input("请输入选项 (1或2, 默认1): ").strip() or "1"
    
    if decrypt_choice == '1':
        # 单条解密
        ciphertext = input("\n请输入Base64编码的密文: ").strip()
        if not ciphertext:
            print("[错误] 密文不能为空!")
            return
        
        print("\n" + "=" * 60)
        print("解密中...")
        print("=" * 60)
        
        if mode == 'ECB':
            result = aes_decrypt_ecb(ciphertext, key_string, key_length)
        else:
            result = aes_decrypt_cbc(ciphertext, key_string, iv_string, key_length)
        
        print(f"\n【解密结果】")
        print(f"模式: AES-{mode}")
        print(f"密钥长度: {key_length}位")
        print(f"密文: {ciphertext}")
        print(f"明文: {result}")
        
    else:
        # 批量解密
        print("\n请输入密文列表 (每行一个, 输入空行结束):")
        ciphertext_list = []
        while True:
            line = input().strip()
            if not line:
                break
            ciphertext_list.append(line)
        
        if not ciphertext_list:
            print("[错误] 密文列表不能为空!")
            return
        
        print("\n" + "=" * 60)
        print(f"开始批量解密 (共 {len(ciphertext_list)} 条)...")
        print("=" * 60)
        
        results = batch_decrypt(ciphertext_list, key_string, mode, iv_string, key_length)
        
        print("\n【批量解密结果】")
        print(f"模式: AES-{mode}")
        print(f"密钥长度: {key_length}位")
        print("-" * 60)
        for idx, (cipher, plain) in enumerate(zip(ciphertext_list, results), 1):
            print(f"\n第 {idx} 条:")
            print(f"  密文: {cipher}")
            print(f"  明文: {plain}")
    
    print("\n" + "=" * 60)
    print("解密完成!")
    print("=" * 60)


# ==================== 使用示例 ====================

def example_usage():
    """使用示例"""
    print("\n" + "=" * 60)
    print("代码调用示例")
    print("=" * 60)
    
    # 示例1: ECB模式解密
    print("\n【示例1: ECB模式解密】")
    key = "mySecretKey123"
    ciphertext = "YourBase64EncodedCiphertext"  # 替换为实际的密文
    
    print(f"密钥: {key}")
    print(f"密文: {ciphertext}")
    
    # 解密
    plaintext = aes_decrypt_ecb(ciphertext, key)
    print(f"明文: {plaintext}")
    
    # 示例2: CBC模式解密
    print("\n【示例2: CBC模式解密】")
    iv = "myInitVector16b"  # IV通常是16字节
    plaintext_cbc = aes_decrypt_cbc(ciphertext, key, iv)
    print(f"明文: {plaintext_cbc}")
    
    # 示例3: 批量解密
    print("\n【示例3: 批量解密】")
    ciphertext_list = [
        "ciphertext1",
        "ciphertext2",
        "ciphertext3"
    ]
    results = batch_decrypt(ciphertext_list, key, mode='ECB')
    for idx, result in enumerate(results, 1):
        print(f"  {idx}. {result}")


if __name__ == "__main__":
    # 运行交互式模式
    interactive_mode()
    
    # 如果需要查看代码示例,取消下面这行的注释
    # example_usage()








