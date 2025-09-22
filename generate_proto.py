import os
import subprocess

def generate_proto_files():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    proto_dir = os.path.join(current_dir, 'app', 'proto_files')
    
    # Create proto_files directory if it doesn't exist
    os.makedirs(proto_dir, exist_ok=True)
    
    # Define the proto file path
    proto_file = os.path.join(proto_dir, 'property.proto')
    
    # Generate Python files from proto
    subprocess.run([
        'python', '-m', 'grpc_tools.protoc',
        f'--proto_path={proto_dir}',
        f'--python_out={proto_dir}',
        f'--grpc_python_out={proto_dir}',
        'property.proto'
    ], check=True)
    
    print("Proto files generated successfully!")

if __name__ == "__main__":
    generate_proto_files() 