#!/bin/bash
# Script to install eBPF dependencies for Lithops energy monitoring

echo "Installing eBPF dependencies..."

# Update package lists
sudo apt-get update

# Install BCC (BPF Compiler Collection)
sudo apt-get install -y bpfcc-tools python3-bpfcc

# Install additional dependencies
sudo apt-get install -y linux-headers-$(uname -r)
sudo apt-get install -y libbpf-dev

# Install BCC Python package in the current Python environment
echo "Installing BCC Python package..."
pip install bcc || sudo pip install bcc

# Check if we're in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual environment detected: $VIRTUAL_ENV"
    echo "Installing BCC in the virtual environment..."
    pip install bcc
fi

echo "Checking BCC installation..."
python3 -c "import bcc; print('BCC is installed successfully')" || echo "BCC installation failed"

echo "Checking kernel support for eBPF..."
grep BPF /boot/config-$(uname -r) | grep -E 'CONFIG_BPF=|CONFIG_BPF_SYSCALL='

echo "Testing simple BPF program..."
sudo python3 -c "from bcc import BPF; BPF(text='int kprobe__sys_clone(void *ctx) { return 0; }'); print('BPF works')" || echo "BPF test failed"

echo "Installation complete. You can now run Lithops with both energy monitors."
