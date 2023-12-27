
from app.auth.jwt import JWTUserDataDependency
from app.products.constants import LicenseIds
from app.telegram.exceptions import NoLicense

from app.users import service as users_service


async def has_valid_license(jwt_user_data: JWTUserDataDependency):
    user_licenses = await users_service.get_user_licenses(jwt_user_data.user_id)

    has_license = False

    for user_license in user_licenses:
        if user_license["license_id"] == LicenseIds.TELEGRAM:
            has_license = True

            break

    if not has_license:
        raise NoLicense()
