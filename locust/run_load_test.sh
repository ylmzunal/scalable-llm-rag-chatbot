#!/bin/bash
# Run load tests with different scenarios and generate reports

# Create reports directory if it doesn't exist
mkdir -p load_test_reports

# Make sure API server is running
echo "Ensure the API server is running at http://localhost:8000"
echo "Press Enter to continue or Ctrl+C to abort"
read

# Function to run a load test
run_load_test() {
    local users=$1
    local spawn_rate=$2
    local duration=$3
    local name=$4
    
    echo "Running load test: $name with $users users, spawn rate $spawn_rate, duration $duration"
    
    locust -f locust/locustfile.py \
        --host=http://localhost:8000 \
        --headless \
        -u $users \
        -r $spawn_rate \
        -t $duration \
        --html=load_test_reports/${name}.html \
        --csv=load_test_reports/${name} \
        --csv-full-history
        
    echo "Test complete: $name. Report saved to load_test_reports/${name}.html"
    echo ""
}

# Run tests with increasing load
echo "=== Starting Load Tests ==="

# Light load - 5 users
run_load_test 5 1 "1m" "light_load"

# Medium load - 20 users
run_load_test 20 5 "1m" "medium_load"

# Heavy load - 50 users
run_load_test 50 10 "1m" "heavy_load"

# Peak load - 100 users
run_load_test 100 20 "1m" "peak_load"

# Endurance test - 20 users for 5 minutes
run_load_test 20 5 "5m" "endurance_test"

echo "=== All Load Tests Completed ==="
echo "Reports are available in the load_test_reports directory"