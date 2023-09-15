# Makefile

#################################################################################
# GLOBALS                                                                       #
#################################################################################
SHELL:=/bin/bash
python=python3.10
BIN=venv/bin/

all: requirements

#################################################################################
# COMMANDS                                                                      #
#################################################################################

# Create a virtual environment.
venv:
	echo ">>> Create environment..."
	$(python) -m venv venv
	echo ">>> Environment successfully created!"

# Delete the virtual environment.
clean:
	rm -rf venv

# Install Python dependencies.
requirements: venv
	echo ">>> Installing requirements..."
	$(BIN)python -m pip install --upgrade pip wheel
	$(BIN)python -m pip install -r requirements.txt

# Run streamlit application
st:

	cd notebooks
	@streamlit run streamlit_app.py --theme.primaryColor="#2c71de" --theme.backgroundColor="#678fd2" --theme.secondaryBackgroundColor="#767a96" --theme.textColor="#dfe4ea"

# Silencing commands
.SILENT: venv requirements clean
