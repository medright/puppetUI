import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from test_runner import TestRunner
from utils import scan_test_files, parse_test_commands
from presets import PresetManager
import time
import random
from datetime import datetime, timedelta

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
        
        # Initialize session state
        if 'test_files' not in st.session_state:
            st.session_state.test_files = []
        if 'selected_tests' not in st.session_state:
            st.session_state.selected_tests = []
        if 'test_results' not in st.session_state:
            st.session_state.test_results = None
        if 'test_history' not in st.session_state:
            st.session_state.test_history = []
            # Add mock test history data
            self.add_mock_history_data()
        if 'presets' not in st.session_state:
            st.session_state.presets = self.preset_manager.load_presets()
        if 'preset_loaded' not in st.session_state:
            st.session_state.preset_loaded = False
        if 'selected_preset_name' not in st.session_state:
            st.session_state.selected_preset_name = None

    def add_mock_history_data(self):
        """Add mock test history data to demonstrate visualization features"""
        # Mock test names
        test_names = [
            "UserAuth.test.js",
            "api/endpoints.test.js",
            "components/Button.test.js",
            "utils/helpers.test.js"
        ]
        
        # Generate data for the last 7 days
        now = datetime.now()
        for days_ago in range(7, -1, -1):
            # Create 3 entries per day
            base_time = now - timedelta(days=days_ago)
            for hour in [9, 13, 17]:  # Morning, afternoon, evening
                timestamp = base_time.replace(hour=hour, minute=0, second=0)
                
                for test in test_names:
                    # Vary success rate over time
                    success_chance = 0.8  # Base 80% success rate
                    if days_ago > 5:  # Lower success rate in older entries
                        success_chance = 0.6
                    elif days_ago < 2:  # Higher success rate in recent entries
                        success_chance = 0.9
                    
                    # Random status based on success chance
                    status = '✅ PASS' if random.random() < success_chance else '❌ FAIL'
                    
                    # Vary duration based on test type and add some randomness
                    base_duration = {
                        'UserAuth.test.js': 2.5,
                        'api/endpoints.test.js': 1.8,
                        'components/Button.test.js': 0.9,
                        'utils/helpers.test.js': 0.5
                    }[test]
                    
                    # Add some random variation to duration
                    duration = base_duration + random.uniform(-0.2, 0.2)
                    
                    # Create history entry
                    history_entry = {
                        'timestamp': timestamp,
                        'test': test,
                        'status': status,
                        'duration': max(0.1, duration),  # Ensure duration is positive
                        'output': f"Mock output for {test} at {timestamp}"
                    }
                    st.session_state.test_history.append(history_entry)

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
                    st.success(f"Found {len(st.session_state.test_files)} test files!")

    def render_test_selection(self):
        if st.session_state.test_files:
            st.subheader("Test Selection")
            
            # Preset Selection
            st.markdown("### Preset Management")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                available_presets = list(st.session_state.presets.keys())
                if available_presets:
                    selected_preset = st.selectbox(
                        "Load from preset",
                        ["Select a preset..."] + available_presets,
                        help="Choose a saved preset to quickly load a group of tests"
                    )
                    st.markdown("""
                    ℹ️ **How to use presets:**
                    1. Select tests you want to save using the multi-select below
                    2. Enter a preset name and click 'Save as Preset'
                    3. Load your saved presets anytime using this dropdown
                    """)
                    
                    # Preview selected preset
                    if selected_preset != "Select a preset..." and selected_preset in st.session_state.presets:
                        st.markdown("#### 👀 Preset Preview")
                        st.markdown(f"**{selected_preset}** contains these tests:")
                        for test in st.session_state.presets[selected_preset]:
                            st.markdown(f"- `{test}`")
            
            with col2:
                if selected_preset != "Select a preset..." and selected_preset in st.session_state.presets:
                    if st.button("📥 Load Preset", type="primary"):
                        st.session_state.selected_tests = st.session_state.presets[selected_preset]
                        st.session_state.preset_loaded = True
                        st.session_state.selected_preset_name = selected_preset
            
            # Show success message when preset is loaded
            if st.session_state.preset_loaded and st.session_state.selected_preset_name:
                st.success(f"✨ Preset '{st.session_state.selected_preset_name}' loaded successfully!")
                # Reset the loaded flag
                st.session_state.preset_loaded = False
            
            # Test Selection
            test_commands = parse_test_commands(st.session_state.test_files)
            selected_tests = st.multiselect(
                "Select tests to run",
                options=test_commands,
                default=st.session_state.selected_tests,
                help="Choose one or more tests to execute"
            )
            st.session_state.selected_tests = selected_tests
            
            # Save Preset
            if selected_tests:
                col1, col2 = st.columns([3, 1])
                with col1:
                    preset_name = st.text_input(
                        "Save current selection as preset",
                        help="Enter a name for your preset to save the current test selection"
                    )
                with col2:
                    if preset_name and st.button("💾 Save as Preset"):
                        if self.preset_manager.add_preset(preset_name, selected_tests):
                            st.session_state.presets = self.preset_manager.load_presets()
                            st.success(f"✨ Preset '{preset_name}' saved successfully!")

            # Preset Management
            if st.session_state.presets:
                with st.expander("🔧 Manage Presets"):
                    preset_to_delete = st.selectbox(
                        "Select preset to delete",
                        ["Select a preset..."] + list(st.session_state.presets.keys())
                    )
                    if preset_to_delete != "Select a preset..." and st.button("🗑️ Delete Preset"):
                        if self.preset_manager.delete_preset(preset_to_delete):
                            st.session_state.presets = self.preset_manager.load_presets()
                            st.success(f"Preset '{preset_to_delete}' deleted!")

            if st.button("▶️ Run Selected Tests", disabled=not selected_tests):
                self.run_tests()

    def store_test_history(self, results):
        """Store test results in history with timestamp"""
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

        # Store results in history
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

            for result in results:
                with st.expander(f"Output: {result['Test']}"):
                    st.code(result['Output'])

    def render_test_history(self):
        if st.session_state.test_history:
            st.subheader("Test History")

            # Create DataFrame from history
            history_df = pd.DataFrame(st.session_state.test_history)
            
            # Success rate over time
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

            # Test duration trends
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

            # Test history table
            st.subheader("Recent Test Runs")
            recent_history = history_df.sort_values('timestamp', ascending=False).head(50)
            st.dataframe(
                recent_history[['timestamp', 'test', 'status', 'duration']],
                use_container_width=True
            )

    def render(self):
        self.render_header()
        self.render_directory_input()
        self.render_test_selection()
        self.render_test_history()

if __name__ == "__main__":
    app = JestTestUI()
    app.render()
