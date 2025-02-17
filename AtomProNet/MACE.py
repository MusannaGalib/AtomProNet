import subprocess
import sys
import os

def install_mace():
    """
    Installs MACE, sets up the virtual environment, and installs all necessary dependencies.
    """
    # Ask user for installation folder
    install_folder = input("Enter the folder where MACE should be installed (default is current directory): ")
    if not install_folder:
        install_folder = os.getcwd()

    # Check if the folder exists, if not create it
    if not os.path.exists(install_folder):
        os.makedirs(install_folder)
    
    # Create the virtual environment
    venv_path = os.path.join(install_folder, "MACE")
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])

    # Activate the virtual environment using the appropriate script
    activate_venv_script = os.path.join(venv_path, "bin", "activate")
    
    # Check if activation script exists
    if not os.path.exists(activate_venv_script):
        print(f"Activation script not found at {activate_venv_script}")
        sys.exit(1)

    # Use subprocess to activate the environment and install packages
    print(f"Activating virtual environment at {venv_path}")
    activate_command = f"source {activate_venv_script} && "
    
    try:
        # Install ipykernel and other dependencies
        print("Installing ipykernel...")
        subprocess.check_call(activate_command + "pip install ipykernel", shell=True)

        # Install the necessary packages
        print("Installing required packages...")
        subprocess.check_call(activate_command + "pip install e3nn==0.4.4 opt_einsum ase torch_ema prettytable", shell=True)

        # Clone and install MACE
        print("Cloning and installing MACE...")
        subprocess.check_call(activate_command + "pip install git+https://github.com/ACEsuit/mace.git", shell=True)

        # Install the kernel for Jupyter
        print("Installing Jupyter kernel...")
        subprocess.check_call(activate_command + "python -m ipykernel install --user --name=ML_MACE --display-name=ML_MACE", shell=True)
        
        # List installed packages for confirmation
        print("Listing installed packages...")
        subprocess.check_call(activate_command + "pip list", shell=True)

        # Debug line to confirm installation
        print("Installation completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)


def run_mace_training():
    """
    Prompts user to provide file paths for training, testing, and validation datasets,
    and runs the MACE training script with the provided paths.
    """
    # Ask the user to provide paths to the dataset
    train_file = input("Enter the path to the training file: ")
    test_file = input("Enter the path to the test file: ")
    valid_file = input("Enter the path to the validation file: ")

    # Ask the user to review the YAML configuration
    print("Please review and make sure the paths for train, test, and validation datasets are correct in the following YAML config:")
    print(f"""
    --train_file="{train_file}"
    --test_file="{test_file}"
    --valid_file="{valid_file}"
    """)

    review = input("Do you want to proceed with the training (yes/no)? ").lower()
    if review == "yes":
        # Run the training script with the provided arguments
        train_command = f"""
        python3 ./mace/scripts/run_train.py \
        --name="MACE_alumina_model" \
        --model_dir="MACE_models" \
        --log_dir="MACE_models" \
        --checkpoints_dir="MACE_models" \
        --results_dir="MACE_models" \
        --train_file="{train_file}" \
        --test_file="{test_file}" \
        --valid_file="{valid_file}" \
        --E0s="{{13:-0.01623775, 8:-0.02536379}}" \
        --energy_key="REF_energy" \
        --forces_key="REF_forces" \
        --model="MACE" \
        --r_max=7.0 \
        --batch_size=1 \
        --valid_batch_size=1 \
        --max_num_epochs=150 \
        --num_interactions=2 \
        --num_channels=128 \
        --max_L=1 \
        --correlation=3 \
        --ema \
        --ema_decay=0.99 \
        --error_table='PerAtomRMSE' \
        --amsgrad \
        --default_dtype="float64" \
        --device=cuda \
        --seed=123 \
        --swa \
        --save_cpu \
        --restart_latest
        """

        # Execute the training command
        subprocess.check_call(train_command, shell=True)
        print("Training started successfully.")
    else:
        print("Training was not started. Exiting.")

def main():
    """
    Main function to guide the user through MACE installation and training.
    """
    # Ask if the user wants to install MACE
    install_option = input("Do you want to install MACE? (yes/no): ").lower()
    if install_option == "yes":
        install_mace()

    # Ask if the user wants to train a model
    train_option = input("Do you want to train a MACE model? (yes/no): ").lower()
    if train_option == "yes":
        run_mace_training()
    else:
        print("Exiting without training.")

if __name__ == "__main__":
    main()
