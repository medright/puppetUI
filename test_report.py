import json
import pandas as pd
from datetime import datetime
from pathlib import Path

class TestReportExporter:
    def __init__(self):
        self.reports_dir = Path("test_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def generate_filename(self, prefix: str, extension: str) -> str:
        """Generate a unique filename for the report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
        
    def export_current_results(self, results: list, format: str = "json") -> str:
        """Export current test results to specified format"""
        if not results:
            return None
            
        filename = self.generate_filename("test_results", format)
        filepath = self.reports_dir / filename
        
        if format == "json":
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        elif format == "csv":
            df = pd.DataFrame(results)
            df.to_csv(filepath, index=False)
            
        return str(filepath)
        
    def export_test_history(self, history: list, format: str = "json") -> str:
        """Export test history to specified format"""
        if not history:
            return None
            
        filename = self.generate_filename("test_history", format)
        filepath = self.reports_dir / filename
        
        if format == "json":
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=2, default=str)
        elif format == "csv":
            df = pd.DataFrame(history)
            df.to_csv(filepath, index=False)
            
        return str(filepath)
        
    def generate_summary_report(self, results: list, history: list) -> str:
        """Generate a detailed summary report in Markdown format"""
        if not results or not history:
            return None
            
        filename = self.generate_filename("test_summary", "md")
        filepath = self.reports_dir / filename
        
        current_results_df = pd.DataFrame(results)
        history_df = pd.DataFrame(history)
        
        # Calculate statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['Status'] == '✅ PASS')
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        avg_duration = current_results_df['Duration'].str.replace('s', '').astype(float).mean()
        
        with open(filepath, 'w') as f:
            f.write("# Jest Test Execution Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary Statistics\n\n")
            f.write(f"- Total Tests Executed: {total_tests}\n")
            f.write(f"- Tests Passed: {passed_tests}\n")
            f.write(f"- Tests Failed: {total_tests - passed_tests}\n")
            f.write(f"- Success Rate: {success_rate:.2f}%\n")
            f.write(f"- Average Duration: {avg_duration:.2f}s\n\n")
            
            f.write("## Test Results\n\n")
            f.write("| Test | Status | Duration |\n")
            f.write("|------|--------|----------|\n")
            for _, row in current_results_df.iterrows():
                f.write(f"| {row['Test']} | {row['Status']} | {row['Duration']} |\n")
            
            f.write("\n## Detailed Test Outputs\n\n")
            for result in results:
                f.write(f"### {result['Test']}\n")
                f.write("```\n")
                f.write(result['Output'])
                f.write("\n```\n\n")
        
        return str(filepath)
