# syntax=docker/dockerfile:1.0.0-experimental
FROM oriolmac/compss-extract:3.3-amd

# Copy the entire TASKA-C directory
COPY TASKA-C /TASKA-C

# Use build secrets to handle sensitive files and install dependencies
RUN --mount=type=secret,id=kubeconfig,dst=/tmp/.kube/config \
    --mount=type=secret,id=lithopsconfig,dst=/tmp/.lithops/config \
    mkdir -p /root/.kube /root/.lithops && \
    cp /tmp/.kube/config /root/.kube/config && \
    cp /tmp/.lithops/config /root/.lithops/config && \
    cd /TASKA-C && \
    python3 -m pip install -r requirements.txt && \
    python3 -m pip install kubernetes && \
    python3 -m pip install .
