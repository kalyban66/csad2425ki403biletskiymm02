import unittest
import os
from coverage import Coverage  # Упевніться, що модуль coverage встановлено

class TestReportGenerator:
    @staticmethod
    def generate_report(results, coverage_percentage):
        total_tests = results.testsRun
        failed_tests = len(results.failures) + len(results.errors)
        passed_tests = total_tests - failed_tests

        with open("test_summary.txt", "w") as report_file:
            report_file.write(f"Total tests run: {total_tests}\n")
            report_file.write(f"Passed tests: {passed_tests}\n")
            report_file.write(f"Failed tests: {failed_tests}\n")
            report_file.write(f"Code coverage: {coverage_percentage:.2f}%\n")

def run_tests_with_report():
    # Ініціюємо покриття і вказуємо файл, для якого рахується покриття
    cov = Coverage(source=["main"])
    cov.start()

    # Завантажуємо і запускаємо тести з файлу test.py
    suite = unittest.defaultTestLoader.loadTestsFromName("test")
    runner = unittest.TextTestRunner(resultclass=unittest.TestResult)
    result = runner.run(suite)

    # Зупиняємо і зберігаємо покриття
    cov.stop()
    cov.save()
    coverage_percentage = cov.report()  # Отримуємо відсоток покриття коду

    # Генеруємо звіт
    TestReportGenerator.generate_report(result, coverage_percentage)

if __name__ == "__main__":
    run_tests_with_report()
