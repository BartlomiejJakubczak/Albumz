def test_check_auth_user_signal(auth_user):
    from albumz_app.domain.models import User as DomainUser

    assert DomainUser.objects.filter(auth_user=auth_user).exists()
