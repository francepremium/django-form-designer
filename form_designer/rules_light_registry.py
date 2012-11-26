import rules_light


rules_light.registry.setdefault('form_designer.form.create', True)
rules_light.registry.setdefault('form_designer.form.update',
    lambda user, rule, form: user == form.author)
