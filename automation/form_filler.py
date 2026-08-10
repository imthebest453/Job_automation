def fill_application(page, profile):

    fields = {
        "full_name": profile.full_name,
        "email": profile.email,
        "phone": profile.phone,
        "address": profile.address,
        "city": profile.city,
        "postcode": profile.postcode,
    }

    for field_name, value in fields.items():

        if not value:
            continue

        selectors = [
            f'input[name="{field_name}"]',
            f'input[id="{field_name}"]',
            f'input[placeholder*="{field_name}" i]',
        ]

        for selector in selectors:

            try:
                field = page.locator(selector).first

                if field.count() > 0:
                    field.fill(value)
                    break

            except Exception:
                pass