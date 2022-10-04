import json
from flask import request, _request_ctx_stack,abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'felix-njema.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'felix-njema'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():

    authorization_header = request.headers.get("Authorization", None)

    if not authorization_header:
        raise AuthError({"code": "authorization_header_missing",
                         "description":"Authorization header was not provided"
                         }, 401)

    
    authorization_header_parts = authorization_header.split()

    if len(authorization_header_parts) != 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'please provide authorization header in right format'

        },401)

        

    elif authorization_header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'please provide a bear token authorization header'

        },401)

    authorization_token = authorization_header_parts[1]

    return authorization_token       

   #raise Exception('Not Implemented')

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):

    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not found in jwt payload.'
        }, 400)
    
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'permission not included in jwt payload'

        }, 403)

    return True
    #raise Exception('Not Implemented')

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
#def verify_decode_jwt(token):
def get_key_to_decode_jwt(token):
    try:

        jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        if 'kid' not in unverified_header:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'key missing from authorization header.'
            }, 401)

        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }

        if not rsa_key:
            raise AuthError({
                'code': 'invalid_key',
                'description': 'an appropriate rsa key was not provided'
            }, 401)
        return rsa_key
    except Exception:
    
        raise AuthError({
                'code': 'invalid_header',
                'description': 'header could not be verified'
            }, 401)

def verify_decode_jwt(token):
    rsa_key = get_key_to_decode_jwt(token)

    
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer='https://' + AUTH0_DOMAIN + '/'
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise AuthError({
            'code': 'token_expired',
            'description': 'the provided Token has expired.'
        }, 401)

    except jwt.JWTClaimsError:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'please provide valid claims'
        }, 401)
    except Exception:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'token could not be authenticated'
        }, 400)


    #raise Exception('Not Implemented')

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()

            payload = verify_decode_jwt(token)

            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator