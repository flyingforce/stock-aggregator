import click
import webbrowser
import requests
from urllib.parse import urlencode, unquote
import json
import base64
import logging

logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Stock Portfolio Aggregator CLI"""
    pass

@cli.command()
def get_schwab_token():
    """Get a Schwab access token using OAuth 2.0"""
    # Get credentials from user
    client_id = click.prompt('Enter your Schwab Client ID', default='6yk6qZxIfkBKGa1yOTJWsq5JcAOkAvZV')
    # client_id = click.prompt('Enter your Schwab Client ID', default='1wzwOrhivb2PkR1UCAUVTKYqC4MTNYlj')
    client_secret = click.prompt('Enter your Schwab Client Secret', hide_input=True)
    callback_url = click.prompt('Enter your callback URL', default='https://127.0.0.1:5003')
    
    try:
        # Step 1: Construct authorization URL
        auth_url = "https://api.schwabapi.com/v1/oauth/authorize"

        params = {
            "client_id": client_id,
            "redirect_uri": callback_url,
            "response_type": "code",
            # "scope": "readonly"
        }
        auth_url = f"{auth_url}?{urlencode(params)}"
        
        # Step 2: Open browser for user authorization
        click.echo("\nOpening browser for authorization...")
        click.echo(f"Please visit: {auth_url}")
        webbrowser.open(auth_url)
        
        # Step 3: Get authorization code from user and URL decode it
        returned_url = click.prompt("\nEnter the URL contains authorization code")
        # decoded_auth_code = unquote(auth_code)

        auth_code = f"{returned_url[returned_url.index('code=') + 5: returned_url.index('%40')]}@"

        print(auth_code)
        
        # Step 4: Exchange authorization code for tokens
        token_url = "https://api.schwabapi.com/v1/oauth/token"
        
        # Create Basic Auth header
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        
        # Prepare token request with URL decoded auth code
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": callback_url
        }
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Make token request
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        tokens = response.json()
        
        # Save tokens to file
        token_path = 'schwab_token.json'
        with open(token_path, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        # Display token information
        click.echo("\nAuthentication successful!")
        click.echo(f"Tokens have been saved to {token_path}")
        click.echo("\nToken Information:")
        click.echo(f"Access Token: {tokens.get('access_token')}")
        click.echo(f"Refresh Token: {tokens.get('refresh_token')}")
        click.echo(f"Expires in: {tokens.get('expires_in')} seconds")
        click.echo(f"Token Type: {tokens.get('token_type')}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during authentication: {str(e)}")
        click.echo(f"Error during authentication: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        click.echo(f"Unexpected error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    cli() 