# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""An optgroup widget for z3c.form."""

# zope imports
from z3c.form import converter, interfaces
from z3c.form.browser import widget
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter, getMultiAdapter
from zope.schema.interfaces import (IFromUnicode, ITextLine,
    ITitledTokenizedTerm, ITokenizedTerm)
from zope.i18n import translate
from zope.interface import implementer, implements
from zope.interface.declarations import directlyProvides

# local imports
from z3c.formwidget.optgroup.interfaces import IOptgroupWidget


class OptgroupTerm(object):
    """A SimpleTerm with an aditional attribute "optgroup".

    It's also a tokenized term used by SimpleVocabulary.
    """
    implements(ITokenizedTerm)

    def __init__(self, value, token=None, title=None, optgroup=None):
        """Create a term for value and token.

        If token is omitted, str(value) is used for the token. If title is
        provided, term implements ITitledTokenizedTerm.
        """
        self.optgroup = optgroup
        self.value = value
        if token is None:
            token = value
        self.token = str(token)
        self.title = title
        if title is not None:
            directlyProvides(self, ITitledTokenizedTerm)


class OptgroupWidget(SelectWidget):
    """Optgroup widget based on SelectWidget."""
    implements(IOptgroupWidget, IFromUnicode)

    klass = u'optgroup-widget'

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(OptgroupWidget, self).update()
        widget.addFieldClass(self)

    @property
    def items(self):
        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })
        unordered_items = {}
        optgroups = []
        for count, term in enumerate(self.terms):
            # Exctract optgroups in an ordered list, so we can use this to
            # preserve the main order of optgroups.
            if not term.optgroup in optgroups:
                optgroups.append(term.optgroup)
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, count)
            content = term.title
            if ITitledTokenizedTerm.providedBy(term):
                content = self.getContent(term)
            if not term.optgroup in unordered_items:
                unordered_items[term.optgroup] = []
            unordered_items[term.optgroup].append({
                'id': id,
                'value': term.token,
                'content': content,
                'selected': selected,
            })
        for group in optgroups:
            item = {}
            item['title'] = group
            item['member'] = unordered_items[group]
            items.append(item)
        self.getSize(items)
        return items

    def getSize(self, items):
        """Get a dynamic size for the widget."""
        if hasattr(self.field, 'max_length'):
            self.size = self.field.max_length
            return
        if not self.multiple:
            self.size = 1
            return
        amount = len(items)
        for optgroup in range(0, len(items)):
            amount = amount + len(items[optgroup]['member'])
        if amount <= 10:
            self.size = amount
        else:
            self.size = 10

    def displayValue(self):
        value = {}
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            term = self.terms.getTermByToken(token)
            if ITitledTokenizedTerm.providedBy(term):
                content = self.getContent(term)
            else:
                value.append(term.value)
            if not term.optgroup in value:
                value[term.optgroup] = []
            value[term.optgroup].append(content)
        return value

    def getContent(self, term):
        return translate(term.title, context=self.request, default=term.title)


@adapter(converter.FieldDataConverter)
@adapter(ITextLine, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def OptgroupFieldWidget(field, request):
    """Factory for OptgroupWidget."""
    widget = FieldWidget(field, OptgroupWidget(request))
    if hasattr(field, 'value_type'):
        widget.multiple = getMultiAdapter((field,
            field.value_type, request), interfaces.IFieldWidget).multiple
    else:
        widget.multiple = getMultiAdapter((field, request),
            interfaces.IFieldWidget).multiple
    return widget
