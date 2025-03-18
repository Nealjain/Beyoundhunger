import os
import subprocess
import sys

def generate_requirements():
    print("Generating requirements.txt file...")
    try:
        # Activate virtual environment if it exists
        if os.path.exists('.venv'):
            if sys.platform == 'win32':
                pip_cmd = ['.venv\\Scripts\\pip', 'freeze']
            else:
                pip_cmd = ['.venv/bin/pip', 'freeze']
        else:
            pip_cmd = ['pip', 'freeze']
        
        # Run pip freeze command
        result = subprocess.run(pip_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error generating requirements: {result.stderr}")
            return
        
        # Write output to requirements.txt
        with open('requirements_full.txt', 'w') as f:
            f.write(result.stdout)
            
        print("Successfully generated requirements_full.txt")
        print("You can review and merge it with your existing requirements.txt file.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    generate_requirements() 