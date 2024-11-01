import streamlit as st
import pandas as pd
from pathlib import Path
from test_runner import TestRunner
from utils import scan_test_files, parse_test_commands
import time

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
        
        # Initialize session state
        if 'test_files' not in st.session_state:
            st.session_state.test_files = []
        if 'selected_tests' not in st.session_state:
            st.session_state.selected_tests = []
        if 'test_results' not in st.session_state:
            st.session_state.test_results = None

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
            st.subheader("Available Tests")
            
            test_commands = parse_test_commands(st.session_state.test_files)
            selected_tests = st.multiselect(
                "Select tests to run",
                options=test_commands,
                default=None,
                help="Choose one or more tests to execute"
            )
            st.session_state.selected_tests = selected_tests

            if st.button("Run Selected Tests", disabled=not selected_tests):
                self.run_tests()

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

    def render(self):
        self.render_header()
        self.render_directory_input()
        self.render_test_selection()

if __name__ == "__main__":
    app = JestTestUI()
    app.render()
