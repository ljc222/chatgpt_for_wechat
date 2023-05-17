#!/bin/bash

unset KUBECONFIG

cd .. && docker build -f docker/Dockerfile.latest \
             -t ljc222/chatgpt_for_wechat .

docker tag ljc222/chatgpt_for_wechat ljc222/chatgpt_for_wechat:$(date +%y%m%d)