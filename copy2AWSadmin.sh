#!/bin/bash
SERVER="admin@aandewiel.nl"
TARGET="/home/admin/flasherWebsite_v2"
SSH_KEY="$HOME/.ssh/LightsailDefaultKey-eu-central-1.pem"

echo "Deploying projects/ to $SERVER:$TARGET ..."
echo "📋 Syncing projects/ (add/update only, no deletion)..."
echo ""

#-- Sync projects/ directory WITHOUT --delete
#-- This will add new files and update existing ones, but never delete
/usr/bin/rsync -avz \
  -e "ssh -i $SSH_KEY" \
  --exclude '.DS_Store' \
  ~/Documents/platformioProjects/espMorseMachine/projects/ $SERVER:$TARGET/projects/

if [ $? -ne 0 ]; then
  echo "❌ Error: projects rsync failed"
  exit 1
fi

echo ""
echo "✅ Deployment complete!"
echo "📁 Synced projects: All subdirectories and files (add/update only)"
