#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hive AES 加密解密测试脚本
用于验证加密和解密功能是否正常工作
"""

import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import hashlib

from hive_aes_decrypt import aes_decrypt_ecb, prepare_key


def aes_encrypt_ecb(plaintext: str, key_string: str, key_length: int = 128) -> str:
    """
    AES-ECB模式加密(用于测试)
    
    参数:
        plaintext: 明文字符串
        key_string: 密钥字符串
        key_length: 密钥长度(位)
    
    返回:
        str: Base64编码的密文
    """
    # 1. 转换为字节
    plaintext_bytes = plaintext.encode('utf-8')
    
    # 2. 准备密钥
    key = prepare_key(key_string, key_length)
    
    # 3. 添加PKCS7填充
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext_bytes) + padder.finalize()
    
    # 4. 创建AES-ECB加密器
    cipher = Cipher(
        algorithms.AES(key),
        modes.ECB(),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # 5. 加密
    ciphertext_bytes = encryptor.update(padded_data) + encryptor.finalize()
    
    # 6. Base64编码
    ciphertext_base64 = base64.b64encode(ciphertext_bytes).decode('utf-8')
    
    return ciphertext_base64


def test_basic_encryption_decryption():
    """测试基本的加密解密功能"""
    print("=" * 60)
    print("测试1: 基本加密解密功能")
    print("=" * 60)
    
    # 测试数据
    test_cases = [
        ("Hello World", "mykey123"),
        ("中文测试", "密钥123456"),
        ("12345678", "testkey"),
        ("user@example.com", "secretkey999"),
        ("特殊字符!@#$%^&*()", "complexKey@2024"),
    ]
    
    success_count = 0
    
    for idx, (plaintext, key) in enumerate(test_cases, 1):
        print(f"\n测试用例 {idx}:")
        print(f"  原始明文: {plaintext}")
        print(f"  密钥: {key}")
        
        # 加密
        ciphertext = aes_encrypt_ecb(plaintext, key)
        print(f"  密文: {ciphertext}")
        
        # 解密
        decrypted = aes_decrypt_ecb(ciphertext, key)
        print(f"  解密结果: {decrypted}")
        
        # 验证
        if decrypted == plaintext:
            print(f"  ✓ 成功")
            success_count += 1
        else:
            print(f"  ✗ 失败")
    
    print(f"\n通过率: {success_count}/{len(test_cases)}")
    print("=" * 60)


def test_different_key_lengths():
    """测试不同密钥长度"""
    print("\n" + "=" * 60)
    print("测试2: 不同密钥长度")
    print("=" * 60)
    
    plaintext = "测试数据"
    key = "mySecretKey"
    
    key_lengths = [128, 192, 256]
    
    for key_len in key_lengths:
        print(f"\n密钥长度: {key_len}位")
        
        # 加密
        ciphertext = aes_encrypt_ecb(plaintext, key, key_len)
        print(f"  密文: {ciphertext}")
        
        # 解密
        decrypted = aes_decrypt_ecb(ciphertext, key, key_len)
        print(f"  解密结果: {decrypted}")
        
        # 验证
        if decrypted == plaintext:
            print(f"  ✓ 成功")
        else:
            print(f"  ✗ 失败")
    
    print("=" * 60)


def test_wrong_key():
    """测试错误的密钥"""
    print("\n" + "=" * 60)
    print("测试3: 错误密钥处理")
    print("=" * 60)
    
    plaintext = "敏感数据"
    correct_key = "correctKey123"
    wrong_key = "wrongKey456"
    
    print(f"明文: {plaintext}")
    print(f"正确密钥: {correct_key}")
    
    # 使用正确密钥加密
    ciphertext = aes_encrypt_ecb(plaintext, correct_key)
    print(f"密文: {ciphertext}")
    
    # 使用正确密钥解密
    print(f"\n使用正确密钥解密:")
    decrypted_correct = aes_decrypt_ecb(ciphertext, correct_key)
    print(f"  结果: {decrypted_correct}")
    if decrypted_correct == plaintext:
        print(f"  ✓ 成功")
    
    # 使用错误密钥解密
    print(f"\n使用错误密钥({wrong_key})解密:")
    decrypted_wrong = aes_decrypt_ecb(ciphertext, wrong_key)
    print(f"  结果: {decrypted_wrong}")
    if "[错误]" in decrypted_wrong:
        print(f"  ✓ 正确识别错误密钥")
    
    print("=" * 60)


def test_key_derivation():
    """测试密钥派生"""
    print("\n" + "=" * 60)
    print("测试4: 密钥派生机制")
    print("=" * 60)
    
    test_keys = [
        "short",           # 短密钥
        "1234567890123456",  # 正好16字节
        "this_is_a_very_long_key_string_that_needs_to_be_truncated",  # 长密钥
    ]
    
    for key_str in test_keys:
        print(f"\n原始密钥: {key_str} (长度: {len(key_str)}字节)")
        
        for key_len in [128, 192, 256]:
            derived_key = prepare_key(key_str, key_len)
            print(f"  {key_len}位派生密钥: {derived_key.hex()} (长度: {len(derived_key)}字节)")
    
    print("=" * 60)


def test_empty_and_special_cases():
    """测试空值和特殊情况"""
    print("\n" + "=" * 60)
    print("测试5: 特殊情况处理")
    print("=" * 60)
    
    key = "testkey123"
    
    # 测试空字符串
    print("\n测试空字符串:")
    empty_encrypted = aes_encrypt_ecb("", key)
    print(f"  空字符串密文: {empty_encrypted}")
    empty_decrypted = aes_decrypt_ecb(empty_encrypted, key)
    print(f"  解密结果: '{empty_decrypted}'")
    if empty_decrypted == "":
        print(f"  ✓ 成功")
    
    # 测试单个字符
    print("\n测试单个字符:")
    single_char = "A"
    single_encrypted = aes_encrypt_ecb(single_char, key)
    print(f"  密文: {single_encrypted}")
    single_decrypted = aes_decrypt_ecb(single_encrypted, key)
    print(f"  解密结果: '{single_decrypted}'")
    if single_decrypted == single_char:
        print(f"  ✓ 成功")
    
    # 测试长文本
    print("\n测试长文本:")
    long_text = "这是一段很长的文本" * 100
    long_encrypted = aes_encrypt_ecb(long_text, key)
    print(f"  原文长度: {len(long_text)}字符")
    print(f"  密文长度: {len(long_encrypted)}字符")
    long_decrypted = aes_decrypt_ecb(long_encrypted, key)
    if long_decrypted == long_text:
        print(f"  ✓ 成功")
    else:
        print(f"  ✗ 失败")
    
    # 测试无效的Base64
    print("\n测试无效的Base64:")
    invalid_result = aes_decrypt_ecb("This is not valid base64!!!", key)
    print(f"  结果: {invalid_result}")
    if "[错误]" in invalid_result:
        print(f"  ✓ 正确处理无效输入")
    
    print("=" * 60)


def generate_test_data():
    """生成测试数据供Hive使用"""
    print("\n" + "=" * 60)
    print("生成Hive测试数据")
    print("=" * 60)
    
    key = "hiveTestKey123"
    
    test_data = [
        "用户A",
        "user@example.com",
        "13800138000",
        "敏感信息123",
        "special!@#$%chars",
    ]
    
    print(f"\n密钥: {key}")
    print("\n可以在Hive中使用以下SQL验证:")
    print("-" * 60)
    print("CREATE TEMPORARY FUNCTION aes_decrypt AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesDecrypt';")
    print()
    
    for idx, data in enumerate(test_data, 1):
        encrypted = aes_encrypt_ecb(data, key)
        print(f"\n-- 测试数据{idx}: {data}")
        print(f"SELECT aes_decrypt('{encrypted}', '{key}');")
        print(f"-- 期望结果: {data}")
        print(f"-- Python加密结果: {encrypted}")
    
    print("\n" + "=" * 60)


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "Hive AES 加密解密测试套件" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        # 运行所有测试
        test_basic_encryption_decryption()
        test_different_key_lengths()
        test_wrong_key()
        test_key_derivation()
        test_empty_and_special_cases()
        generate_test_data()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()








