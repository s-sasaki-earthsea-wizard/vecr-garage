# description: AWS CLIのMakefile

# ------------------------------------------------------------
# Environment Check
# ------------------------------------------------------------

check-env: ## Check required AWS environment variables
	@if [ -z "$(AWS_PROFILE)" ]; then \
		echo "Error: AWS_PROFILE is not set"; \
		exit 1; \
	fi
	@if [ -z "$(PROJECT_NAME)" ]; then \
		echo "Error: PROJECT_NAME is not set"; \
		exit 1; \
	fi
	@if [ -z "$(AWS_ENVIRONMENT)" ]; then \
		echo "Error: AWS_ENVIRONMENT is not set"; \
		exit 1; \
	fi

# ------------------------------------------------------------
# Secrets Manager
# ------------------------------------------------------------

aws-secret-get: check-env ## Get a secret value by key. Usage: make secret-get KEY=key_name
	@if [ -z "$(KEY)" ]; then \
		echo "Error: KEY is required. Usage: make secret-get KEY=<key_name> [SECRET=lambda-secrets|app-secrets]"; \
		exit 1; \
	fi
	@SECRET_NAME=$${SECRET:-lambda-secrets}; \
	AWS_PROFILE=$(AWS_PROFILE) aws secretsmanager get-secret-value \
		--secret-id $(PROJECT_NAME)-$(AWS_ENVIRONMENT)-$$SECRET_NAME \
		--query 'SecretString' --output text | jq -r ".$(KEY)"

aws-secret-list: check-env ## List all secret keys. Usage: make secret-list [SECRET=lambda-secrets]
	@SECRET_NAME=$${SECRET:-lambda-secrets}; \
	echo "Keys in $(PROJECT_NAME)-$(AWS_ENVIRONMENT)-$$SECRET_NAME:"; \
	AWS_PROFILE=$(AWS_PROFILE) aws secretsmanager get-secret-value \
		--secret-id $(PROJECT_NAME)-$(AWS_ENVIRONMENT)-$$SECRET_NAME \
		--query 'SecretString' --output text | jq -r 'keys[]'

aws-secret-list-all: check-env ## List all secrets in Secrets Manager for this PROJECT_NAME
	@echo "Secrets for $(PROJECT_NAME)-$(AWS_ENVIRONMENT):"
	@AWS_PROFILE=$(AWS_PROFILE) aws secretsmanager list-secrets \
		--filter Key=name,Values=$(PROJECT_NAME)-$(AWS_ENVIRONMENT) \
		--query 'SecretList[].Name' --output text | tr '\t' '\n'
