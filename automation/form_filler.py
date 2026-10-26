def fill_application(page, profile):

    # --- Stage 1: Personal Information ---

    # Core personal fields mapped to profile
    personal_fields = {
        "full_name": profile.full_name,
        "email": profile.email,
        "phone": profile.phone,
        "address": profile.address,
        "city": profile.city,
        "postcode": profile.postcode,
    }

    # Enhanced field filling with multiple selector strategies
    def fill_field(field_name, value, selectors_list):

        if not value:
            return False

        filled = False
        attempted_selectors = []

        for selector in selectors_list:
            attempted_selectors.append(selector)

            try:
                field = page.locator(selector).first

                if field.count() > 0:
                    current_value = field.input_value()
                    # Only fill if field is empty (avoid overwriting user input)
                    if current_value.strip() == "":
                        field.fill(value)
                        print(f"Filled: {field_name}")
                    filled = True
                    break
            except Exception:
                pass

        # If no selector worked, try a general name search
        if not filled:
            try:
                field = page.locator(f'input[name="{field_name}"]').first
                if field.count() > 0:
                    current_value = field.input_value()
                    if current_value.strip() == "":
                        field.fill(value)
                        print(f"Filled (broad): {field_name}")
                    filled = True
            except Exception:
                pass

        # If still not filled, try label-associated inputs
        if not filled:
            try:
                # Try finding input by label text
                label_selector = f'label:has-text("{field_name}")'
                field = page.locator(label_selector).first
                # The input associated with the label
                if field.count() > 0:
                    associated_input = field.locator('..').locator('input')
                    if associated_input.count() > 0:
                        current_value = associated_input.input_value()
                        if current_value.strip() == "":
                            associated_input.fill(value)
                            print(f"Filled (label-associated): {field_name}")
                        filled = True
            except Exception:
                pass

        return filled

    # Fill core personal fields
    for field_name, value in personal_fields.items():

        # Enhanced selector strategies for each field type
        base_selectors = [
            # Direct name/ID match
            f'input[name="{field_name}"]',
            f'input[id="{field_name}"]',
            # Label-associated selectors
            f'input[aria-labelledby*="{field_name}"]',
            # Placeholder matching
            f'input[placeholder*="{field_name}"]',
            # Generic type-based
            f'input[type="text"][name*="{field_name}"]',
            f'input[type="email"][name*="{field_name}"]',
        ]

        fill_field(field_name, value, base_selectors)


    # --- Stage 2: Contact and Identifier Fields ---

    # Additional contact identifiers
    identifier_fields = {
        "national_insurance": getattr(profile, 'national_insurance', None),
        "right_to_work": getattr(profile, 'right_to_work', None),
        "availability": getattr(profile, 'availability_date', None),
    }

    # NI number format: AB 12 34 56 C (UK pattern)
    ni_value = identifier_fields["national_insurance"]
    if ni_value:
        ni_selectors = [
            'input[name="national_insurance"]',
            'input[name="ni_number"]',
            'input[name="nino"]',
            'input[id="national_insurance"]',
            'input[id="ni_number"]',
        ]
        fill_field("national_insurance", ni_value, ni_selectors)

    # Right to work select or checkbox
    rtw_value = identifier_fields["right_to_work"]
    if rtw_value:
        rtw_selectors = [
            f'select[name="right_to_work"]',
            f'input[name="right_to_work"][value="{rtw_value}"]',
            f'input[id="right_to_work"]',
        ]
        # Try select first, then checkbox
        for selector in rtw_selectors:
            try:
                field = page.locator(selector).first
                if field.count() > 0:
                    # Handle select elements
                    input_type = field.evaluate("""el => el.tagName""")
                    if 'SELECT' in input_type:
                        field.select_label(rtw_value)
                    else:
                        field.fill(rtw_value)
                    print(f"Filled: right_to_work")
                    break
            except Exception:
                pass

    # Availability date
    avail_value = identifier_fields["availability"]
    if avail_value:
        avail_selectors = [
            'input[name="availability"]',
            'input[name="start_date"]',
            'input[id="availability"]',
        ]
        fill_field("availability", avail_value, avail_selectors)


    # --- Stage 3: Employment History and Education ---

    # Textarea fields from profile
    textarea_fields = {
        "skills": profile.skills,
        "experience": profile.experience,
        "education": profile.education,
    }

    for field_name, value in textarea_fields.items():

        if not value:
            continue

        selectors = [
            f'textarea[name="{field_name}"]',
            f'textarea[id="{field_name}"]',
            # Rich text editors
            f'div[contenteditable="true"]',
        ]

        filled = False
        for selector in selectors:

            try:
                field = page.locator(selector).first

                if field.count() > 0:
                    current_value = field.inner_text()
                    # For contenteditable divs, check if empty
                    if current_value.strip() == "":
                        field.fill(value)
                        print(f"Filled textarea: {field_name}")
                    filled = True
                    break
            except Exception:
                pass

        # Fallback: broad textarea search
        if not filled:
            try:
                field = page.locator('textarea').first
                if field.count() > 0:
                    current_value = field.input_value()
                    if current_value.strip() == "":
                        field.fill(value)
                        print(f"Filled (broad textarea): {field_name}")
                    filled = True
            except Exception:
                pass


    # --- Stage 4: Form Controls (Select, Radio, Checkbox) ---

    # Common employment type select
    job_type = getattr(profile, 'job_types', None)
    if job_type:
        job_type_selectors = [
            f'select[name="job_type"]',
            f'select[id="job_type"]',
            f' input[type="radio"][value="full-time"]',
            f' input[type="radio"][value="part-time"]',
        ]
        for selector in job_type_selectors:
            try:
                field = page.locator(selector).first
                if field.count() > 0:
                    input_type = field.evaluate("""el => el.tagName""")
                    if 'SELECT' in input_type:
                        # Map our values to common form values
                        job_map = {
                            "full-time": "full-time",
                            "part-time": "part-time",
                            "contract": "contract",
                            "apprenticeship": "apprenticeship",
                        }
                        mapped = job_map.get(job_type, job_type)
                        field.select_option(mapped)
                        print(f"Filled: job_type = {mapped}")
                    else:
                        field.fill(job_type)
                        print(f"Filled: job_type = {job_type}")
                    break
            except Exception:
                pass

    # Experience level select
    exp_level = getattr(profile, 'experience_level', None)
    if exp_level:
        exp_selectors = [
            f'select[name="experience_level"]',
            f'select[id="experience_level"]',
        ]
        for selector in exp_selectors:
            try:
                field = page.locator(selector).first
                if field.count() > 0:
                    field.select_option(exp_level)
                    print(f"Filled: experience_level = {exp_level}")
                    break
            except Exception:
                pass


    # --- Stage 5: CV Upload ---

    if profile.cv_path:

        try:

            cv_input = page.locator(
                'input[type="file"]'
            ).first

            if cv_input.count() > 0:

                cv_input.set_input_files(
                    profile.cv_path
                )

                print("CV uploaded successfully.")

        except Exception as e:

            print(
                f"CV upload failed: {e}"
            )