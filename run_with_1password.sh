#!/bin/bash

# Script to run ChronoLog with 1Password-sourced environment variables
# Usage: ./run_with_1password.sh

set -e

echo "🔐 Loading secrets from 1Password..."

# Ensure 1Password CLI is signed in
if ! op account list &>/dev/null; then
    echo "Please sign in to 1Password CLI first:"
    echo "eval \$(op signin)"
    exit 1
fi

# Export environment variables from 1Password
export AUTH0_DOMAIN=$(op item get "Auth0 - ChronoLog" --vault "Private" --field "domain")
export AUTH0_CLIENT_ID=$(op item get "Auth0 - ChronoLog" --vault "Private" --field "client_id")
export AUTH0_CLIENT_SECRET=$(op item get "Auth0 - ChronoLog" --vault "Private" --field "client_secret")
export AUTH0_REDIRECT_URI=$(op item get "Auth0 - ChronoLog" --vault "Private" --field "redirect_uri")

export SUPABASE_URL=$(op item get "Supabase - ChronoLog" --vault "Private" --field "url")
export SUPABASE_ANON_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --field "anon_key")
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --field "service_role secret")

echo "✅ Environment variables loaded"

# Activate virtual environment and run Streamlit
echo "🚀 Starting ChronoLog..."
source venv/bin/activate
streamlit run ChronoLog.py