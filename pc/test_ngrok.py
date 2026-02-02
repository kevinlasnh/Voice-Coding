import os
import sys

# Save and clear proxy environment variables
old_http_proxy = os.environ.pop('http_proxy', None)
old_https_proxy = os.environ.pop('https_proxy', None)
old_HTTP_PROXY = os.environ.pop('HTTP_PROXY', None)
old_HTTPS_PROXY = os.environ.pop('HTTPS_PROXY', None)

print(f"Proxies cleared: http={old_http_proxy}, https={old_https_proxy}")

try:
    from pyngrok import ngrok

    print("Connecting to ngrok...")
    tunnel = ngrok.connect(9528, bind_tls=True)
    print(f"SUCCESS! Tunnel URL: {tunnel.public_url}")

    # Close the tunnel
    ngrok.disconnect(tunnel)
    print("Tunnel closed successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Restore proxy environment variables
    if old_http_proxy:
        os.environ['http_proxy'] = old_http_proxy
    if old_https_proxy:
        os.environ['https_proxy'] = old_https_proxy
    if old_HTTP_PROXY:
        os.environ['HTTP_PROXY'] = old_HTTP_PROXY
    if old_HTTPS_PROXY:
        os.environ['HTTPS_PROXY'] = old_HTTPS_PROXY
    print("Proxies restored")
