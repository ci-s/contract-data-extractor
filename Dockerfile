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