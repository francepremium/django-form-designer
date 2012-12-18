import rules_light


rules_light.registry.setdefault('form_designer.form.create', True)
rules_light.registry.setdefault('form_designer.form.update',
    rules_light.is_authenticated(
        lambda user, rule, form: user == form.author))
