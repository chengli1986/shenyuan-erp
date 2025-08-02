#!/bin/bash

echo "前端诊断脚本"
echo "=============="
echo ""

echo "1. 检查网络接口..."
ip addr show | grep inet | grep -v inet6
echo ""

echo "2. 检查防火墙状态..."
sudo ufw status
echo ""

echo "3. 检查3000端口监听状态..."
sudo ss -tlpn | grep 3000
echo ""

echo "4. 测试本地访问..."
curl -I http://localhost:3000
echo ""

echo "5. 测试0.0.0.0访问..."
curl -I http://0.0.0.0:3000
echo ""

echo "6. 测试公网IP访问（从本地）..."
curl -I http://18.219.25.24:3000
echo ""

echo "7. 检查iptables规则..."
sudo iptables -L -n | grep 3000
echo ""

echo "8. 检查AWS安全组提醒..."
echo "请确保在AWS EC2控制台的安全组中已经开放了3000端口的入站规则"
echo ""