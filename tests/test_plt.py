import unittest
from faerskit.plt import plot_dca


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)
        # # 获取测试集的真实标签
        y_true = [0, 1, 1, 0, 1, 0, 1, 1, 0, 1]
        # # 获取测试集的预测概率
        y_pred = [0.1, 0.9, 0.8, 0.2, 0.7, 0.3, 0.6, 0.5, 0.4, 0.3]
        plot_dca(y_true, y_pred, 'test.png')


if __name__ == '__main__':
    unittest.main()
