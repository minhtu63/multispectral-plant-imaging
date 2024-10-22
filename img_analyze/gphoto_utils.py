import subprocess
import os
import sys
sys.path.append('/home/tu/.local/lib/python3.6/site-packages')
sys.path.append('/usr/local/lib/python3.6/dist-packages')
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/usr/lib/python3.6/dist-packages')
class GPhotoUtils:
    def run_gphoto2_command(self, command):
        """Run a gphoto2 command using subprocess."""
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            return result.stdout

    def list_folders(self):
        """List all folders in the camera's storage."""
        command = ["gphoto2", "--list-folders", "--folder", "/store_00010001/DCIM"]
        output = self.run_gphoto2_command(command)
        folders = []
        if output:
            for line in output.splitlines():
                if line.startswith(""):
                    parts = line.split()
                    if len(parts) > 1:
                        folder_name = parts[-1].split("/")[-1]
                        if folder_name.isdigit():
                            folders.append(int(folder_name))
        return folders

    def list_files_in_folder(self, folder_number):
        """List all files in a specific folder on the camera."""
        folder_path = f"/store_00010001/DCIM/{folder_number:04d}"
        command = ["gphoto2", "--list-files", "--folder", folder_path]
        output = self.run_gphoto2_command(command)
        files = []
        if output:
            for line in output.splitlines():
                if line.startswith("#"):
                    parts = line.split()
                    if len(parts) > 1:
                        file_number = parts[0][1:]  # remove leading '#'
                        file_name = parts[1]  # get the file name
                        files.append((file_number, file_name))
        return files

    def download_file(self, folder_number, file_number, file_name, destination):
        """Download a specific file from a specific folder on the camera to the destination."""
        folder_path = f"/store_00010001/DCIM/{folder_number:04d}"
        command = ["gphoto2", "--get-file", file_number, "--folder", folder_path, "--filename", os.path.join(destination, file_name)]
        self.run_gphoto2_command(command)

    def download_folder(self, folder_number, destination):
        """Download all files from a specific folder on the camera to the destination."""
        files = self.list_files_in_folder(folder_number)
        folder_destination = os.path.join(destination, f"{folder_number:04d}")
        os.makedirs(folder_destination, exist_ok=True)
        for file_number, file_name in files:
            self.download_file(folder_number, file_number, file_name, folder_destination)

    def download_images(self, destination):
        """Main function to download images from the camera to the destination."""
        # Ensure the destination directory exists
        os.makedirs(destination, exist_ok=True)
        
        # List all folders and find the highest number
        folders = self.list_folders()
        if not folders:
            print("No folders found.")
            return
        
        highest_folder = max(folders)
        start_folder = highest_folder - 3
        
        # Download images from folders with the highest number label to highest number label minus 4
        for i in range(start_folder, highest_folder + 1):
            self.download_folder(i, destination)
