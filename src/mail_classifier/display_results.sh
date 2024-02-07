#!/usr/bin/env bash
cd /mnt/c/wsl_shared/enron
echo -e "These are the performance metrics:\n"
cat result_metrics.json | jq
echo -e "\n"
echo -e "These are the important variables:\n"
cat feature_importance.json | jq
echo -e "\n"

exit 0
