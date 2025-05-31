FROM python:3.10-slim

# 1) Instala todas las herramientas de sistema en un solo RUN
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      gcc \
      unzip \
      sudo \
      procps \
      curl \
      wget \
 && (apt-get install -y bpfcc-tools python3-bpfcc || echo "BPF tools not available") \
 && (apt-get install -y linux-perf || echo "linux-perf not available") \
 && rm -rf /var/lib/apt/lists/*

# 2) Try to create perf symlink if available
RUN which perf && ln -sf $(which perf) /usr/local/bin/perf || echo "perf not available, energy monitoring will use CPU estimation"

# 3) Python y tus deps
RUN pip install --upgrade pip && \
    pip install \
      Click tabulate six PyYAML pika tqdm tblib \
      requests paramiko cloudpickle ps-mem psutil \
      kubernetes boto3 numpy pandas flask

# 4) Prepara workspace y copia tu ZIP
WORKDIR /lithops
COPY lithops_k8s.zip .

# 5) Ahora sí, descomprime
RUN unzip lithops_k8s.zip && rm lithops_k8s.zip

# 6) Configura sudo para perf (si está disponible)
RUN echo "root ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# 7) Create a simple script to check energy monitoring capabilities
RUN echo '#!/bin/bash\n\
echo "=== Energy Monitoring Capability Check ==="\n\
echo "Perf available: $(which perf >/dev/null && echo "YES" || echo "NO")"\n\
echo "RAPL accessible: $(test -r /sys/class/powercap/intel-rapl:0/energy_uj 2>/dev/null && echo "YES" || echo "NO")"\n\
echo "CPU estimation: YES (always available)"\n\
echo "========================================"\n\
' > /usr/local/bin/check-energy && chmod +x /usr/local/bin/check-energy

CMD ["python"]
