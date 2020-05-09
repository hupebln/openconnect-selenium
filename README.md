# openconnect-selenium
## Description
I wrote openconnect-selenium as our company is using Pulse Secure on Windows and Mac to connect to VPN.  
On Linux there exists also a Pulse Secure client, but for the ones who love opensource software openconnect is probably the better choice.

The problem we face is SAML authentication with openconnect, as it cannot handle it. And here is where openconnect-selenium comes into the game.  
The idea is to outsource the authentication to a webbrowser and get the cookie and pass is to openconnect.

## Installation
You can install it by executing the following on the command line.
```shell script
pip3 install -U https://github.com/hupebln/openconnect-selenium --user
```

## Command-Line options
You have two possibilities, you can either define a hostname and it will build the url out of the provided information or
you define the URL you want to connect to.

Examples for `host` are:
```shell script
openconnect-selenium host example.com -po 123 -pr https

openconnect-selenium host example.com
```

An example for `url` is:
```shell script
openconnect-selenium url https://example.com:123
```

## Help
### General
```
usage: openconnect-selenium [-h] [-c COOKIE] [-v] {host,url} ...

Get Cookie from the session and pass to openconnect.

positional arguments:
  {host,url}
    host                use "host" if the endpoint is hosted at the root of
                        the address
    url                 use "url" if you want to use a specific url (helps if
                        the endpoint is hosted at a sub-path)

optional arguments:
  -h, --help            show this help message and exit
  -c COOKIE, --cookie COOKIE
                        name of the cookie to fetch - defaults to DSID
  -v, --verbose         -v loglevel INFO, -vv loglevel DEBUG
```

## CMD host
```
usage: openconnect-selenium host [-h] [-pr PROTO] [-po PORT] host

positional arguments:
  host                  The host which serves the VPN.

optional arguments:
  -h, --help            show this help message and exit
  -pr PROTO, --proto PROTO
                        either http or https -- defaults to https
  -po PORT, --port PORT
                        the port to be used -- defaults to 443

```

## CMD url
```
usage: openconnect-selenium url [-h] url

positional arguments:
  url         The URL-Endpoint which serves the landing page.

optional arguments:
  -h, --help  show this help message and exit

```

## Cookie-Name
As the company I work for is using Pulse Secure, it will search for a cookie called `DSID` by default, but you can change
this behavior by adding `-c <cooke-name>` to the command.