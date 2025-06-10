import unittest
import sys
import os
from datetime import datetime

def run_all_tests():
    """运行所有测试用例"""
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    
    # 获取测试目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern="test_*.py")
    
    # 创建测试运行器
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 运行测试
    print(f"\n开始运行测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    result = runner.run(suite)
    
    print("\n测试结果统计:")
    print("-" * 40)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        print("-" * 40)
        for failure in result.failures:
            print(f"\n{failure[0]}")
            print(failure[1])
    
    if result.errors:
        print("\n错误的测试:")
        print("-" * 40)
        for error in result.errors:
            print(f"\n{error[0]}")
            print(error[1])
    
    return len(result.failures) + len(result.errors)

def run_specific_test(test_file):
    """运行特定的测试文件"""
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    
    # 获取测试目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(test_dir, test_file)
    
    if not os.path.exists(test_file_path):
        print(f"错误: 测试文件 {test_file} 不存在")
        return 1
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=test_file)
    
    # 创建测试运行器
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 运行测试
    print(f"\n开始运行测试 {test_file} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    result = runner.run(suite)
    
    print("\n测试结果统计:")
    print("-" * 40)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        print("-" * 40)
        for failure in result.failures:
            print(f"\n{failure[0]}")
            print(failure[1])
    
    if result.errors:
        print("\n错误的测试:")
        print("-" * 40)
        for error in result.errors:
            print(f"\n{error[0]}")
            print(error[1])
    
    return len(result.failures) + len(result.errors)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行特定的测试文件
        test_file = sys.argv[1]
        sys.exit(run_specific_test(test_file))
    else:
        # 运行所有测试
        sys.exit(run_all_tests()) 