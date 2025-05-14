#!/usr/bin/env python
"""
Visualize Locust load test results for presentations.
This script takes CSV files produced by Locust and generates charts for presentations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import argparse
from datetime import datetime

def setup_styling():
    """Setup plot styling for consistent visuals"""
    sns.set(style="whitegrid")
    plt.rcParams["figure.figsize"] = (12, 8)
    plt.rcParams["font.size"] = 12
    
def load_stats_history(file_path):
    """Load the stats_history.csv file into a DataFrame"""
    df = pd.read_csv(file_path)

    # Timestamp sütununu bul ve normalize et
    timestamp_col = None
    for col in df.columns:
        if col.lower() == 'timestamp':
            timestamp_col = col
            break
    
    if timestamp_col is None:
        raise KeyError("CSV dosyasında timestamp sütunu bulunamadı.")

    df['timestamp'] = pd.to_datetime(df[timestamp_col])

    return df

def generate_response_time_chart(df, output_dir, prefix):
    """Generate response time chart from stats_history data"""
    # Filter only for /chat endpoint
    chat_df = df[df['Name'] == '/chat']

    plt.figure()
    plt.plot(chat_df['timestamp'], chat_df['50%'], label='Median (50%)')
    plt.plot(chat_df['timestamp'], chat_df['95%'], label='95th Percentile')
    plt.plot(chat_df['timestamp'], chat_df['99%'], label='99th Percentile')

    plt.title('Response Time - /chat endpoint')
    plt.xlabel('Time')
    plt.ylabel('Response Time (ms)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_file = os.path.join(output_dir, f"{prefix}_response_times.png")
    plt.savefig(output_file, dpi=300)
    print(f"Saved response time chart to {output_file}")
    plt.close()

def generate_requests_per_second_chart(df, output_dir, prefix):
    """Generate requests per second chart from stats_history data"""
    # Group by timestamp and Name, then sum the requests
    rps_df = df.groupby(['timestamp', 'Name'])['Requests/s'].sum().reset_index()
    
    plt.figure()
    for name in rps_df['Name'].unique():
        data = rps_df[rps_df['Name'] == name]
        plt.plot(data['timestamp'], data['Requests/s'], label=name)
    
    plt.title('Requests Per Second')
    plt.xlabel('Time')
    plt.ylabel('Requests/s')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, f"{prefix}_requests_per_second.png")
    plt.savefig(output_file, dpi=300)
    print(f"Saved requests per second chart to {output_file}")
    plt.close()

def generate_users_chart(df, output_dir, prefix):
    """Generate users chart from stats_history data"""
    # Get user count over time
    users_df = df.drop_duplicates('timestamp')[['timestamp', 'User Count']]
    
    plt.figure()
    plt.plot(users_df['timestamp'], users_df['User Count'])
    
    plt.title('Number of Users')
    plt.xlabel('Time')
    plt.ylabel('Users')
    plt.grid(True)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, f"{prefix}_users.png")
    plt.savefig(output_file, dpi=300)
    print(f"Saved users chart to {output_file}")
    plt.close()

def generate_endpoint_comparison(df, output_dir, prefix):
    """Generate a bar chart comparing different endpoints"""
    # Aggregate data by endpoint
    endpoint_df = df.groupby('Name')['50%'].mean().reset_index()

    plt.figure()
    ax = sns.barplot(x='Name', y='50%', data=endpoint_df)

    # Add values on top of bars
    for i, v in enumerate(endpoint_df['50%']):
        ax.text(i, v + 5, f"{v:.1f}", ha='center')

    plt.title('Median Response Time by Endpoint')
    plt.xlabel('Endpoint')
    plt.ylabel('Median Response Time (ms)')
    plt.tight_layout()

    output_file = os.path.join(output_dir, f"{prefix}_endpoint_comparison.png")
    plt.savefig(output_file, dpi=300)
    print(f"Saved endpoint comparison chart to {output_file}")
    plt.close()

def process_test_results(test_file, output_dir):
    """Process a single test's stats_history.csv file"""
    if not os.path.exists(test_file):
        print(f"{test_file} not found, skipping...")
        return

    # Extract test name from file name
    test_name = os.path.basename(test_file).replace("_stats_history.csv", "")
    prefix = test_name

    # Load data
    print(f"Processing test results for {test_name}...")
    df = load_stats_history(test_file)

    # Generate charts
    generate_response_time_chart(df, output_dir, prefix)
    generate_requests_per_second_chart(df, output_dir, prefix)
    generate_users_chart(df, output_dir, prefix)
    generate_endpoint_comparison(df, output_dir, prefix)

