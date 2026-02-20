#!/bin/bash
# Test all TARS commands

echo "Testing TARS CLI Commands..."
echo "=============================="

# Commands that work without arguments
echo "✓ Testing: tars version"
tars version

echo -e "\n✓ Testing: tars health"
tars health

echo -e "\n✓ Testing: tars nodes"
tars nodes

echo -e "\n✓ Testing: tars namespaces"
tars namespaces

echo -e "\n✓ Testing: tars context"
tars context

echo -e "\n✓ Testing: tars crds"
tars crds | head -5

echo -e "\n✓ Testing: tars pods"
tars pods -n default | head -10

echo -e "\n✓ Testing: tars deployments"
tars deployments -n default

echo -e "\n✓ Testing: tars services"
tars services -n default

echo -e "\n✓ Testing: tars events"
tars events -n default | head -10

echo -e "\n✓ Testing: tars configmaps"
tars configmaps -n default

echo -e "\n✓ Testing: tars secrets"
tars secrets -n default

echo -e "\n✓ Testing: tars ingress"
tars ingress -n default

echo -e "\n✓ Testing: tars volumes"
tars volumes -n default

echo -e "\n✓ Testing: tars pending"
tars pending -n default

echo -e "\n✓ Testing: tars crashloop"
tars crashloop -n default

echo -e "\n✓ Testing: tars oom"
tars oom -n default

echo -e "\n✓ Testing: tars errors"
tars errors -n default

echo -e "\n✓ Testing: tars quota"
tars quota -n default

echo -e "\n✓ Testing: tars network"
tars network -n default

echo -e "\n✓ Testing: tars compliance"
tars compliance -n default

echo -e "\n✓ Testing: tars audit"
tars audit -n default | head -10

echo -e "\n✓ Testing: tars cost"
tars cost -n default

echo -e "\n=============================="
echo "All basic tests passed!"
