# =============================================================================
# InfraBuddy - AWS Lambda Containerfile / Dockerfile
# =============================================================================
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements / pyproject
WORKDIR ${LAMBDA_TASK_ROOT}

# Install dependencies
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install "fastapi>=0.111.0" \
                "mangum>=0.17.0" \
                "slack-bolt>=1.18.0" \
                "botbuilder-core>=4.16.0" \
                "boto3>=1.34.0" \
                "pydantic>=2.7.0" \
                "pydantic-settings>=2.2.0" \
                "python-dotenv>=1.0.0"

# Copy application files
COPY agent/ ${LAMBDA_TASK_ROOT}/agent/
COPY aws/ ${LAMBDA_TASK_ROOT}/aws/
COPY chatops/ ${LAMBDA_TASK_ROOT}/chatops/
COPY server.py ${LAMBDA_TASK_ROOT}/server.py
COPY main.py ${LAMBDA_TASK_ROOT}/main.py

# Lambda handler entry point
CMD [ "server.handler" ]
