```python
# /home/ubuntu/pentest_project/collectors/harvester_collector.py
import subprocess
import json

class HarvesterCollector:
    def __init__(self, target):
        self.target = target
        self.raw_data = None

    def collect_data(self):
        """Executes theHarvester tool and collects its output."""
        try:
            # Assuming theHarvester is in PATH or provide full path
            # Basic command, can be expanded with more options
            command = [
                'theHarvester',
                '-d', self.target,
                '-b', 'all', # Search all available sources
                '-f', f'{self.target}_harvester_results.json', # Save results to a JSON file
                '-l', '500' # Limit results if necessary, adjust as needed
            ]
            # Using subprocess.run for better control and error handling
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            self.raw_data = self._read_json_output(f'{self.target}_harvester_results.json')
            return self.raw_data
        except FileNotFoundError:
            # Handle case where theHarvester is not installed or not in PATH
            print(f"Error: theHarvester tool not found. Please ensure it's installed and in your PATH.")
            self.raw_data = {"error": "theHarvester tool not found"}
            return None
        except subprocess.CalledProcessError as e:
            # Handle errors during theHarvester execution
            print(f"Error executing theHarvester: {e}")
            # Try to read partial results if any, otherwise set error
            try:
                self.raw_data = self._read_json_output(f'{self.target}_harvester_results.json')
            except:
                self.raw_data = {"error": f"theHarvester execution failed: {e.stderr}"}
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.raw_data = {"error": str(e)}
            return None

    def _read_json_output(self, file_path):
        """Reads and parses the JSON output file from theHarvester."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Error: Output file {file_path} not found.")
            return {"error": f"Output file {file_path} not found"}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {file_path}.")
            return {"error": f"Could not decode JSON from {file_path}"}

    def process_data(self):
        """Processes the raw JSON data from theHarvester."""
        if not self.raw_data or "error" in self.raw_data:
            return {"error": "No data to process or error in data collection."}

        processed_data = {
            'emails': self.raw_data.get('emails', []),
            'hosts': self.raw_data.get('hosts', []),
            'ips': self.raw_data.get('ips', []),
            'interesting_urls': self.raw_data.get('interesting_urls', [])
            # Add more fields as needed based on theHarvester's output structure
        }
        return processed_data

    def get_results(self):
        """Returns the processed data."""
        return self.process_data()

# Example Usage (for testing this module independently)
if __name__ == '__main__':
    # Replace 'example.com' with a domain you have permission to test
    target_domain = "example.com" 
    harvester = HarvesterCollector(target_domain)
    
    # Collect data (this will also save to a JSON file)
    raw_output = harvester.collect_data()
    if raw_output:
        print(f"Raw output from theHarvester for {target_domain}:")
        print(json.dumps(raw_output, indent=4))
        
        # Process the collected data
        processed_results = harvester.get_results()
        print(f"\nProcessed results for {target_domain}:")
        print(json.dumps(processed_results, indent=4))
    else:
        print(f"Failed to collect data for {target_domain}.")

```

This code defines the `HarvesterCollector` class, which encapsulates the logic for running theHarvester, collecting its output, and processing it into a structured format. It includes basic error handling for cases where theHarvester is not found or encounters an error during execution. The `if __name__ == '__main__':` block provides an example of how to use this class.

**Next Steps:**

1.  **Implement other collector classes:** Create similar classes for SpiderFoot and other OSINT tools you plan to integrate.
2.  **Develop the main orchestration logic:** Create a main script or module that uses these collector classes to gather information based on user input or predefined configurations.
3.  **Integrate with a data storage solution:** Decide how and where to store the collected data (e.g., in memory, JSON files, a database).
4.  **Build the analysis and reporting features:** Develop the logic to analyze the collected data, identify patterns, and generate reports.

