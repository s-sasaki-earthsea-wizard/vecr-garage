FROM minio/minio:latest

# Set working directory
WORKDIR /data

# Expose MinIO ports
EXPOSE 9000 9001

# Environment variables will be provided in docker-compose.yml

# Start MinIO server
ENTRYPOINT ["minio"]
CMD ["server", "/data", "--console-address", ":9001"]