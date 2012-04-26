Introduction
============

This package implements a widget that groups select values into optgroups.


Usage
=====

Imagine you have the following schema::


    class IMySchema(Interface):
        country = schema.Choice(
            required=True,
            title=u"Country",
            vocabulary='countries',
        )

        subdivision = schema.Choice(
            required=True,
            title=u"State",
            vocabulary='subdivisions',
        )

        region = schema.Choice(
            required=True,
            title=u"County",
            vocabulary='regions',
        )


When you create your vocabularies (e.g. using ``SimpleVocabulary``), instead of adding ``SimpleTerm`` items::

    ...
    for country in pycountry.countries:
        terms.append(SimpleTerm(value=country.alpha2, token=country.alpha2,
                                title=country.name))
    ...


you add ``OptgroupTerm`` items::

    from z3c.formwidget.optgroup.widget import OptgroupTerm

    ...
    country_list = countries(context)
    for item in pycountry.subdivisions:
        parent = country_list.getTermByToken(item.country_code).title
        terms.append(OptgroupTerm(value=item.code, token=item.code,
                                  title=item.name, optgroup=parent))
    ...



In your form, simply assign the ``OptgroupFieldWidget``::

    from z3c.formwidget.optgroup.widget import OptgroupFieldWidget

    class MyForm(form.Form):
        fields = field.Fields(IMySchema)

        fields['subdivision'].widgetFactory = OptgroupFieldWidget
        fields['region'].widgetFactory = OptgroupFieldWidget
