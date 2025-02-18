#!/bin/bash

# AWS Batch job submission script
set -e

# Configuration parameters
JOB_NAME="ControlM_Triggered_Job_$(date +%Y%m%d%H%M%S)"
JOB_QUEUE="your-batch-job-queue"          # Replace with your queue name
JOB_DEFINITION="your-job-definition"      # Replace with your job definition name
PARAMETERS='{"param1":"value1","param2":"value2"}'  # Optional parameters

# Submit job to AWS Batch
echo "Submitting AWS Batch job: ${JOB_NAME}"
response=$(aws batch submit-job \
    --job-name "${JOB_NAME}" \
    --job-queue "${JOB_QUEUE}" \
    --job-definition "${JOB_DEFINITION}" \
    --parameters "${PARAMETERS}")

# Extract important information from response
jobId=$(echo $response | jq -r '.jobId')
echo "Submitted Batch Job ID: ${jobId}"

# Optional: Wait for completion (remove if not needed)
echo "Waiting for job completion..."
aws batch wait jobs-terminated --jobs "${jobId}"

# Get final status
status=$(aws batch describe-jobs --jobs "${jobId}" | jq -r '.jobs[].status')
echo "Job ${jobId} finished with status: ${status}"

# Exit with appropriate code
if [ "$status" = "SUCCEEDED" ]; then
    exit 0
else
    exit 1
fi
