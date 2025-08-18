#!/bin/bash

# Script to populate secrets.toml from 1Password CLI
# Usage: ./setup_secrets.sh

set -e

echo "Setting up secrets from 1Password..."

# Ensure 1Password CLI is signed in
if ! op account list &>/dev/null; then
    echo "Please sign in to 1Password CLI first:"
    echo "eval \$(op signin)"
    exit 1
fi

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Fetch secrets from 1Password and create secrets.toml
cat > .streamlit/secrets.toml << EOF
# ChronoLog Application Secrets
# Generated from 1Password CLI on $(date)

[auth0]
domain = "$(op item get "Auth0 - ChronoLog" --vault "Private" --field "domain")"
client_id = "$(op item get "Auth0 - ChronoLog" --vault "Private" --field "client_id")"
client_secret = "$(op item get "Auth0 - ChronoLog" --vault "Private" --field "client_secret")"
redirect_uri = "http://localhost:8501"
mapping_redirect_uri="http://localhost:8502"

[supabase]
url = "$(op item get "Supabase - ChronoLog 1" --vault "Private" --field "url")"
key = "$(op item get "Supabase - ChronoLog 1" --vault "Private" --field "service_role secret")"
# service_role_key = "$(op item get "Supabase - ChronoLog 1" --vault "Private" --field "service_role secret")"
bucket = "uploads"
EOF

echo "✅ secrets.toml created successfully!"
echo "🔒 File contains sensitive data - ensure it's in .gitignore"

# Verify .gitignore excludes secrets.toml
if ! grep -q "secrets.toml" .gitignore 2>/dev/null; then
    echo "⚠️  Adding secrets.toml to .gitignore"
    echo ".streamlit/secrets.toml" >> .gitignore
fi

echo "🚀 Ready to run: streamlit run ChronoLog.py"
