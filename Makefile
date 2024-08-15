# Makefile

#################################################################################
# GLOBALS                                                                       #
#################################################################################
SHELL:=/bin/bash
python=python3
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
	@streamlit run src/streamlit_app.py


# Docker
build_image:
	@docker build . -t meteo_stats

run:
	@docker run \
	-v `pwd`/.streamlit:/app/.streamlit \
	-p 8080:8501 \
	-it \
	--rm \
	--init \
	meteo_stats

# Silencing commands
.SILENT: venv requirements clean
