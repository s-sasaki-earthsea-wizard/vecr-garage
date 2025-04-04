FROM minio/minio:latest

# Create directory for sample files
RUN mkdir -p /tmp/sample_data

# Copy sample files
COPY sample_data /tmp/sample_data

# Copy and make executable the initialize script
COPY init.sh /init.sh
RUN chmod +x /init.sh

# Set working directory
WORKDIR /data

# Expose MinIO ports
EXPOSE 9000 9001

# Use ENTRYPOINT instead of CMD to ensure init.sh is executed
ENTRYPOINT ["/init.sh"]