def generate_comparison_chart(test_dirs, output_dir):
    """Generate a chart comparing multiple tests"""
    all_data = []
    
    for test_dir in test_dirs:
        stats_history_path = os.path.join(test_dir, "stats_history.csv")
        if not os.path.exists(stats_history_path):
            continue
            
        test_name = os.path.basename(test_dir).split("_stats")[0]
        df = load_stats_history(stats_history_path)
        
        # Filter for /chat endpoint and get average response times
        chat_df = df[df['Name'] == '/chat']
        if chat_df.empty:
            continue
            
        avg_response = chat_df['Average Response Time'].mean()
        median_response = chat_df['Median Response Time'].mean()
        p95_response = chat_df['95% Response Time'].mean()
        
        all_data.append({
            'Test': test_name,
            'Average': avg_response,
            'Median': median_response,
            '95th Percentile': p95_response
        })
    
    if not all_data:
        print("No valid data for comparison chart")
        return
        
    comparison_df = pd.DataFrame(all_data)
    
    # Plotting
    plt.figure(figsize=(14, 8))
    
    # Create grouped bar chart
    bar_width = 0.25
    x = range(len(comparison_df['Test']))
    
    plt.bar([i - bar_width for i in x], comparison_df['Average'], 
            width=bar_width, label='Average', color='skyblue')
    plt.bar(x, comparison_df['Median'], 
            width=bar_width, label='Median', color='lightgreen')
    plt.bar([i + bar_width for i in x], comparison_df['95th Percentile'], 
            width=bar_width, label='95th Percentile', color='salmon')
    
    plt.xlabel('Load Test')
    plt.ylabel('Response Time (ms)')
    plt.title('Response Time Comparison Across Tests')
    plt.xticks(x, comparison_df['Test'])
    plt.legend()
    
    # Add values on top of bars
    for i in x:
        plt.text(i - bar_width, comparison_df['Average'].iloc[i] + 5, 
                 f"{comparison_df['Average'].iloc[i]:.0f}", 
                 ha='center', va='bottom', fontsize=9)
        plt.text(i, comparison_df['Median'].iloc[i] + 5, 
                 f"{comparison_df['Median'].iloc[i]:.0f}", 
                 ha='center', va='bottom', fontsize=9)
        plt.text(i + bar_width, comparison_df['95th Percentile'].iloc[i] + 5, 
                 f"{comparison_df['95th Percentile'].iloc[i]:.0f}", 
                 ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, "test_comparison.png")
    plt.savefig(output_file, dpi=300)
    print(f"Saved test comparison chart to {output_file}")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Generate charts from Locust test results")
    parser.add_argument('--results-dir', default='load_test_reports',
                        help='Directory containing load test results')
    parser.add_argument('--output-dir', default='load_test_charts',
                        help='Directory to save charts')
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Setup plot styling
    setup_styling()

    # Find all stats_history.csv files directly
    csv_files = glob.glob(f"{args.results_dir}/*_stats_history.csv")

    if not csv_files:
        print(f"No test results found in {args.results_dir}")
        return

    # Process each CSV file directly
    for csv_file in csv_files:
        process_test_results(csv_file, args.output_dir)

    # Generate comparison chart
    generate_comparison_chart(csv_files, args.output_dir)

    print(f"All charts have been saved to {args.output_dir}")
    print("You can use these charts in your presentation to demonstrate the performance of your RAG chatbot")

if __name__ == "__main__":
    main() 