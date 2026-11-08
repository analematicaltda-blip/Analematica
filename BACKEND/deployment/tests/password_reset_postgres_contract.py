"""One-use reset contract against the explicitly isolated PostgreSQL fixture."""
import os,secrets,uuid
_BARRIER=None

def attempt(payload):
    from django.db import connections
    from apps.prestadores.mi_negocio.web_password_reset import confirm_reset
    try:
        connections.close_all();_BARRIER.wait(timeout=10)
        return {'accepted':confirm_reset(payload['uid'],payload['token'],payload['password']),'pid':os.getpid()}
    finally:connections.close_all()


def run(context):
    from concurrent.futures import ProcessPoolExecutor
    from django.db import connections
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from api.models import CustomUser
    from allauth.account.models import EmailAddress
    from allauth.mfa.totp.internal.auth import TOTP,generate_totp_secret
    from apps.turismo.models import ErpSecurityEvent
    from apps.prestadores.mi_negocio.web_password_reset import TOKENS
    user=CustomUser(username='reset-'+uuid.uuid4().hex,email=uuid.uuid4().hex+'@example.test',is_active=True)
    user.set_password(secrets.token_urlsafe(24));CustomUser.objects.bulk_create([user])
    EmailAddress.objects.create(user=user,email=user.email,verified=True,primary=True)
    factor=TOTP.activate(user,generate_totp_secret()).instance;factor_data=factor.data.copy()
    uid=urlsafe_base64_encode(force_bytes(user.pk));token=TOKENS.make_token(user)
    passwords=[secrets.token_urlsafe(24) for _ in (0,1)]
    global _BARRIER
    _BARRIER=context.Barrier(2);connections.close_all()
    with ProcessPoolExecutor(max_workers=2,mp_context=context) as pool:
        futures=[pool.submit(attempt,{'uid':uid,'token':token,'password':password}) for password in passwords]
        results=[future.result(timeout=20) for future in futures]
    assert len({result['pid'] for result in results})==2
    assert sum(result['accepted'] for result in results)==1
    winner=next(index for index,result in enumerate(results) if result['accepted'])
    user.refresh_from_db();factor.refresh_from_db()
    assert user.check_password(passwords[winner]) and factor.data==factor_data
    assert ErpSecurityEvent.objects.filter(actor_id=user.pk,kind='password_reset').count()==1
    assert not TOKENS.check_token(user,token)
    return {'scenario':'same_link_two_processes','accepted':1,'rejected':1,'audit_events':1,'mfa_preserved':True}
