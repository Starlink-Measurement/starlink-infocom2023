#!/usr/bin/env bash
cd instances
terraform init -input=false
terraform plan -out=tfplan -input=false

count=0
until terraform apply -input=false -auto-approve tfplan
do
    [ "$count" -lt "10" ] || kill -INT 0 # Kill process group
    echo "Failed to spin up instances. Trying again..."
    sleep 1
    ((count++))
done
