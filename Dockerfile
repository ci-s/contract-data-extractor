FROM amazonlinux:latest

# Download Miniconda installer
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install Miniconda
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda

# Add Miniconda to PATH
ENV PATH="/miniconda/bin:${PATH}"

# Copy your environment file
COPY environment.yml .

# Create a new conda environment from your file
RUN conda env create -f environment.yml

# Activate the environment
SHELL ["conda", "run", "-n", "docker_env2", "/bin/bash", "-c"]

COPY final-project/ .

EXPOSE 5001
# Continue with your Dockerfile...