import sys
import pandas as pd
import matplotlib.pyplot as plt

generated_code = sys.argv[1]

def generate_chart(generated_code):
    # Try executing the dynamically generated code if provided
    try:
        exec(generated_code)
        print("Custom code executed")
        file_path = "./public/custom_chart.png"
        plt.savefig(file_path)
        return file_path
    except Exception as e:
        print(f"Error in custom code: {str(e)}")
        return "./public/error.png"  # Provide an error image or alternative behavior

try:
    file_path = generate_chart(generated_code)
    print(file_path)
except Exception as e:
    print(f"Error: {str(e)}")