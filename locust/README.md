# Load Testing with Locust

This directory contains configuration for load testing the RAG chatbot using [Locust](https://locust.io/).

## Prerequisites

- Python 3.10+
- Locust installed: `pip install locust`
- Required Python packages for visualization: `pip install pandas matplotlib seaborn`
- RAG chatbot API server running on `http://localhost:8000`

## Running Load Tests

### Interactive Web UI

Run the load test with an interactive web UI:

```bash
cd /path/to/scalable-llm-rag-chatbot
locust -f locust/locustfile.py --host=http://localhost:8000
```

This will start the Locust web UI at http://localhost:8089.

1. Open your browser and navigate to http://localhost:8089
2. Configure your test:
   - Number of users: Start with 10-20 for local testing
   - Spawn rate: 1-5 users per second
   - Host: http://localhost:8000 (if not set via command line)
3. Start the test and monitor results in real-time

### Automated Test Suite

For running a series of predefined tests and creating reports for all of them:

```bash
cd /path/to/scalable-llm-rag-chatbot
./locust/run_load_test.sh
```

This script will run multiple tests with different configurations:
- Light load: 5 users
- Medium load: 20 users
- Heavy load: 50 users
- Peak load: 100 users
- Endurance test: 20 users for 5 minutes

### Headless Mode

For running a single test in headless mode (no UI):

```bash
locust -f locust/locustfile.py --host=http://localhost:8000 --headless -u 20 -r 5 -t 1m --html=locust_report.html
```

Parameters:
- `-u`: Number of users to simulate
- `-r`: Spawn rate (users per second)
- `-t`: Test duration (e.g., 1m for 1 minute, 5m for 5 minutes)
- `--html`: Output file for HTML report

## Test Scenarios

The locustfile includes three types of tasks:

1. **ask_question** (Weight: 10) - Send queries with RAG enabled
2. **health_check** (Weight: 3) - Simple health endpoint checks
3. **ask_without_rag** (Weight: 1) - Send queries with RAG disabled

The locustfile is optimized to use questions that match predefined responses in the SimpleMLLService for efficient testing.

## Visualizing Results

After running the tests with the `run_load_test.sh` script, you can generate visualizations for your presentation:

```bash
cd /path/to/scalable-llm-rag-chatbot
python locust/visualize_results.py
```

This will:
1. Process all test results in the `load_test_reports` directory
2. Generate visualization charts in the `load_test_charts` directory
3. Create comparison charts showing performance across different load levels

You can customize the directories:

```bash
python locust/visualize_results.py --results-dir=custom_results --output-dir=custom_charts
```

## Understanding the Results

### Key Metrics

- **Response Time**: How long it takes for the API to respond to requests
  - Median: Shows the typical user experience
  - 95th/99th percentiles: Shows the experience of users during peak loads
  
- **Requests per Second (RPS)**: The throughput of your system
  - Higher is better, but should be balanced with acceptable response times
  
- **Failure Rate**: Percentage of failed requests
  - Lower is better; should be close to 0% in a well-functioning system

### Interpreting Results for Presentations

1. **System Capacity**: The maximum number of concurrent users your system can handle while maintaining acceptable response times (usually under 1000ms)

2. **Scalability**: How response times increase with user load
   - Linear increase: Good scalability
   - Exponential increase: Potential bottlenecks
   
3. **Bottlenecks**: Components that slow down first under load
   - CPU/memory usage
   - Database access
   - External API calls

4. **Optimization Opportunities**: Areas to focus on for improving performance

## Performance Comparison

Use the comparison charts to demonstrate how different configurations affect performance:

- RAG vs. non-RAG responses
- Effect of different database sizes
- Impact of adding Kubernetes horizontal scaling 