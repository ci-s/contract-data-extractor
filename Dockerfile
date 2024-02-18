FROM vllm/vllm-openai:latest
# nvidia/cuda:12.3.1-runtime-ubuntu22.04 # works
# nvcr.io/nvidia/pytorch:24.01-py3
# amazonlinux:latest
# Update the package lists for upgrades and new package installations
RUN apt-get update

# Install curl
RUN apt-get install -y curl

# Download Miniconda installer
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install Miniconda
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda

# Add Miniconda to PATH
ENV PATH="/miniconda/bin:${PATH}"

# Copy your environment file
COPY environment_vllm3.yml .

# Create a new conda environment from your file
RUN conda env create -f environment_vllm3.yml

# Activate the environment
# SHELL ["conda", "run", "-n", "docker_env2", "/bin/bash", "-c"]
RUN echo "source /miniconda/etc/profile.d/conda.sh" >> ~/.bashrc

# Activate the environment
# SHELL ["/bin/bash", "-c"]
# RUN conda activate docker_env2


COPY data/ /data
COPY code/ /code
WORKDIR /code/serve
# CMD [ "python", "serve_vllm.py"]
RUN conda run -n docker_env2 python serve_vllm.py
# Starthere: thros error bc of no gpu. but gpu goes in with docker run command. do i need to do it elsewhere?
EXPOSE 5001
# ENTRYPOINT ["tail", "-f", "/dev/null"]
# Continue with your Dockerfile...