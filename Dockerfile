# syntax=docker/dockerfile:1
# 開発用：CPU/GPU 両対応イメージ
# PyTorch 公式イメージベース
FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-devel

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=1000

# システムパッケージ（opencv が必要とする libGL 系を含む）
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    vim \
    sudo \
    openssh-client \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

WORKDIR /app

USER $USERNAME

ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

COPY --chown=$USERNAME:$USER_GID requirements-dev.txt setup.py setup.cfg README.md LICENSE ./

RUN --mount=type=cache,target=/home/$USERNAME/.cache/pip,uid=$USER_UID,gid=$USER_GID \
    pip install --upgrade pip \
    && pip install -r requirements-dev.txt

COPY --chown=$USERNAME:$USER_GID . .

RUN pip install -e .

CMD ["/bin/bash"]
