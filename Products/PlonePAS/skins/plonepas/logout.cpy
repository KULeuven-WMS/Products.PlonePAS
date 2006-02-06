## Script (Python) "logout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Logout handler
##parameters=

# CHANGES:
#  removed cookie crumbler expire
#  call PAS.logout
from Products.CMFCore.utils import getToolByName

try:
    context.acl_users.logout(context.REQUEST)
except:
    pass  # we expect Unauthorized

REQUEST = context.REQUEST

# if REQUEST.has_key('portal_skin'):
#   context.portal_skins.clearSkinCookie()

skinvar = context.portal_skins.getRequestVarname()
path = '/' + context.absolute_url(1)

if REQUEST.has_key(skinvar) and not context.portal_skins.getCookiePersistence():
    REQUEST.RESPONSE.expireCookie(skinvar, path=path)

#cookie_auth=getattr(context, 'cookie_authentication')
#if cookie_auth is not None:
#    cookie_name=cookie_auth.getProperty('auth_cookie')
#    REQUEST.RESPONSE.expireCookie(cookie_name, path='/')

sdm = getToolByName(context, 'session_data_manager', None)
if sdm is not None:
    session = sdm.getSessionData(create=0)
    if session is not None:
        session.invalidate()
from Products.CMFPlone import transaction_note
transaction_note('Logged out')

# If you want to do a traverse next, instead of a redirect, you need to
# kill the current security context.  Keep in mind that this may mean
# that you end up on a logged_out page with a context that you can't view...
# context.portal_membership.immediateLogout()

return state.set(next_action='redirect_to:string:'+REQUEST.URL1.replace('$','$$')+'/logged_out')