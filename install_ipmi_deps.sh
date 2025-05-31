#!/bin/bash
#
# (C) Copyright IBM Corp. 2020
# (C) Copyright Cloudlab URV 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# This script installs the dependencies required for the IPMI energy monitor.
# It installs the ipmitool package, which is used to communicate with the BMC
# (Baseboard Management Controller) to collect power consumption data.

set -e

echo "Installing IPMI dependencies..."

# Detect the Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
elif type lsb_release >/dev/null 2>&1; then
    OS=$(lsb_release -si)
    VER=$(lsb_release -sr)
else
    OS=$(uname -s)
    VER=$(uname -r)
fi

echo "Detected OS: $OS $VER"

# Install ipmitool based on the distribution
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    echo "Installing ipmitool on Ubuntu/Debian..."
    sudo apt-get update
    sudo apt-get install -y ipmitool
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Fedora"* ]]; then
    echo "Installing ipmitool on CentOS/RHEL/Fedora..."
    sudo yum install -y ipmitool
elif [[ "$OS" == *"SUSE"* ]]; then
    echo "Installing ipmitool on SUSE..."
    sudo zypper install -y ipmitool
elif [[ "$OS" == *"Alpine"* ]]; then
    echo "Installing ipmitool on Alpine..."
    sudo apk add ipmitool
else
    echo "Unsupported OS: $OS"
    echo "Please install ipmitool manually."
    exit 1
fi

# Check if ipmitool was installed successfully
if command -v ipmitool >/dev/null 2>&1; then
    echo "ipmitool installed successfully!"
    echo "Version: $(ipmitool -V)"
else
    echo "Failed to install ipmitool. Please install it manually."
    exit 1
fi

# Test if IPMI is available on the system
echo "Testing IPMI functionality..."
if sudo ipmitool chassis status >/dev/null 2>&1; then
    echo "IPMI is working correctly!"
else
    echo "IPMI test failed. This could be because:"
    echo "1. The system does not have a BMC (Baseboard Management Controller)"
    echo "2. The BMC is not configured correctly"
    echo "3. You don't have sufficient permissions"
    echo ""
    echo "The IPMI monitor will still work, but it will generate placeholder data."
    echo "To use IPMI with a remote server, configure the following options:"
    echo "  ipmi_host: IP address of the remote server"
    echo "  ipmi_username: IPMI username"
    echo "  ipmi_password: IPMI password"
fi

echo ""
echo "Installation complete!"
echo "You can now use the IPMI energy monitor in Lithops."
echo "See examples/energy_monitoring/README_IPMI.md for usage instructions."