Remember to handle API keys and sensitive information securely if your tools require them. Also, ensure you have permission to scan any targets you test against.```python
import os
import json
import subprocess

class HarvesterCollector:
    def __init__(self, target):
        self.target = target
        self.raw_data = None
        # Ensure the output directory exists
        self.output_dir = os.path.join(os.getcwd(), "harvester_results")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.output_file = os.path.join(self.output_dir, f"{self.target}_harvester_results.json")

    def collect_data(self):
        """Executes theHarvester tool and collects its output."""
        try:
            command = [
                'theHarvester',
                '-d', self.target,
                '-b', 'all', # Search all available sources
                '-f', self.output_file # Save results to a JSON file
                # '-l', '500' # Limit results if necessary, adjust as needed
            ]
            # Using subprocess.run for better control and error handling
            # Increased timeout to 600 seconds (10 minutes) as theHarvester can take time
            process = subprocess.run(command, capture_output=True, text=True, check=True, timeout=600)
            self.raw_data = self._read_json_output()
            return self.raw_data
        except FileNotFoundError:
            error_msg = f"Error: theHarvester tool not found. Please ensure it's installed and in your PATH."
            print(error_msg)
            self.raw_data = {"error": error_msg}
            return None
        except subprocess.TimeoutExpired:
            error_msg = f"Error: theHarvester timed out after 600 seconds for target {self.target}. Partial results might be available in {self.output_file}"
            print(error_msg)
            # Try to read partial results if any
            try:
                self.raw_data = self._read_json_output()
            except:
                self.raw_data = {"error": error_msg, "partial_data_error": "Could not read partial data."}
            return None # Or return partial data if available
        except subprocess.CalledProcessError as e:
            error_msg = f"Error executing theHarvester for {self.target}: {e.stderr}"
            print(error_msg)
            # Try to read partial results if any, as some modules might have succeeded before an error
            try:
                self.raw_data = self._read_json_output()
            except:
                self.raw_data = {"error": error_msg, "partial_data_error": "Could not read partial data after error."}
            return None # Or return partial data if available
        except Exception as e:
            error_msg = f"An unexpected error occurred while running theHarvester for {self.target}: {e}"
            print(error_msg)
            self.raw_data = {"error": str(e)}
            return None

    def _read_json_output(self):
        """Reads and parses the JSON output file from theHarvester."""
        try:
            with open(self.output_file, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            # This might happen if theHarvester failed before creating the file
            # Or if the file path is incorrect.
            error_msg = f"Error: Output file {self.output_file} not found."
            print(error_msg)
            # Return an empty dict or specific error structure if needed
            return {"error": error_msg, "data_sources_status": "File not found, likely due to earlier error."}
        except json.JSONDecodeError:
            error_msg = f"Error: Could not decode JSON from {self.output_file}. The file might be empty or corrupted."
            print(error_msg)
            # Attempt to read raw content if JSON decoding fails
            try:
                with open(self.output_file, 'r') as f:
                    raw_content = f.read()
                return {"error": error_msg, "raw_content": raw_content}
            except Exception as e_read:
                return {"error": error_msg, "raw_content_error": str(e_read)}

    def process_data(self):
        """Processes the raw JSON data from theHarvester."""
        if not self.raw_data or self.raw_data.get("error"):
            # If there was an error during collection or reading, return it
            return self.raw_data 

        # Initialize with empty lists to handle cases where keys might be missing
        processed_data = {
            'emails': self.raw_data.get('emails', []),
            'hosts': self.raw_data.get('hosts', []),
            'ips': self.raw_data.get('ips', []),
            'interesting_urls': self.raw_data.get('interesting_urls', []),
            'linkedin_people': self.raw_data.get('linkedin_people', []),
            'twitter_people': self.raw_data.get('twitter_people', []),
            'trello_urls': self.raw_data.get('trello_urls', []),
            # Add more fields as needed based on theHarvester's output structure
        }
        return processed_data

    def get_results(self):
        """Returns the processed data."""
        return self.process_data()

if __name__ == '__main__':
    # Example usage:
    target_domain = "example.com"  # Replace with a domain you have permission to test
    harvester_instance = HarvesterCollector(target_domain)
    
    print(f"Starting data collection for {target_domain}...")
    # Collect data (this will also save to a JSON file)
    # In a real application, you might want to handle the return value of collect_data()
    # to check if the collection was successful before processing.
    harvester_instance.collect_data()
    
    # Process the collected data
    # This will read from the file if it exists, or use in-memory data if available
    processed_results = harvester_instance.get_results()
    
    if processed_results and not processed_results.get("error"):
        print(f"\nProcessed results for {target_domain}:")
        print(json.dumps(processed_results, indent=4))
    else:
        print(f"\nFailed to get processed results for {target_domain}.")
        if processed_results and processed_results.get("error"):
            print(f"Error details: {processed_results['error']}")

    # You can also access the raw data if needed:
    # print("\nRaw data:")
    # print(json.dumps(harvester_instance.raw_data, indent=4))
```
