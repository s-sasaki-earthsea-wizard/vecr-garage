# ============================================================
# VECR Garage - CI/CD Runner Service
# コード品質チェックとフォーマット専用コンテナ
# ============================================================

FROM python:3.11-slim

# 作業ディレクトリ設定
WORKDIR /workspace

# 必要なシステムパッケージのインストール
RUN apt-get update && apt-get install -y \
    git \
    libatomic1 \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Git safe directory設定（Dockerコンテナ内での実行用）
RUN git config --global --add safe.directory /workspace

# Makefile lint（checkmake）
RUN curl -sSfL https://github.com/mrtazz/checkmake/releases/download/0.2.2/checkmake-0.2.2.linux.amd64 \
    -o /usr/local/bin/checkmake && \
    chmod +x /usr/local/bin/checkmake

# JavaScript/CSS lint・format（ESLint + Prettier）
RUN npm install -g \
    eslint@8.57.0 \
    prettier@3.2.5 \
    @eslint/js@8.57.0 \
    && npm cache clean --force

# Python CI/CDツールのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip && \
    rm requirements.txt

# スクリプトディレクトリをコピー
COPY scripts/ /ci-scripts/
RUN chmod +x /ci-scripts/*.sh

# デフォルトコマンド
CMD ["/bin/bash"]
