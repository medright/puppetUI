import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from test_runner import TestRunner
from utils import scan_test_files, parse_test_commands
from presets import PresetManager
from test_report import TestReportExporter
import time
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Jest Test Runner",
    page_icon="🧪",
    layout="wide"
)

# Custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

class JestTestUI:
    def __init__(self):
        self.test_runner = TestRunner()
        self.preset_manager = PresetManager()
        self.report_exporter = TestReportExporter()
        
        # Initialize session state
        if 'test_files' not in st.session_state:
            st.session_state.test_files = []
        if 'test_commands' not in st.session_state:
            st.session_state.test_commands = []
        if 'selected_tests' not in st.session_state:
            st.session_state.selected_tests = []
        if 'test_results' not in st.session_state:
            st.session_state.test_results = None
        if 'test_history' not in st.session_state:
            st.session_state.test_history = []
            self.add_mock_history_data()
        if 'presets' not in st.session_state:
            st.session_state.presets = self.preset_manager.load_presets()
        if 'preset_loaded' not in st.session_state:
            st.session_state.preset_loaded = False
        if 'selected_preset_name' not in st.session_state:
            st.session_state.selected_preset_name = None

    def render_header(self):
        st.title("🧪 Jest Test Runner")
        st.markdown("Execute and monitor your Jest tests with ease.")

    def render_directory_input(self):
        col1, col2 = st.columns([3, 1])
        with col1:
            directory = st.text_input(
                "Project Directory",
                value=str(Path.cwd()),
                help="Enter the path to your project directory containing Jest tests"
            )
        with col2:
            if st.button("Scan Directory", type="primary"):
                with st.spinner("Scanning for test files..."):
                    st.session_state.test_files = scan_test_files(directory)
                    st.session_state.test_commands = parse_test_commands(st.session_state.test_files)
                    st.success(f"Found {len(st.session_state.test_files)} test files!")

    def render_preset_management(self):
        st.header("📋 Test Presets")
        st.markdown("""
        Save and load your frequently used test combinations for quick access. 
        Presets help you maintain consistent test runs across your development workflow.
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            available_presets = list(st.session_state.presets.keys())
            if available_presets:
                selected_preset = st.selectbox(
                    "📥 Load a Preset",
                    ["Select a preset..."] + available_presets,
                    help="Choose a saved preset to quickly load a group of tests"
                )
                
                if selected_preset != "Select a preset..." and selected_preset in st.session_state.presets:
                    st.markdown("#### 👀 Preset Contents")
                    for test in st.session_state.presets[selected_preset]:
                        st.markdown(f"- `{test}`")
                    
                    if st.button("📥 Load Selected Preset", type="primary", key="load_preset"):
                        st.session_state.selected_tests = st.session_state.presets[selected_preset]
                        st.session_state.preset_loaded = True
                        st.session_state.selected_preset_name = selected_preset
        
        with col2:
            st.markdown("### Save New Preset")
            if st.session_state.selected_tests:
                preset_name = st.text_input(
                    "New Preset Name",
                    help="Enter a name for your new preset"
                )
                if preset_name and st.button("💾 Save Current Selection", type="primary"):
                    if self.preset_manager.add_preset(preset_name, st.session_state.selected_tests):
                        st.session_state.presets = self.preset_manager.load_presets()
                        st.success(f"✨ Preset '{preset_name}' saved successfully!")
            else:
                st.info("Select tests below to create a new preset")

        if st.session_state.preset_loaded and st.session_state.selected_preset_name:
            st.success(f"✨ Preset '{st.session_state.selected_preset_name}' loaded successfully!")
            st.session_state.preset_loaded = False

        if st.session_state.presets:
            with st.expander("🔧 Manage Existing Presets"):
                preset_to_delete = st.selectbox(
                    "Select preset to delete",
                    ["Select a preset..."] + list(st.session_state.presets.keys()),
                    key="delete_preset"
                )
                if preset_to_delete != "Select a preset..." and st.button("🗑️ Delete Preset", type="secondary"):
                    if self.preset_manager.delete_preset(preset_to_delete):
                        st.session_state.presets = self.preset_manager.load_presets()
                        st.success(f"Preset '{preset_to_delete}' deleted!")

        st.markdown("---")

    def run_single_test(self, test_pattern: str):
        with st.spinner(f"Running test: {test_pattern}"):
            start_time = time.time()
            success, output = self.test_runner.run_test(test_pattern)
            duration = round(time.time() - start_time, 2)

            result = {
                'Test': test_pattern,
                'Status': '✅ PASS' if success else '❌ FAIL',
                'Duration': f'{duration}s',
                'Output': output
            }

            self.store_test_history([result])
            self.display_results([result], st.empty())

    def render_test_selection(self):
        if st.session_state.test_files:
            st.header("🎯 Test Selection")
            
            # Group tests by file
            test_files = {}
            for cmd in st.session_state.test_commands:
                if cmd['file'] not in test_files:
                    test_files[cmd['file']] = []
                test_files[cmd['file']].append(cmd)

            # Display tests grouped by file
            for file_path, commands in test_files.items():
                with st.expander(f"📄 {file_path}", expanded=True):
                    file_command = next(cmd for cmd in commands if cmd['type'] == 'file')
                    
                    # File-level controls
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.checkbox(
                            "Select all tests in file",
                            value=file_command['pattern'] in st.session_state.selected_tests,
                            key=f"select_all_{file_path}",
                            on_change=self.handle_file_selection,
                            args=(file_command['pattern'], commands)
                        )
                    with col2:
                        st.button(
                            "▶️ Run File",
                            key=f"run_file_{file_path}",
                            on_click=self.run_single_test,
                            args=(file_command['pattern'],)
                        )

                    # Individual test controls
                    for cmd in commands:
                        if cmd['type'] == 'test':
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.checkbox(
                                    cmd['name'],
                                    value=cmd['pattern'] in st.session_state.selected_tests,
                                    key=f"test_{cmd['pattern']}",
                                    on_change=self.handle_test_selection,
                                    args=(cmd['pattern'],)
                                )
                            with col2:
                                st.button(
                                    "▶️ Run",
                                    key=f"run_test_{cmd['pattern']}",
                                    on_click=self.run_single_test,
                                    args=(cmd['pattern'],)
                                )

            if st.session_state.selected_tests:
                st.button("▶️ Run Selected Tests", on_click=self.run_tests, type="primary")

    def handle_file_selection(self, file_pattern: str, commands: list):
        is_selected = file_pattern in st.session_state.selected_tests
        
        if is_selected:
            st.session_state.selected_tests = [
                test for test in st.session_state.selected_tests
                if not any(cmd['pattern'] == test for cmd in commands)
            ]
        else:
            st.session_state.selected_tests.extend(
                cmd['pattern'] for cmd in commands
                if cmd['pattern'] not in st.session_state.selected_tests
            )

    def handle_test_selection(self, test_pattern: str):
        if test_pattern in st.session_state.selected_tests:
            st.session_state.selected_tests.remove(test_pattern)
        else:
            st.session_state.selected_tests.append(test_pattern)

    def add_mock_history_data(self):
        test_names = [
            "UserAuth.test.js",
            "api/endpoints.test.js",
            "components/Button.test.js",
            "utils/helpers.test.js"
        ]
        
        now = datetime.now()
        for days_ago in range(7, -1, -1):
            base_time = now - timedelta(days=days_ago)
            for hour in [9, 13, 17]:
                timestamp = base_time.replace(hour=hour, minute=0, second=0)
                
                for test in test_names:
                    success_chance = 0.8
                    if days_ago > 5:
                        success_chance = 0.6
                    elif days_ago < 2:
                        success_chance = 0.9
                    
                    status = '✅ PASS' if random.random() < success_chance else '❌ FAIL'
                    
                    base_duration = {
                        'UserAuth.test.js': 2.5,
                        'api/endpoints.test.js': 1.8,
                        'components/Button.test.js': 0.9,
                        'utils/helpers.test.js': 0.5
                    }[test]
                    
                    duration = base_duration + random.uniform(-0.2, 0.2)
                    
                    history_entry = {
                        'timestamp': timestamp,
                        'test': test,
                        'status': status,
                        'duration': max(0.1, duration),
                        'output': f"Mock output for {test} at {timestamp}"
                    }
                    st.session_state.test_history.append(history_entry)

    def store_test_history(self, results):
        timestamp = datetime.now()
        for result in results:
            history_entry = {
                'timestamp': timestamp,
                'test': result['Test'],
                'status': result['Status'],
                'duration': float(result['Duration'].replace('s', '')),
                'output': result['Output']
            }
            st.session_state.test_history.append(history_entry)

    def run_tests(self):
        if not st.session_state.selected_tests:
            st.warning("Please select at least one test to run")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()

        total_tests = len(st.session_state.selected_tests)
        results = []

        for idx, test in enumerate(st.session_state.selected_tests, 1):
            status_text.text(f"Running test {idx}/{total_tests}: {test}")
            
            start_time = time.time()
            success, output = self.test_runner.run_test(test)
            duration = round(time.time() - start_time, 2)

            results.append({
                'Test': test,
                'Status': '✅ PASS' if success else '❌ FAIL',
                'Duration': f'{duration}s',
                'Output': output
            })

            progress_bar.progress(idx / total_tests)

        self.store_test_history(results)
        self.display_results(results, results_container)

    def display_results(self, results, container):
        with container:
            st.subheader("Test Results")
            
            df = pd.DataFrame(results)
            st.dataframe(
                df[['Test', 'Status', 'Duration']],
                use_container_width=True
            )

            st.subheader("Export Results")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export Results as CSV"):
                    filepath = self.report_exporter.export_current_results(results, "csv")
                    st.success(f"Results exported to: {filepath}")
                    
            with col2:
                if st.button("📋 Export Results as JSON"):
                    filepath = self.report_exporter.export_current_results(results, "json")
                    st.success(f"Results exported to: {filepath}")
                    
            with col3:
                if st.button("📝 Generate Detailed Report"):
                    filepath = self.report_exporter.generate_summary_report(
                        results, 
                        st.session_state.test_history
                    )
                    st.success(f"Detailed report generated at: {filepath}")

            for result in results:
                with st.expander(f"Output: {result['Test']}"):
                    st.code(result['Output'])

    def render_test_history(self):
        if st.session_state.test_history:
            st.subheader("Test History")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Export History as CSV"):
                    filepath = self.report_exporter.export_test_history(
                        st.session_state.test_history, 
                        "csv"
                    )
                    st.success(f"History exported to: {filepath}")
                    
            with col2:
                if st.button("📋 Export History as JSON"):
                    filepath = self.report_exporter.export_test_history(
                        st.session_state.test_history, 
                        "json"
                    )
                    st.success(f"History exported to: {filepath}")

            history_df = pd.DataFrame(st.session_state.test_history)
            
            st.subheader("Test Success Rate Over Time")
            success_rate = history_df.groupby('timestamp', group_keys=False).apply(
                lambda x: (x['status'] == '✅ PASS').mean() * 100
            ).reset_index()
            success_rate.columns = ['timestamp', 'success_rate']
            
            fig_success = px.line(
                success_rate,
                x='timestamp',
                y='success_rate',
                title='Test Success Rate Trend',
                labels={'success_rate': 'Success Rate (%)', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig_success, use_container_width=True)

            st.subheader("Test Duration Trends")
            duration_df = history_df.groupby(['test', 'timestamp'])['duration'].mean().reset_index()
            fig_duration = px.line(
                duration_df,
                x='timestamp',
                y='duration',
                color='test',
                title='Test Duration Trends',
                labels={'duration': 'Duration (s)', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig_duration, use_container_width=True)

            st.subheader("Recent Test Runs")
            recent_history = history_df.sort_values('timestamp', ascending=False).head(50)
            st.dataframe(
                recent_history[['timestamp', 'test', 'status', 'duration']],
                use_container_width=True
            )

    def render(self):
        self.render_header()
        self.render_directory_input()
        self.render_preset_management()
        self.render_test_selection()
        self.render_test_history()

if __name__ == "__main__":
    app = JestTestUI()
    app.render()