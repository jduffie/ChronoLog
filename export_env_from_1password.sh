#!/bin/bash

# Script to export environment variables from 1Password CLI
# This creates environment variables that correspond to the .streamlit/secrets.toml structure
# Usage: source ./export_env_from_1password.sh

set -e

echo "🔐 Exporting environment variables from 1Password..."

# Ensure 1Password CLI is signed in
if ! op account list &>/dev/null; then
    echo "❌ Please sign in to 1Password CLI first:"
    echo "eval \$(op signin)"
    return 1 2>/dev/null || exit 1
fi

# Export Auth0 environment variables
echo "📋 Exporting Auth0 credentials..."
export AUTH0_DOMAIN=$(op item get "Auth0 - ChronoLog" --vault "Private" --field "domain")
export AUTH0_CLIENT_ID=$(op item get "Auth0 - ChronoLog" --vault "Private" --field "client_id")
export AUTH0_CLIENT_SECRET=$(op item get "Auth0 - ChronoLog" --vault "Private" --field "client_secret")
export AUTH0_REDIRECT_URI="http://localhost:8501"
export AUTH0_MAPPING_REDIRECT_URI="http://localhost:8502"

# Export Supabase environment variables
echo "🗄️  Exporting Supabase credentials..."
export SUPABASE_URL=$(op item get "Supabase - ChronoLog 1" --vault "Private" --field "url")
export SUPABASE_KEY=$(op item get "Supabase - ChronoLog 1" --vault "Private" --field "service_role secret")
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog 1" --vault "Private" --field "service_role secret")
export SUPABASE_BUCKET="uploads"

echo "✅ Environment variables exported successfully!"
echo ""
echo "📝 Available environment variables:"
echo "   AUTH0_DOMAIN=$AUTH0_DOMAIN"
echo "   AUTH0_CLIENT_ID=$AUTH0_CLIENT_ID"
echo "   AUTH0_CLIENT_SECRET=***hidden***"
echo "   AUTH0_REDIRECT_URI=$AUTH0_REDIRECT_URI"
echo "   AUTH0_MAPPING_REDIRECT_URI=$AUTH0_MAPPING_REDIRECT_URI"
echo "   SUPABASE_URL=$SUPABASE_URL"
echo "   SUPABASE_KEY=***hidden***"
echo "   SUPABASE_SERVICE_ROLE_KEY=***hidden***"
echo "   SUPABASE_BUCKET=$SUPABASE_BUCKET"
echo ""
echo "🚀 You can now run the application with environment variables:"
echo "   streamlit run ChronoLog.py"
echo ""
echo "💡 To verify Supabase connection:"
echo "   python verify_supabase.py"